from sqlalchemy import Column, String, Integer
from database.database import Base

class UserModel(Base):
    __tablename__ = "users"

    name = Column(String,primary_key=True,index=True)
    age = Column(Integer)
    email = Column(String,unique=True,index=True)
    hashed_password = Column(String)