from pydantic import BaseModel, EmailStr
from enum import Enum
from typing import Optional

# ---------- User Schemas ----------

class RoleEnum(str, Enum):
    candidate = "candidate"
    recruiter = "recruiter"
    admin = "admin"

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: RoleEnum

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    role: RoleEnum

    class Config:
        orm_mode = True

# ---------- Job Schemas ----------

class JobCreate(BaseModel):
    title: str
    description: str

class JobUpdate(BaseModel):
    title: Optional[str]
    description: Optional[str]
    status: Optional[str]

class JobResponse(BaseModel):
    id: int
    title: str
    description: str
    status: str
    company_id: Optional[int]

    class Config:
        orm_mode = True

# ---------- Application Schemas ----------

class ApplicationCreate(BaseModel):
    job_id: int

class ApplicationResponse(BaseModel):
    id: int
    job_id: int
    user_id: int
    status: str

    class Config:
        orm_mode = True
