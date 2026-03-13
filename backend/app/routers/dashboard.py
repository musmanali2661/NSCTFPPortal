from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_staff
from app.database import get_db
from app.models import (
    DataDiscrepancy, Department, SeverityEnum, Staff, Student,
    StudentStatusEnum, SupportTicket, TicketStatusEnum,
)
from app.schemas import (
    DashboardStats, DepartmentStudentCount, DiscrepanciesBySeverity,
    StudentsByStatus,
)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStats)
async def get_stats(
    db: AsyncSession = Depends(get_db),
    _: Staff = Depends(get_current_staff),
):
    # Total students
    total_students_result = await db.execute(select(func.count(Student.id)))
    total_students: int = total_students_result.scalar_one()

    # Students by status
    status_counts: dict[str, int] = {}
    for s in StudentStatusEnum:
        res = await db.execute(select(func.count(Student.id)).where(Student.status == s))
        status_counts[s.value] = res.scalar_one()

    # Discrepancies by severity
    severity_counts: dict[str, int] = {}
    for sev in SeverityEnum:
        res = await db.execute(
            select(func.count(DataDiscrepancy.id)).where(
                DataDiscrepancy.severity == sev,
                DataDiscrepancy.is_resolved == False,  # noqa: E712
            )
        )
        severity_counts[sev.value] = res.scalar_one()

    # Unresolved discrepancies total
    unresolved_result = await db.execute(
        select(func.count(DataDiscrepancy.id)).where(DataDiscrepancy.is_resolved == False)  # noqa: E712
    )
    unresolved_total: int = unresolved_result.scalar_one()

    # Students per department
    dept_result = await db.execute(select(Department).order_by(Department.name))
    departments = dept_result.scalars().all()
    dept_counts = []
    for dept in departments:
        count_res = await db.execute(
            select(func.count(Student.id)).where(Student.department_id == dept.id)
        )
        dept_counts.append(
            DepartmentStudentCount(
                department_id=dept.id,
                department_name=dept.name,
                student_count=count_res.scalar_one(),
            )
        )

    # Open tickets
    open_tickets_result = await db.execute(
        select(func.count(SupportTicket.id)).where(SupportTicket.status == TicketStatusEnum.Open)
    )
    open_tickets: int = open_tickets_result.scalar_one()

    # Total staff
    total_staff_result = await db.execute(select(func.count(Staff.id)))
    total_staff: int = total_staff_result.scalar_one()

    return DashboardStats(
        total_students=total_students,
        students_by_status=StudentsByStatus(
            Pending_Review=status_counts.get(StudentStatusEnum.Pending_Review.value, 0),
            Validated=status_counts.get(StudentStatusEnum.Validated.value, 0),
            Bulk_Uploaded=status_counts.get(StudentStatusEnum.Bulk_Uploaded.value, 0),
            Student_Registered=status_counts.get(StudentStatusEnum.Student_Registered.value, 0),
        ),
        discrepancies_by_severity=DiscrepanciesBySeverity(
            Low=severity_counts.get(SeverityEnum.Low.value, 0),
            High=severity_counts.get(SeverityEnum.High.value, 0),
            Critical=severity_counts.get(SeverityEnum.Critical.value, 0),
        ),
        unresolved_discrepancies=unresolved_total,
        students_per_department=dept_counts,
        open_tickets=open_tickets,
        total_staff=total_staff,
    )
