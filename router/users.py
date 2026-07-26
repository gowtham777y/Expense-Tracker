from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import UserModel

class User(BaseModel):
    name: str
    age: int
    email : str
    password : str

router = APIRouter()

@router.post("/signup")
def signup(user: User, db: Session = Depends(get_db)):
    db_user = db.query(UserModel).filter(UserModel.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return {"message": "User created"}

@router.post("/login")
def login(user: User,db : Session = Depends(get_db)):
    return {"message": "User Logged in"}
