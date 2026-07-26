from fastapi import FastAPI
from router import users

app = FastAPI()

app.include_router(users.router, tags=["auth"])


