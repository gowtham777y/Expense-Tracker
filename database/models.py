from sqlalchemy import Column, String, Integer
from database.database import Base

class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True,index=True)
    name = Column(String)
    age = Column(Integer)
    email = Column(String,unique=True,index=True)
    hashed_password = Column(String)