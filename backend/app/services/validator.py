"""
Validator service – scans the students table and creates DataDiscrepancy records
for any data quality issues detected.
"""
import re
from datetime import date
from typing import List, Tuple

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    DataDiscrepancy, ErrorTypeEnum, SeverityEnum, Student,
)

PLACEHOLDER_CNIC_RE = re.compile(r"^0{5}-0{7}-\d$")
VALID_CNIC_RE = re.compile(r"^\d{5}-\d{7}-\d$")
VALID_REG_NO_RE = re.compile(r"^[A-Za-z0-9/\-]+$")


async def run_validator(db: AsyncSession, student_ids: List[int] | None = None) -> int:
    """
    Scan students (or a subset) and upsert DataDiscrepancy rows.
    Returns the count of new discrepancies created.
    """
    query = select(Student)
    if student_ids:
        query = query.where(Student.id.in_(student_ids))
    result = await db.execute(query)
    students: List[Student] = result.scalars().all()

    # Collect all reg_nos / cnics for duplicate detection
    all_reg_nos: dict[str, list[int]] = {}
    all_cnics: dict[str, list[int]] = {}
    for s in students:
        all_reg_nos.setdefault(s.reg_no, []).append(s.id)
        all_cnics.setdefault(s.cnic, []).append(s.id)

    # Remove old unresolved discrepancies for these students before re-scanning
    target_ids = [s.id for s in students]
    if target_ids:
        await db.execute(
            delete(DataDiscrepancy).where(
                DataDiscrepancy.student_id.in_(target_ids),
                DataDiscrepancy.is_resolved == False,  # noqa: E712
            )
        )

    new_count = 0
    for student in students:
        issues: List[Tuple[str, ErrorTypeEnum, SeverityEnum]] = []

        # 1. Placeholder CNIC
        if PLACEHOLDER_CNIC_RE.match(student.cnic):
            issues.append(("cnic", ErrorTypeEnum.Placeholder_Value, SeverityEnum.Critical))
        elif not VALID_CNIC_RE.match(student.cnic):
            issues.append(("cnic", ErrorTypeEnum.Format_Mismatch, SeverityEnum.High))

        # 2. Invalid / missing DOB
        if student.dob is None:
            issues.append(("dob", ErrorTypeEnum.Format_Mismatch, SeverityEnum.High))
        elif isinstance(student.dob, date):
            if student.dob.year < 1950 or student.dob > date.today():
                issues.append(("dob", ErrorTypeEnum.Format_Mismatch, SeverityEnum.Low))

        # 3. GPA / CGPA out of range
        if student.gpa is not None and not (0.0 <= student.gpa <= 4.0):
            issues.append(("gpa", ErrorTypeEnum.Format_Mismatch, SeverityEnum.High))
        if student.cgpa is not None and not (0.0 <= student.cgpa <= 4.0):
            issues.append(("cgpa", ErrorTypeEnum.Format_Mismatch, SeverityEnum.High))

        # 4. Duplicate reg_no
        if len(all_reg_nos.get(student.reg_no, [])) > 1:
            issues.append(("reg_no", ErrorTypeEnum.Duplicate, SeverityEnum.Critical))

        # 5. Duplicate cnic
        if len(all_cnics.get(student.cnic, [])) > 1:
            issues.append(("cnic", ErrorTypeEnum.Duplicate, SeverityEnum.Critical))

        # 6. Placeholder / empty name
        if not student.full_name or student.full_name.strip().upper() in ("N/A", "NA", "NULL", "NONE", ""):
            issues.append(("full_name", ErrorTypeEnum.Placeholder_Value, SeverityEnum.High))

        # 7. Mobile number format
        if student.mobile_number:
            cleaned = re.sub(r"[\s\-]", "", student.mobile_number)
            if not re.match(r"^(\+92|0)3\d{9}$", cleaned):
                issues.append(("mobile_number", ErrorTypeEnum.Format_Mismatch, SeverityEnum.Low))

        for field, etype, severity in issues:
            db.add(DataDiscrepancy(
                student_id=student.id,
                field_name=field,
                error_type=etype,
                severity=severity,
                is_resolved=False,
            ))
            new_count += 1

    await db.flush()
    return new_count
