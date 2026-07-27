from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from database.models import UserModel, ExpenseModel, CategoryModel, BudgetModel
from date_ranges import get_month_ranges
from database.database import get_db
from authentication.auth import get_current_user

router = APIRouter()

@router.get("/balance")
def get_balance(month_name: str, db: Session = Depends(get_db), current_user_email: str = Depends(get_current_user)):
    db_user = db.query(UserModel).filter(UserModel.email == current_user_email).first()
    if not db_user.budget:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="Budget doesn't exists")
    start_date, end_date = get_month_ranges(month_name)
    found = None
    for budgetModel in db_user.budget:
        if budgetModel.start_date == start_date:
            found = budgetModel
            break
    if not found:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="Budget doesn't exists")
    query_results = db.query(
        CategoryModel.category.label("category_name"),
        BudgetModel.budget.label("budget_amount"),
        func.sum(ExpenseModel.amount).label("total_spent")
    ).join(
        CategoryModel,
        BudgetModel.category_id == CategoryModel.id
    ).outerjoin(
        ExpenseModel,
        (ExpenseModel.user_id == BudgetModel.user_id) &
        (ExpenseModel.category == CategoryModel.category)&
        (ExpenseModel.date >= start_date)&
        (ExpenseModel.date <= end_date)
    ).filter(
        BudgetModel.user_id == db_user.id,
        BudgetModel.start_date == start_date
    ).group_by(
        CategoryModel.id,
        BudgetModel.id
    ).all()

    report = []
    for row in query_results:
        spent = row.total_spent if row.total_spent is not None else 0.0
        balance = row.budget_amount - spent
        report.append({
            "Category Name": row.category_name,
            "Budget Amount": row.budget_amount,
            "Total Spent": spent,
            "Balance": balance
        })
    return report
    