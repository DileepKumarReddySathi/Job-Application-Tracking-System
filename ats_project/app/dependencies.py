from fastapi import Depends, HTTPException
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer
from app.models import User
from app.database import get_db
from sqlalchemy.orm import Session
import os

# Correct token URL to match your login endpoint
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, os.environ.get("SECRET_KEY"), algorithms=["HS256"])
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def role_required(role: str):
    def wrapper(user=Depends(get_current_user)):
        if user.role.value != role:  # compare with enum value
            raise HTTPException(status_code=403, detail="Forbidden")
        return user
    return wrapper
