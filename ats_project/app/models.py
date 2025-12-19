from sqlalchemy import Column, Integer, String, Enum, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.database import Base


# ======================
# ENUMS
# ======================

class Role(enum.Enum):
    candidate = "candidate"
    recruiter = "recruiter"
    hiring_manager = "hiring_manager"


class JobStatus(enum.Enum):
    open = "open"
    closed = "closed"


class Stage(enum.Enum):
    Applied = "Applied"
    Screening = "Screening"
    Interview = "Interview"
    Offer = "Offer"
    Hired = "Hired"
    Rejected = "Rejected"


# ======================
# USER MODEL
# ======================

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(Enum(Role), nullable=False)
    company_id = Column(Integer, nullable=True)

    applications = relationship("Application", back_populates="candidate")


# ======================
# JOB MODEL
# ======================

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    status = Column(Enum(JobStatus), default=JobStatus.open, nullable=False)
    company_id = Column(Integer, nullable=True)

    applications = relationship("Application", back_populates="job")


# ======================
# APPLICATION MODEL
# ======================

class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    candidate_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    stage = Column(Enum(Stage), default=Stage.Applied, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    job = relationship("Job", back_populates="applications")
    candidate = relationship("User", back_populates="applications")
    history = relationship("ApplicationHistory", back_populates="application")


# ======================
# APPLICATION HISTORY
# ======================

class ApplicationHistory(Base):
    __tablename__ = "application_history"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=False)

    previous_stage = Column(Enum(Stage), nullable=True)
    new_stage = Column(Enum(Stage), nullable=False)

    changed_by = Column(Integer, ForeignKey("users.id"))
    changed_at = Column(DateTime, default=datetime.utcnow)

    application = relationship("Application", back_populates="history")
