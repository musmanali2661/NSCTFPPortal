import io
import re
from datetime import date, datetime
from typing import Any, Dict, List, Optional

import pandas as pd
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_staff
from app.database import get_db
from app.models import (
    BatchTypeEnum, Department, GenderEnum, Staff, Student, StudentStatusEnum,
)
from app.schemas import UploadResult
from app.services.validator import run_validator

router = APIRouter(prefix="/uploads", tags=["uploads"])

# Mapping of common CSV column name variations -> model field names
COLUMN_MAP: Dict[str, str] = {
    # reg_no
    "reg_no": "reg_no",
    "regno": "reg_no",
    "registration_no": "reg_no",
    "registration no": "reg_no",
    "reg no": "reg_no",
    "student_id": "reg_no",
    # full_name
    "full_name": "full_name",
    "fullname": "full_name",
    "name": "full_name",
    "student_name": "full_name",
    "student name": "full_name",
    # father_name
    "father_name": "father_name",
    "fathername": "father_name",
    "father name": "father_name",
    "father": "father_name",
    # cnic
    "cnic": "cnic",
    "nic": "cnic",
    "national_id": "cnic",
    # dob
    "dob": "dob",
    "date_of_birth": "dob",
    "date of birth": "dob",
    "birth_date": "dob",
    # gender
    "gender": "gender",
    "sex": "gender",
    # email
    "email": "email",
    "email_address": "email",
    "email address": "email",
    # mobile_number
    "mobile_number": "mobile_number",
    "mobile": "mobile_number",
    "phone": "mobile_number",
    "contact": "mobile_number",
    "contact_no": "mobile_number",
    "phone_number": "mobile_number",
    # department_id
    "department_id": "department_id",
    "dept_id": "department_id",
    "department": "department_name",  # will be resolved to id
    "dept": "department_name",
    # batch_type
    "batch_type": "batch_type",
    "batch": "batch_type",
    "shift": "batch_type",
    # semester_no
    "semester_no": "semester_no",
    "semester": "semester_no",
    "sem": "semester_no",
    # gpa
    "gpa": "gpa",
    "semester_gpa": "gpa",
    # cgpa
    "cgpa": "cgpa",
    "cumulative_gpa": "cgpa",
    # transport_required
    "transport_required": "transport_required",
    "transport": "transport_required",
    "needs_transport": "transport_required",
}

GENDER_MAP: Dict[str, GenderEnum] = {
    "m": GenderEnum.Male, "male": GenderEnum.Male,
    "f": GenderEnum.Female, "female": GenderEnum.Female,
    "o": GenderEnum.Other, "other": GenderEnum.Other,
}

BATCH_MAP: Dict[str, BatchTypeEnum] = {
    "morning": BatchTypeEnum.Morning,
    "evening": BatchTypeEnum.Evening,
    "lateral": BatchTypeEnum.Lateral,
}

CSV_TEMPLATE_COLUMNS = [
    "reg_no", "full_name", "father_name", "cnic", "dob", "gender",
    "email", "mobile_number", "department_id", "batch_type", "semester_no",
    "gpa", "cgpa", "transport_required",
]


def _normalize_column(col: str) -> str:
    return col.strip().lower().replace(" ", "_")


def _parse_date(val: Any) -> Optional[date]:
    if pd.isna(val) or val is None or str(val).strip() == "":
        return None
    if isinstance(val, (datetime, pd.Timestamp)):
        return val.date()
    if isinstance(val, date):
        return val
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%m/%d/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(str(val).strip(), fmt).date()
        except ValueError:
            continue
    return None


def _parse_bool(val: Any) -> bool:
    if isinstance(val, bool):
        return val
    if pd.isna(val):
        return False
    s = str(val).strip().lower()
    return s in ("1", "true", "yes", "y")


def _parse_float(val: Any) -> Optional[float]:
    try:
        if pd.isna(val):
            return None
    except TypeError:
        pass
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def _parse_int(val: Any) -> Optional[int]:
    try:
        if pd.isna(val):
            return None
    except TypeError:
        pass
    try:
        return int(float(val))
    except (ValueError, TypeError):
        return None


async def _load_dataframe(file: UploadFile) -> pd.DataFrame:
    content = await file.read()
    filename = (file.filename or "").lower()
    if filename.endswith(".xlsx") or filename.endswith(".xls"):
        return pd.read_excel(io.BytesIO(content))
    elif filename.endswith(".csv"):
        return pd.read_csv(io.BytesIO(content))
    else:
        # Try CSV first, then Excel
        try:
            return pd.read_csv(io.BytesIO(content))
        except Exception:
            return pd.read_excel(io.BytesIO(content))


@router.post("/csv", response_model=UploadResult)
async def bulk_upload(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    _: Staff = Depends(get_current_staff),
):
    try:
        df = await _load_dataframe(file)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Could not parse file: {exc}",
        )

    if df.empty:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="File is empty")

    # Normalize column names
    df.columns = [_normalize_column(c) for c in df.columns]
    df.rename(columns={c: COLUMN_MAP[c] for c in df.columns if c in COLUMN_MAP}, inplace=True)

    # Load departments for name -> id resolution
    dept_result = await db.execute(select(Department))
    departments = dept_result.scalars().all()
    dept_name_to_id: Dict[str, int] = {d.name.lower(): d.id for d in departments}
    dept_id_set = {d.id for d in departments}

    created = updated = skipped = 0
    errors: List[str] = []
    new_student_ids: List[int] = []

    for idx, row in df.iterrows():
        row_num = idx + 2  # 1-indexed + header row
        row_errors: List[str] = []

        # Required field: reg_no
        reg_no = str(row.get("reg_no", "")).strip()
        if not reg_no:
            errors.append(f"Row {row_num}: missing reg_no")
            skipped += 1
            continue

        # Resolve department
        dept_id: Optional[int] = None
        if "department_id" in row and not pd.isna(row["department_id"]):
            try:
                dept_id = int(float(row["department_id"]))
            except (ValueError, TypeError):
                pass
        if dept_id is None and "department_name" in row:
            dept_name = str(row["department_name"]).strip().lower()
            dept_id = dept_name_to_id.get(dept_name)
        if dept_id is None or dept_id not in dept_id_set:
            errors.append(f"Row {row_num}: invalid or missing department")
            skipped += 1
            continue

        # gender
        raw_gender = str(row.get("gender", "")).strip().lower()
        gender = GENDER_MAP.get(raw_gender)
        if gender is None:
            gender = GenderEnum.Other

        # batch_type
        raw_batch = str(row.get("batch_type", "")).strip().lower()
        batch_type = BATCH_MAP.get(raw_batch, BatchTypeEnum.Morning)

        # cnic
        cnic = str(row.get("cnic", "")).strip()
        if not cnic:
            errors.append(f"Row {row_num}: missing cnic")
            skipped += 1
            continue

        full_name = str(row.get("full_name", "")).strip()
        father_name = str(row.get("father_name", "")).strip()

        student_data = dict(
            reg_no=reg_no,
            full_name=full_name or "N/A",
            father_name=father_name or "N/A",
            cnic=cnic,
            dob=_parse_date(row.get("dob")),
            gender=gender,
            email=str(row.get("email", "")).strip() or None,
            mobile_number=str(row.get("mobile_number", "")).strip() or None,
            department_id=dept_id,
            batch_type=batch_type,
            semester_no=_parse_int(row.get("semester_no")),
            gpa=_parse_float(row.get("gpa")),
            cgpa=_parse_float(row.get("cgpa")),
            transport_required=_parse_bool(row.get("transport_required", False)),
            status=StudentStatusEnum.Bulk_Uploaded,
        )

        # Check for existing student
        existing_result = await db.execute(select(Student).where(Student.reg_no == reg_no))
        existing = existing_result.scalar_one_or_none()
        if existing:
            for field, value in student_data.items():
                if value is not None:
                    setattr(existing, field, value)
            await db.flush()
            new_student_ids.append(existing.id)
            updated += 1
        else:
            # Check duplicate cnic
            cnic_check = await db.execute(select(Student).where(Student.cnic == cnic))
            if cnic_check.scalar_one_or_none():
                errors.append(f"Row {row_num}: duplicate cnic '{cnic}'")
                skipped += 1
                continue
            student = Student(**student_data)
            db.add(student)
            await db.flush()
            await db.refresh(student)
            new_student_ids.append(student.id)
            created += 1

    # Run validator on all processed students
    discrepancies_found = 0
    if new_student_ids:
        discrepancies_found = await run_validator(db, student_ids=new_student_ids)

    return UploadResult(
        total_rows=len(df),
        created=created,
        updated=updated,
        skipped=skipped,
        errors=errors,
        discrepancies_found=discrepancies_found,
    )


@router.get("/template")
async def download_template(_: Staff = Depends(get_current_staff)):
    sample_data = [
        {
            "reg_no": "CS-2021-001",
            "full_name": "Muhammad Ali",
            "father_name": "Muhammad Khan",
            "cnic": "35202-1234567-1",
            "dob": "2000-03-15",
            "gender": "Male",
            "email": "mali@student.uog.edu.pk",
            "mobile_number": "03001234567",
            "department_id": 1,
            "batch_type": "Morning",
            "semester_no": 4,
            "gpa": 3.5,
            "cgpa": 3.4,
            "transport_required": False,
        }
    ]
    df = pd.DataFrame(sample_data, columns=CSV_TEMPLATE_COLUMNS)
    output = io.StringIO()
    df.to_csv(output, index=False)
    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode()),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=student_upload_template.csv"},
    )
