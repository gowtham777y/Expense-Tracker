from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import UserModel
from authentication.auth import hash_password, verify_password, create_access_token

class User(BaseModel):
    name: str
    age: int
    email : str
    password : str

router = APIRouter()

@router.post("/signup")
def signup(user: User, db: Session = Depends(get_db)):
    existing = db.query(UserModel).filter(UserModel.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = hash_password(user.password)
    db_user = UserModel(
        name=user.name,
        age=user.age,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"message": "User has been Signed up"}

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(),db : Session = Depends(get_db)):
    db_user = db.query(UserModel).filter(UserModel.email == form_data.username).first()
    if not db_user or not verify_password(form_data.password,db_user.hashed_password):
        raise HTTPException(status_code=404, detail="Invalid Username or Password")
    access_token = create_access_token(data={"sub": db_user.email})
    return {"access_token": access_token, "type": "bearer"}

