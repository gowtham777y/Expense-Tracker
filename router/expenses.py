from fastapi import APIRouter,HTTPException, Depends, status
from database.database import get_db
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import date
from authentication.auth import get_current_user
from database.models import UserModel,ExpenseModel,CategoryModel
from date_ranges import get_month_ranges

class Expense(BaseModel):
    name: str
    category: str
    description: str
    expense_date: date
    amount: float

router = APIRouter()

@router.post("/expenses")
def add_expense(expense: Expense,db: Session = Depends(get_db),current_user_email: str = Depends(get_current_user)):
    db_user = db.query(UserModel).filter(UserModel.email == current_user_email).first()
    db_category = db.query(CategoryModel).filter(CategoryModel.category == expense.category).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category doesn't exist")
    db_expense = ExpenseModel(
        name=expense.name,
        category=expense.category,
        description=expense.description,
        date=expense.expense_date,
        amount=expense.amount,
        user_id=db_user.id
    )
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return {"status": status.HTTP_201_CREATED, "message": "Expense added", "expense_id": {db_expense.id}}

@router.get("/expenses")
def get_expenses(month_name: str,db:Session = Depends(get_db), current_user_email: str = Depends(get_current_user)):
    db_user = db.query(UserModel).filter(UserModel.email == current_user_email).first()
    start_date, end_date = get_month_ranges(month_name)
    query_results = db.query(
        ExpenseModel.name.label("expense_name"),
        ExpenseModel.amount.label("expense_amount"),
        ExpenseModel.description.label("expense_description")
    ).select_from(ExpenseModel).filter(
        ExpenseModel.user_id == db_user.id,
        ExpenseModel.date >= start_date,
        ExpenseModel.date <= end_date
    ).all()
    if not query_results:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail="No Expenses found")
    result = []
    for row in query_results:
        result.append({
            "Expense Name": row.expense_name,
            "Amount Spent": row.expense_amount,
            "Description": row.expense_description
        })
    return result