from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_staff
from app.database import get_db
from app.models import QuestionBank, ReviewStatusEnum, Staff
from app.schemas import QuestionCreate, QuestionOut, QuestionUpdate

router = APIRouter(prefix="/question-bank", tags=["question-bank"])


@router.get("", response_model=List[QuestionOut])
async def list_questions(
    subject_area: Optional[str] = Query(None),
    teacher_id: Optional[int] = Query(None),
    review_status: Optional[ReviewStatusEnum] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    _: Staff = Depends(get_current_staff),
):
    query = select(QuestionBank)
    if subject_area:
        query = query.where(QuestionBank.subject_area.ilike(f"%{subject_area}%"))
    if teacher_id:
        query = query.where(QuestionBank.teacher_id == teacher_id)
    if review_status:
        query = query.where(QuestionBank.review_status == review_status)
    query = query.order_by(QuestionBank.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("", response_model=QuestionOut, status_code=status.HTTP_201_CREATED)
async def create_question(
    body: QuestionCreate,
    db: AsyncSession = Depends(get_db),
    _: Staff = Depends(get_current_staff),
):
    question = QuestionBank(**body.model_dump())
    db.add(question)
    await db.flush()
    await db.refresh(question)
    return question


@router.put("/{question_id}", response_model=QuestionOut)
async def update_question(
    question_id: int,
    body: QuestionUpdate,
    db: AsyncSession = Depends(get_db),
    _: Staff = Depends(get_current_staff),
):
    result = await db.execute(select(QuestionBank).where(QuestionBank.id == question_id))
    question = result.scalar_one_or_none()
    if not question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(question, field, value)
    await db.flush()
    await db.refresh(question)
    return question
