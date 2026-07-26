from fastapi import FastAPI
from router import auth

app = FastAPI()

app.include_router(auth.router, tags=["auth"])


