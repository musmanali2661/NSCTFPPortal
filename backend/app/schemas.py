from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, field_validator, model_validator
import re

from app.models import (
    RoleEnum, GenderEnum, BatchTypeEnum, StudentStatusEnum,
    ErrorTypeEnum, SeverityEnum, TicketCategoryEnum, TicketStatusEnum,
    ReviewStatusEnum,
)


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    staff_id: int
    role: RoleEnum
    name: str


# ---------------------------------------------------------------------------
# Department
# ---------------------------------------------------------------------------

class DepartmentBase(BaseModel):
    name: str
    coordinator_id: Optional[int] = None


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentUpdate(BaseModel):
    name: Optional[str] = None
    coordinator_id: Optional[int] = None


class DepartmentOut(DepartmentBase):
    id: int

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Staff
# ---------------------------------------------------------------------------

class StaffBase(BaseModel):
    name: str
    email: str
    role: RoleEnum = RoleEnum.Coordinator
    department_id: Optional[int] = None


class StaffCreate(StaffBase):
    password: str


class StaffUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[RoleEnum] = None
    department_id: Optional[int] = None
    password: Optional[str] = None


class StaffOut(StaffBase):
    id: int

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Student
# ---------------------------------------------------------------------------

class StudentBase(BaseModel):
    reg_no: str
    full_name: str
    father_name: str
    cnic: str
    dob: Optional[date] = None
    gender: GenderEnum
    email: Optional[str] = None
    mobile_number: Optional[str] = None
    department_id: int
    batch_type: BatchTypeEnum
    semester_no: Optional[int] = None
    gpa: Optional[float] = None
    cgpa: Optional[float] = None
    status: StudentStatusEnum = StudentStatusEnum.Pending_Review
    transport_required: bool = False


class StudentCreate(StudentBase):
    pass


class StudentUpdate(BaseModel):
    reg_no: Optional[str] = None
    full_name: Optional[str] = None
    father_name: Optional[str] = None
    cnic: Optional[str] = None
    dob: Optional[date] = None
    gender: Optional[GenderEnum] = None
    email: Optional[str] = None
    mobile_number: Optional[str] = None
    department_id: Optional[int] = None
    batch_type: Optional[BatchTypeEnum] = None
    semester_no: Optional[int] = None
    gpa: Optional[float] = None
    cgpa: Optional[float] = None
    status: Optional[StudentStatusEnum] = None
    transport_required: Optional[bool] = None


class StudentOut(StudentBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class StudentListOut(BaseModel):
    total: int
    items: List[StudentOut]


# ---------------------------------------------------------------------------
# Data Discrepancy
# ---------------------------------------------------------------------------

class DiscrepancyBase(BaseModel):
    student_id: int
    field_name: str
    error_type: ErrorTypeEnum
    severity: SeverityEnum
    is_resolved: bool = False


class DiscrepancyCreate(DiscrepancyBase):
    pass


class DiscrepancyOut(DiscrepancyBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Support Ticket
# ---------------------------------------------------------------------------

class TicketBase(BaseModel):
    student_cnic: str
    category: TicketCategoryEnum
    original_query: str


class TicketCreate(TicketBase):
    pass


class TicketUpdate(BaseModel):
    category: Optional[TicketCategoryEnum] = None
    original_query: Optional[str] = None
    ai_suggested_reply: Optional[str] = None
    status: Optional[TicketStatusEnum] = None


class TicketOut(TicketBase):
    id: int
    ai_suggested_reply: Optional[str] = None
    status: TicketStatusEnum
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Question Bank
# ---------------------------------------------------------------------------

class QuestionBase(BaseModel):
    subject_area: str
    teacher_id: int
    question_text: str
    gift_format_blob: str
    review_status: ReviewStatusEnum = ReviewStatusEnum.Needs_Revision


class QuestionCreate(QuestionBase):
    pass


class QuestionUpdate(BaseModel):
    subject_area: Optional[str] = None
    teacher_id: Optional[int] = None
    question_text: Optional[str] = None
    gift_format_blob: Optional[str] = None
    review_status: Optional[ReviewStatusEnum] = None


class QuestionOut(QuestionBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Upload
# ---------------------------------------------------------------------------

class UploadResult(BaseModel):
    total_rows: int
    created: int
    updated: int
    skipped: int
    errors: List[str]
    discrepancies_found: int


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

class StudentsByStatus(BaseModel):
    Pending_Review: int = 0
    Validated: int = 0
    Bulk_Uploaded: int = 0
    Student_Registered: int = 0


class DiscrepanciesBySeverity(BaseModel):
    Low: int = 0
    High: int = 0
    Critical: int = 0


class DepartmentStudentCount(BaseModel):
    department_id: int
    department_name: str
    student_count: int


class DashboardStats(BaseModel):
    total_students: int
    students_by_status: StudentsByStatus
    discrepancies_by_severity: DiscrepanciesBySeverity
    unresolved_discrepancies: int
    students_per_department: List[DepartmentStudentCount]
    open_tickets: int
    total_staff: int
