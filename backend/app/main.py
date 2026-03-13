import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from app.auth import hash_password
from app.config import get_settings
from app.database import AsyncSessionLocal, Base, engine
from app.models import Department, RoleEnum, Staff
from app.routers import (
    auth, dashboard, departments, discrepancies, question_bank,
    staff, students, tickets, uploads,
)


async def _seed_data() -> None:
    """Create default admin user and departments if they don't exist."""
    async with AsyncSessionLocal() as session:
        # Admin user
        result = await session.execute(
            select(Staff).where(Staff.email == "admin@uog.edu.pk")
        )
        if not result.scalar_one_or_none():
            admin = Staff(
                name="System Administrator",
                email="admin@uog.edu.pk",
                hashed_password=hash_password("admin123"),
                role=RoleEnum.Admin,
            )
            session.add(admin)

        # Default departments
        default_depts = [
            "Computer Science",
            "Information Technology",
            "Software Engineering",
        ]
        for dept_name in default_depts:
            existing = await session.execute(
                select(Department).where(Department.name == dept_name)
            )
            if not existing.scalar_one_or_none():
                session.add(Department(name=dept_name))

        await session.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    if settings.SECRET_KEY == "dev-secret-key-change-in-production":
        logging.warning(
            "SECURITY WARNING: Using default SECRET_KEY. "
            "Set a strong SECRET_KEY in your .env file before deploying to production."
        )
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    # Seed initial data
    await _seed_data()
    yield
    await engine.dispose()


app = FastAPI(
    title="NSCT Focal Person Portal API",
    description="Backend API for NSCT Focal Person Portal",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(departments.router)
app.include_router(staff.router)
app.include_router(students.router)
app.include_router(discrepancies.router)
app.include_router(tickets.router)
app.include_router(uploads.router)
app.include_router(dashboard.router)
app.include_router(question_bank.router)


@app.get("/", tags=["health"])
async def root():
    return {"status": "ok", "service": "NSCT Focal Person Portal API"}


@app.get("/health", tags=["health"])
async def health():
    return {"status": "ok"}
