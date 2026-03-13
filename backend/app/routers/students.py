from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_staff
from app.database import get_db
from app.models import DataDiscrepancy, Staff, Student, StudentStatusEnum
from app.schemas import (
    StudentCreate, StudentListOut, StudentOut, StudentUpdate,
)
from app.services.validator import run_validator

router = APIRouter(prefix="/students", tags=["students"])


@router.get("", response_model=StudentListOut)
async def list_students(
    department_id: Optional[int] = Query(None),
    status: Optional[StudentStatusEnum] = Query(None),
    batch_type: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    _: Staff = Depends(get_current_staff),
):
    query = select(Student)
    if department_id is not None:
        query = query.where(Student.department_id == department_id)
    if status is not None:
        query = query.where(Student.status == status)
    if batch_type is not None:
        query = query.where(Student.batch_type == batch_type)
    if search:
        pattern = f"%{search}%"
        query = query.where(
            or_(
                Student.full_name.ilike(pattern),
                Student.reg_no.ilike(pattern),
                Student.cnic.ilike(pattern),
                Student.email.ilike(pattern),
            )
        )

    count_query = select(func.count(Student.id))
    if department_id is not None:
        count_query = count_query.where(Student.department_id == department_id)
    if status is not None:
        count_query = count_query.where(Student.status == status)
    if batch_type is not None:
        count_query = count_query.where(Student.batch_type == batch_type)
    if search:
        pattern = f"%{search}%"
        search_clause = or_(
            Student.full_name.ilike(pattern),
            Student.reg_no.ilike(pattern),
            Student.cnic.ilike(pattern),
            Student.email.ilike(pattern),
        )
        count_query = count_query.where(search_clause)

    count_result = await db.execute(count_query)
    total: int = count_result.scalar_one()

    paged_result = await db.execute(query.order_by(Student.created_at.desc()).offset(skip).limit(limit))
    paged = paged_result.scalars().all()
    return StudentListOut(total=total, items=paged)


@router.get("/{student_id}", response_model=StudentOut)
async def get_student(
    student_id: int,
    db: AsyncSession = Depends(get_db),
    _: Staff = Depends(get_current_staff),
):
    result = await db.execute(select(Student).where(Student.id == student_id))
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    return student


@router.post("", response_model=StudentOut, status_code=status.HTTP_201_CREATED)
async def create_student(
    body: StudentCreate,
    db: AsyncSession = Depends(get_db),
    _: Staff = Depends(get_current_staff),
):
    existing = await db.execute(
        select(Student).where(
            or_(Student.reg_no == body.reg_no, Student.cnic == body.cnic)
        )
    )
    conflict = existing.scalar_one_or_none()
    if conflict:
        field = "reg_no" if conflict.reg_no == body.reg_no else "cnic"
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Student with {field}='{getattr(body, field)}' already exists",
        )
    student = Student(**body.model_dump())
    db.add(student)
    await db.flush()
    await db.refresh(student)
    await run_validator(db, student_ids=[student.id])
    return student


@router.put("/{student_id}", response_model=StudentOut)
async def update_student(
    student_id: int,
    body: StudentUpdate,
    db: AsyncSession = Depends(get_db),
    _: Staff = Depends(get_current_staff),
):
    result = await db.execute(select(Student).where(Student.id == student_id))
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(student, field, value)
    await db.flush()
    await db.refresh(student)
    await run_validator(db, student_ids=[student_id])
    return student


@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_student(
    student_id: int,
    db: AsyncSession = Depends(get_db),
    _: Staff = Depends(get_current_staff),
):
    result = await db.execute(select(Student).where(Student.id == student_id))
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    await db.delete(student)


@router.post("/{student_id}/resolve-discrepancies", status_code=status.HTTP_200_OK)
async def resolve_all_discrepancies(
    student_id: int,
    db: AsyncSession = Depends(get_db),
    _: Staff = Depends(get_current_staff),
):
    result = await db.execute(select(Student).where(Student.id == student_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")

    disc_result = await db.execute(
        select(DataDiscrepancy).where(
            DataDiscrepancy.student_id == student_id,
            DataDiscrepancy.is_resolved == False,  # noqa: E712
        )
    )
    discrepancies = disc_result.scalars().all()
    for d in discrepancies:
        d.is_resolved = True
    await db.flush()
    return {"resolved": len(discrepancies)}
