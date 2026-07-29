from fastapi import APIRouter,HTTPException, Depends, status
from database.database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel, field_validator
from datetime import date
from authentication.auth import get_current_user_id
from database.models import ExpenseModel,CategoryModel
from date_ranges import get_month_ranges
from typing import Optional
from events.publish import publish_event

class Expense(BaseModel):
    name: str
    category: str
    description: str
    expense_date: date
    amount: float

    @field_validator("amount")
    @classmethod
    def amount_is_positive(cls,value):
        if value < 0:
            raise ValueError("Amount can't be negative")
        return value

    @field_validator("expense_date")
    @classmethod
    def date_is_future(cls,value):
        if value > date.today():
            raise ValueError("Date can't be in Future")
        return value


class ExpenseUpdate(BaseModel):
    expense_id: int
    name: str
    category: str
    description: str
    expense_date: date
    amount: float

    @field_validator("amount")
    @classmethod
    def amount_is_positive(cls,value):
        if value < 0:
            raise ValueError("Amount can't be negative")
        return value

    @field_validator("expense_date")
    @classmethod
    def date_is_future(cls,value):
        if value > date.today():
            raise ValueError("Date can't be in Future")
        return value

router = APIRouter()

@router.post("/expenses")
def add_expense(expense: Expense,db: Session = Depends(get_db),current_user_id: str = Depends(get_current_user_id)):
    db_category = db.query(CategoryModel).filter(CategoryModel.category == expense.category).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category doesn't exist")
    db_expense = ExpenseModel(
        name=expense.name,
        category=expense.category,
        description=expense.description,
        date=expense.expense_date,
        amount=expense.amount,
        user_id=current_user_id
    )
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    publish_event("expense.created", {
        "expense_id": db_expense.id,
        "user_id": current_user_id,
        "amount": db_expense.amount,
        "category": db_expense.category
    })
    return {"status": status.HTTP_201_CREATED, "message": "Expense added", "expense_id": db_expense.id}

@router.get("/expenses")
def get_expenses(
    category: Optional[str] = None,
    start_date : Optional[date] = None,
    end_date: Optional[date] = None,
    skip: Optional[int] = 0,
    limit: Optional[int] = 20,
    db:Session = Depends(get_db), 
    current_user_id: str = Depends(get_current_user_id)
    ):
    db_expenses = db.query(ExpenseModel).filter(ExpenseModel.user_id == current_user_id)
    if category:
        db_expenses = db_expenses.filter(ExpenseModel.category == category)
    if start_date:
        db_expenses = db_expenses.filter(ExpenseModel.date >= start_date)
    if end_date:
        db_expenses = db_expenses.filter(ExpenseModel.date <= end_date)
    return db_expenses.offset(skip).limit(limit).all()

@router.put("/expenses")
def update_expense(expense: ExpenseUpdate, db: Session = Depends(get_db), current_user_id: str = Depends(get_current_user_id)):
    db_expense = db.query(ExpenseModel).filter(ExpenseModel.id == expense.expense_id).first()
    if current_user_id != db_expense.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Expense is not associated with the user")
    db_expense.name = expense.name
    db_expense.description = expense.description
    db_expense.amount = expense.amount
    db_expense.category = expense.category
    db_expense.date = expense.expense_date
    db.commit()
    db.refresh(db_expense)
    return {"status": status.HTTP_200_OK, "Expense ID": db_expense.id, "message": "Expense Updated"}

@router.delete("/expenses")
def delete_expense(expense_id: int, db: Session = Depends(get_db), current_user_id: str = Depends(get_current_user_id)):
    db_expense = db.query(ExpenseModel).filter(ExpenseModel.id == expense_id).first()
    if not db_expense:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")
    if db_expense.user_id != current_user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your Expense")
    db.delete(db_expense)
    db.commit()
    return {"status": status.HTTP_200_OK, "message": "Expense Deleted"}

@router.get("/expenses/summary")
def get_expenses_summary(month_name: str, db: Session = Depends(get_db), current_user_id: str = Depends(get_current_user_id)):
    start_date, end_date = get_month_ranges(month_name)
    query_results = db.query(
        ExpenseModel.category.label("category_name"),
        func.sum(ExpenseModel.amount).label("expense_amount")
    ).filter(
        ExpenseModel.user_id == current_user_id,
        ExpenseModel.date >= start_date,
        ExpenseModel.date <= end_date
    ).group_by(
        ExpenseModel.category
    ).all()
    if not query_results:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Expenses found")
    result = []
    for row in query_results:
        result.append({
            "Category" : row.category_name,
            "Total Spent" : row.expense_amount
        })
    return result