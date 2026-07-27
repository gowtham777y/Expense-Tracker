from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from authentication.auth import get_current_user
from database.database import get_db
from database.models import UserModel, BudgetModel
from pydantic import BaseModel
from datetime import date
import calendar

class Budget(BaseModel):
    category_name: str
    month_name: str
    budget_amount: float

router = APIRouter()

def get_month_ranges(month_name : str):
    cleaned_month = month_name.strip().capitalize()
    try:
        month_list = list(calendar.month_name)
        month_number = month_list.index(cleaned_month)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Month name")
    current_year = date.today().year
    start_date = date(current_year,month_number,1)
    _, total_days = calendar.monthrange(current_year,month_number)
    end_date = date(current_year,month_number,total_days)
    return start_date,end_date 

@router.post("/budget")
def add_budget(budget: Budget, db: Session = Depends(get_db), current_user_email: str = Depends(get_current_user)):
    db_user = db.query(UserModel).filter(UserModel.email == current_user_email).first()
    db_category = None
    for categoryModel in db_user.category:
        if categoryModel.category == budget.category_name:
            db_category = categoryModel
            break
    if not db_category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found for User")
    start_date , end_date = get_month_ranges(budget.month_name)
    existing = None
    for budgetModel in db_user.budget:
        if budgetModel.start_date == start_date and budgetModel.category_id == db_category.id:
            existing = budgetModel
            break
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Budget already exists for this Month")
    db_budget = BudgetModel(
        category_id = db_category.id,
        budget = budget.budget_amount,
        start_date=start_date,
        end_date = end_date,
        user_id = db_user.id
    )
    db.add(db_budget)
    db.commit()
    db.refresh(db_budget)
    return {"status": status.HTTP_201_CREATED, "message": "Budget created"}

@router.put("/budget")
def update_budget(budget: Budget, db: Session = Depends(get_db), current_user_email: str = Depends(get_current_user)):
    db_user = db.query(UserModel).filter(UserModel.email == current_user_email).first()
    db_category = None
    for categoryModel in db_user.category:
        if categoryModel.category == budget.category_name:
            db_category = categoryModel
            break
    if not db_category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category doesn't exist")
    db_budget = None
    start_date, end_date = get_month_ranges(budget.month_name)
    for budgetModel in db_user.budget:
        if budgetModel.category_id == db_category.id and budgetModel.start_date == start_date:
            db_budget = budgetModel
            break
    if not db_budget:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Budget doesn't exist")
    db_budget.budget = budget.budget_amount
    return {"status": status.HTTP_200_OK, "message": "Budget has been updated"}