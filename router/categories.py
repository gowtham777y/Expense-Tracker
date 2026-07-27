from fastapi import APIRouter, Depends, HTTPException, status
from database.models import CategoryModel, UserModel
from database.database import get_db
from authentication.auth import get_current_user
from sqlalchemy.orm import Session
from pydantic import BaseModel

class Category(BaseModel):
    name: str

router = APIRouter()

@router.get("/category")
def get_category(db: Session = Depends(get_db),current_user_email: str = Depends(get_current_user)):
    db_user = db.query(UserModel).filter(UserModel.email == current_user_email).first()
    db_categories = db.query(CategoryModel).filter(CategoryModel.user_id == db_user.id).all()
    return db_categories

@router.post("/category")
def add_category(category: Category, db: Session = Depends(get_db), current_user_email: str = Depends(get_current_user)):
    db_user = db.query(UserModel).filter(UserModel.email == current_user_email).first()
    existing = db.query(CategoryModel).filter(
        CategoryModel.category == category.name,
        CategoryModel.user_id == db_user.id
        ).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="Category already exists")
    db_category = CategoryModel(
        category=category.name,
        user_id = db_user.id
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return {"status": status.HTTP_201_CREATED, "message": "Category created"}