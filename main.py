from fastapi import FastAPI
from router import users, expenses, categories, budgets
from database.database import Base, engine

Base.metadata.create_all(bind=engine)
app = FastAPI()

app.include_router(users.router, tags=["auth"])
app.include_router(categories.router, tags=["categories"])
app.include_router(expenses.router, tags=["expenses"])
app.include_router(budgets.router, tags=["budgets"])


