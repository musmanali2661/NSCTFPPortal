import enum
from datetime import date, datetime
from sqlalchemy import (
    Boolean, Column, Date, DateTime, Enum, Float, ForeignKey,
    Integer, String, Text, func,
)
from sqlalchemy.orm import relationship

from app.database import Base


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class RoleEnum(str, enum.Enum):
    Admin = "Admin"
    Coordinator = "Coordinator"


class GenderEnum(str, enum.Enum):
    Male = "Male"
    Female = "Female"
    Other = "Other"


class BatchTypeEnum(str, enum.Enum):
    Morning = "Morning"
    Evening = "Evening"
    Lateral = "Lateral"


class StudentStatusEnum(str, enum.Enum):
    Pending_Review = "Pending_Review"
    Validated = "Validated"
    Bulk_Uploaded = "Bulk_Uploaded"
    Student_Registered = "Student_Registered"


class ErrorTypeEnum(str, enum.Enum):
    Placeholder_Value = "Placeholder_Value"
    Format_Mismatch = "Format_Mismatch"
    Duplicate = "Duplicate"


class SeverityEnum(str, enum.Enum):
    Low = "Low"
    High = "High"
    Critical = "Critical"


class TicketCategoryEnum(str, enum.Enum):
    Transport = "Transport"
    Login = "Login"
    Data_Correction = "Data_Correction"
    General_Info = "General_Info"


class TicketStatusEnum(str, enum.Enum):
    Open = "Open"
    Resolved = "Resolved"


class ReviewStatusEnum(str, enum.Enum):
    Approved = "Approved"
    Needs_Revision = "Needs_Revision"


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, unique=True)
    coordinator_id = Column(Integer, ForeignKey("staff.id", use_alter=True, name="fk_dept_coordinator"), nullable=True)

    coordinator = relationship("Staff", foreign_keys=[coordinator_id], back_populates="coordinated_department")
    staff_members = relationship("Staff", foreign_keys="Staff.department_id", back_populates="department")
    students = relationship("Student", back_populates="department")


class Staff(Base):
    __tablename__ = "staff"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    email = Column(String(200), nullable=False, unique=True, index=True)
    hashed_password = Column(String(256), nullable=False)
    role = Column(Enum(RoleEnum), nullable=False, default=RoleEnum.Coordinator)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)

    department = relationship("Department", foreign_keys=[department_id], back_populates="staff_members")
    coordinated_department = relationship("Department", foreign_keys=[Department.coordinator_id], back_populates="coordinator", uselist=False)
    questions = relationship("QuestionBank", back_populates="teacher")


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    reg_no = Column(String(50), nullable=False, unique=True, index=True)
    full_name = Column(String(200), nullable=False)
    father_name = Column(String(200), nullable=False)
    cnic = Column(String(20), nullable=False, unique=True, index=True)
    dob = Column(Date, nullable=True)
    gender = Column(Enum(GenderEnum), nullable=False)
    email = Column(String(200), nullable=True)
    mobile_number = Column(String(20), nullable=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    batch_type = Column(Enum(BatchTypeEnum), nullable=False)
    semester_no = Column(Integer, nullable=True)
    gpa = Column(Float, nullable=True)
    cgpa = Column(Float, nullable=True)
    status = Column(Enum(StudentStatusEnum), nullable=False, default=StudentStatusEnum.Pending_Review)
    transport_required = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    department = relationship("Department", back_populates="students")
    discrepancies = relationship("DataDiscrepancy", back_populates="student", cascade="all, delete-orphan")


class DataDiscrepancy(Base):
    __tablename__ = "data_discrepancies"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, index=True)
    field_name = Column(String(100), nullable=False)
    error_type = Column(Enum(ErrorTypeEnum), nullable=False)
    severity = Column(Enum(SeverityEnum), nullable=False)
    is_resolved = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)

    student = relationship("Student", back_populates="discrepancies")


class SupportTicket(Base):
    __tablename__ = "support_tickets"

    id = Column(Integer, primary_key=True, index=True)
    student_cnic = Column(String(20), nullable=False, index=True)
    category = Column(Enum(TicketCategoryEnum), nullable=False)
    original_query = Column(Text, nullable=False)
    ai_suggested_reply = Column(Text, nullable=True)
    status = Column(Enum(TicketStatusEnum), nullable=False, default=TicketStatusEnum.Open)
    created_at = Column(DateTime, default=func.now(), nullable=False)


class QuestionBank(Base):
    __tablename__ = "question_bank"

    id = Column(Integer, primary_key=True, index=True)
    subject_area = Column(String(200), nullable=False)
    teacher_id = Column(Integer, ForeignKey("staff.id"), nullable=False)
    question_text = Column(Text, nullable=False)
    gift_format_blob = Column(Text, nullable=False)
    review_status = Column(Enum(ReviewStatusEnum), nullable=False, default=ReviewStatusEnum.Needs_Revision)
    created_at = Column(DateTime, default=func.now(), nullable=False)

    teacher = relationship("Staff", back_populates="questions")
