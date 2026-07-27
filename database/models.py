from sqlalchemy import Column, String, Integer, Date, ForeignKey
from sqlalchemy.orm import Relationship
from database.database import Base

class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True,index=True)
    name = Column(String)
    age = Column(Integer)
    email = Column(String,unique=True,index=True)
    hashed_password = Column(String)

    expenses = Relationship("ExpenseModel",back_populates="owner")
    category = Relationship("CategoryModel",back_populates="owner")
    budget = Relationship("BudgetModel",back_populates="owner")

class ExpenseModel(Base):
    __tablename__ = "expenses"

    id = Column(Integer,primary_key=True,index=True)
    name = Column(String)
    category = Column(String)
    description = Column(String)
    date = Column(Date)
    user_id = Column(Integer,ForeignKey("users.id"))

    owner = Relationship("UserModel",back_populates="expenses")

class CategoryModel(Base):
    __tablename__ = "categories"

    id = Column(Integer,primary_key=True,index=True)
    category = Column(String)
    user_id = Column(Integer,ForeignKey("users.id"))

    owner = Relationship("UserModel",back_populates="category")
    budget = Relationship("BudgetModel",back_populates="category")

class BudgetModel(Base):
    __tablename__ = "budgets"

    id = Column(Integer,primary_key=True,index=True)
    category = Column(String,ForeignKey("categories.category"))
    budget = Column(Integer)
    user_id = Column(Integer,ForeignKey("users.id"))

    owner = Relationship("UserModel",back_populates="budget")
    category = Relationship("CategoryModel",back_populates="budget")

