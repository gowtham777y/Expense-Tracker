from sqlalchemy import Column, String, Integer, Date, ForeignKey, Float
from database.database import Base

class ExpenseModel(Base):
    __tablename__ = "expenses"

    id = Column(Integer,primary_key=True,index=True)
    name = Column(String)
    category = Column(String)
    description = Column(String)
    date = Column(Date)
    amount = Column(Float)
    user_id = Column(Integer)

class CategoryModel(Base):
    __tablename__ = "categories"

    id = Column(Integer,primary_key=True,index=True)
    category = Column(String)
    user_id = Column(Integer)


class BudgetModel(Base):
    __tablename__ = "budgets"

    id = Column(Integer,primary_key=True,index=True)
    category_id = Column(Integer,ForeignKey("categories.id"))
    budget = Column(Float)
    start_date = Column(Date)
    end_date = Column(Date)
    user_id = Column(Integer)

