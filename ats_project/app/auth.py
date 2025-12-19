from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
import os

pwd = CryptContext(schemes=["bcrypt"])
SECRET_KEY = os.getenv("SECRET_KEY", "mysecretkey")  # fallback if env not set

def hash_password(password: str) -> str:
    # bcrypt only allows 72 characters, truncate safely
    if len(password) > 72:
        password = password[:72]
    return pwd.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    if len(password) > 72:
        password = password[:72]
    return pwd.verify(password, hashed)

def create_token(data: dict) -> str:
    data["exp"] = datetime.utcnow() + timedelta(hours=6)
    return jwt.encode(data, SECRET_KEY, algorithm="HS256")
