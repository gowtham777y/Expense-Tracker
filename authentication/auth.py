from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt, JWTError
import os
from dotenv import load_dotenv
from pathlib import Path

pwd_context = CryptContext(schemes=["bcrypt"],deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 15))
SECRET_KEY = os.getenv("SECRET_KEY", "IwatchedOdesseyrecently")

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(dotenv_path=BASE_DIR / ".env")

def hash_password(password : str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hash_password: str) -> bool:
    return pwd_context.verify(plain_password,hash_password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expire_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode,SECRET_KEY,algorithm="HS256")