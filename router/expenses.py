from fastapi import APIRouter,HTTPException, Depends, status
from database.database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import func
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

class ExpenseUpdate(BaseModel):
    expense_id: int
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
    if expense.amount < 0:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Negative Amount is not acceptable")
    if expense.expense_date > date.today():
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Future Expense is not acceptable")
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

@router.put("/expenses")
def update_expense(expense: ExpenseUpdate, db: Session = Depends(get_db), current_user_email: str = Depends(get_current_user)):
    db_user = db.query(UserModel).filter(UserModel.email == current_user_email).first()
    db_expense = db.query(ExpenseModel).filter(ExpenseModel.id == expense.expense_id).first()
    if db_user.id != db_expense.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Expense is not associated with the user")
    if expense.amount < 0:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Negative Amount is not acceptable")
    if expense.expense_date > date.today():
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Future Expense is not acceptable")
    db_expense.name = expense.name
    db_expense.description = expense.description
    db_expense.amount = expense.amount
    db_expense.category = expense.category
    db_expense.date = expense.expense_date
    db.commit()
    db.refresh(db_expense)
    return {"status": status.HTTP_200_OK, "Expense ID": db_expense.id, "message": "Expense Updated"}

@router.delete("/expenses")
def delete_expense(expense_id: int, db: Session = Depends(get_db), current_user_email: str = Depends(get_current_user)):
    db_user = db.query(UserModel).filter(UserModel.email == current_user_email).first()
    db_expense = db.query(ExpenseModel).filter(ExpenseModel.id == expense_id).first()
    if not db_expense:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")
    if db_expense.user_id != db_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your Expense")
    db.delete(db_expense)
    db.commit()
    return {"status": status.HTTP_200_OK, "message": "Expense Deleted"}

@router.get("/expenses/summary")
def get_expenses_summary(month_name: str, db: Session = Depends(get_db), current_user_email: str = Depends(get_current_user)):
    db_user = db.query(UserModel).filter(UserModel.email == current_user_email).first()
    start_date, end_date = get_month_ranges(month_name)
    query_results = db.query(
        ExpenseModel.category.label("category_name"),
        func.sum(ExpenseModel.amount).label("expense_amount")
    ).select_from(ExpenseModel).join(
        CategoryModel,
        CategoryModel.category == ExpenseModel.category
    ).filter(
        ExpenseModel.user_id == db_user.id,
        ExpenseModel.date >= start_date,
        ExpenseModel.date <= end_date
    ).group_by(
        CategoryModel.category
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