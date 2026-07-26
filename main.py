from fastapi import FastAPI
from router import users
from database.database import Base, engine

Base.metadata.create_all(bind=engine)
app = FastAPI()

app.include_router(users.router, tags=["auth"])


