from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_staff
from app.database import get_db
from app.models import DataDiscrepancy, SeverityEnum, Staff
from app.schemas import DiscrepancyOut

router = APIRouter(prefix="/discrepancies", tags=["discrepancies"])


@router.get("", response_model=List[DiscrepancyOut])
async def list_discrepancies(
    is_resolved: Optional[bool] = Query(None),
    severity: Optional[SeverityEnum] = Query(None),
    student_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    _: Staff = Depends(get_current_staff),
):
    query = select(DataDiscrepancy)
    if is_resolved is not None:
        query = query.where(DataDiscrepancy.is_resolved == is_resolved)
    if severity is not None:
        query = query.where(DataDiscrepancy.severity == severity)
    if student_id is not None:
        query = query.where(DataDiscrepancy.student_id == student_id)
    query = query.order_by(DataDiscrepancy.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.put("/{disc_id}/resolve", response_model=DiscrepancyOut)
async def resolve_discrepancy(
    disc_id: int,
    db: AsyncSession = Depends(get_db),
    _: Staff = Depends(get_current_staff),
):
    result = await db.execute(select(DataDiscrepancy).where(DataDiscrepancy.id == disc_id))
    disc = result.scalar_one_or_none()
    if not disc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Discrepancy not found")
    disc.is_resolved = True
    await db.flush()
    await db.refresh(disc)
    return disc
