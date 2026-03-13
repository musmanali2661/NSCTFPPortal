from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_staff
from app.database import get_db
from app.models import Staff, SupportTicket, TicketStatusEnum
from app.schemas import TicketCreate, TicketOut, TicketUpdate
from app.services.ai_service import generate_auto_reply, recognize_intent

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.get("", response_model=List[TicketOut])
async def list_tickets(
    status: Optional[TicketStatusEnum] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    _: Staff = Depends(get_current_staff),
):
    query = select(SupportTicket)
    if status is not None:
        query = query.where(SupportTicket.status == status)
    query = query.order_by(SupportTicket.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("", response_model=TicketOut, status_code=status.HTTP_201_CREATED)
async def create_ticket(
    body: TicketCreate,
    db: AsyncSession = Depends(get_db),
):
    ticket = SupportTicket(**body.model_dump())
    db.add(ticket)
    await db.flush()
    await db.refresh(ticket)
    return ticket


@router.put("/{ticket_id}", response_model=TicketOut)
async def update_ticket(
    ticket_id: int,
    body: TicketUpdate,
    db: AsyncSession = Depends(get_db),
    _: Staff = Depends(get_current_staff),
):
    result = await db.execute(select(SupportTicket).where(SupportTicket.id == ticket_id))
    ticket = result.scalar_one_or_none()
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(ticket, field, value)
    await db.flush()
    await db.refresh(ticket)
    return ticket


@router.post("/{ticket_id}/ai-reply", response_model=TicketOut)
async def generate_ai_reply(
    ticket_id: int,
    db: AsyncSession = Depends(get_db),
    _: Staff = Depends(get_current_staff),
):
    result = await db.execute(select(SupportTicket).where(SupportTicket.id == ticket_id))
    ticket = result.scalar_one_or_none()
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

    category = recognize_intent(ticket.original_query)
    reply = generate_auto_reply(ticket.original_query, category)
    ticket.ai_suggested_reply = reply
    await db.flush()
    await db.refresh(ticket)
    return ticket
