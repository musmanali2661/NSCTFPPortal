from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_staff, hash_password
from app.database import get_db
from app.models import Staff
from app.schemas import StaffCreate, StaffOut, StaffUpdate

router = APIRouter(prefix="/staff", tags=["staff"])


@router.get("", response_model=List[StaffOut])
async def list_staff(
    db: AsyncSession = Depends(get_db),
    _: Staff = Depends(get_current_staff),
):
    result = await db.execute(select(Staff).order_by(Staff.name))
    return result.scalars().all()


@router.post("", response_model=StaffOut, status_code=status.HTTP_201_CREATED)
async def create_staff(
    body: StaffCreate,
    db: AsyncSession = Depends(get_db),
    current: Staff = Depends(get_current_staff),
):
    from app.models import RoleEnum
    if current.role != RoleEnum.Admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")

    existing = await db.execute(select(Staff).where(Staff.email == body.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    data = body.model_dump()
    password = data.pop("password")
    staff = Staff(**data, hashed_password=hash_password(password))
    db.add(staff)
    await db.flush()
    await db.refresh(staff)
    return staff


@router.put("/{staff_id}", response_model=StaffOut)
async def update_staff(
    staff_id: int,
    body: StaffUpdate,
    db: AsyncSession = Depends(get_db),
    current: Staff = Depends(get_current_staff),
):
    from app.models import RoleEnum
    if current.role != RoleEnum.Admin and current.id != staff_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    result = await db.execute(select(Staff).where(Staff.id == staff_id))
    staff = result.scalar_one_or_none()
    if not staff:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Staff not found")

    update_data = body.model_dump(exclude_none=True)
    if "password" in update_data:
        update_data["hashed_password"] = hash_password(update_data.pop("password"))

    for field, value in update_data.items():
        setattr(staff, field, value)

    await db.flush()
    await db.refresh(staff)
    return staff
