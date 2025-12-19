from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.models import User, Role
from app.auth import hash_password, verify_password, create_token
from app.database import get_db
from app.dependencies import get_current_user
from fastapi.security import OAuth2PasswordRequestForm


router = APIRouter(prefix="/users", tags=["users"])

# -------------------------
# Pydantic Schemas
# -------------------------
class UserRegister(BaseModel):
    email: str
    password: str
    role: str  # Will convert to Role Enum in code

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    role: str

# -------------------------
# Register new user
# -------------------------
@router.post("/register", response_model=UserResponse)
def register(user_in: UserRegister, db: Session = Depends(get_db)):
    # Convert role string to Enum
    try:
        role_enum = Role(user_in.role)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid role")

    # Check if email already exists
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create user
    try:
        user = User(
            email=user_in.email,
            password=hash_password(user_in.password),
            role=role_enum,
            company_id=None
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    return {"id": user.id, "email": user.email, "role": user.role.value}

# -------------------------
# Login
# -------------------------
@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_token({"user_id": user.id, "role": user.role.value})
    return {"access_token": token, "token_type": "bearer"}

# -------------------------
# Current user info
# -------------------------
@router.get("/me", response_model=UserResponse)
def me(user=Depends(get_current_user)):
    return {"id": user.id, "email": user.email, "role": user.role.value}
