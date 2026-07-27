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

@router.post("/budgets")
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

@router.put("/budgets")
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

@router.delete("/budgets")
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
    db.delete(db_budget)
    db.commit()
    return {"message": "Budget Deleted"}

@router.get("/budgets")
def get_budgets(month_name: str, db: Session = Depends(get_db), current_user_email: str = Depends(get_current_user)):
    db_user = db.query(UserModel).filter(UserModel.email == current_user_email).first()
    start_date , end_date = get_month_ranges(month_name)
    query_results = db.query(
        CategoryModel.category.label("Category_Name"),
        BudgetModel.budget.label("Budget_Amount")
    ).select_from(BudgetModel).join(
        CategoryModel
    ).filter(
        BudgetModel.user_id == db_user.id,
        BudgetModel.start_date == start_date
    ).all()
    if not query_results:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Budget not created")
    report = []
    for row in query_results:
        report.append({
            "Category Name": row.Category_Name,
            "Budget Amount": row.Budget_Amount
        })
    return report

@router.get("/budgets/status")
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
    