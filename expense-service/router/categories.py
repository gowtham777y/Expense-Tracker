from fastapi import APIRouter, Depends, HTTPException, status
from database.models import CategoryModel
from database.database import get_db
from authentication.auth import get_current_user_id
from sqlalchemy.orm import Session
from pydantic import BaseModel

class Category(BaseModel):
    name: str

router = APIRouter()

@router.get("/category")
def get_category(db: Session = Depends(get_db),current_user_id: str = Depends(get_current_user_id)):
    return db.query(CategoryModel).filter(CategoryModel.user_id == current_user_id).all()

@router.post("/category")
def add_category(category: Category, db: Session = Depends(get_db), current_user_id: str = Depends(get_current_user_id)):
    existing = db.query(CategoryModel).filter(
        CategoryModel.category == category.name,
        CategoryModel.user_id == current_user_id
        ).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="Category already exists")
    db_category = CategoryModel(
        category=category.name,
        user_id = current_user_id
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return {"status": status.HTTP_201_CREATED, "message": "Category created"}