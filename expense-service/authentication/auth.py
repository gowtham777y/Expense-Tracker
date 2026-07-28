from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException
from jose import jwt, JWTError
import os
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(dotenv_path=BASE_DIR / ".env")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="http://localhost:8001/login")
expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 15))
SECRET_KEY = os.getenv("SECRET_KEY", "IwatchedOdesseyrecently")

def get_current_user_id(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=["HS256"])
        user_id = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
        return user_id
    except JWTError:
        raise credentials_exception