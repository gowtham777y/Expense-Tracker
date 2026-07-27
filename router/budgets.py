from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from authentication.auth import get_current_user
from database.database import get_db
from database.models import UserModel, BudgetModel, CategoryModel, ExpenseModel
from pydantic import BaseModel
from date_ranges import get_month_ranges

class Budget(BaseModel):
    category_name: str
    month_name: str
    budget_amount: float

class BudgetDel(BaseModel):
    category_name: str
    month_name: str

router = APIRouter()

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
    db.commit()
    db.refresh(db_budget)
    return {"status": status.HTTP_200_OK, "message": "Budget has been updated"}

@router.delete("/budget")
def delete_budget(budget: BudgetDel, db: Session = Depends(get_db), current_user_email: str= Depends(get_current_user)):
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
    del db_budget
    db.commit()
    return {"message": "Budget Deleted"}
