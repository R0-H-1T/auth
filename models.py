from typing import Optional
from sqlmodel import SQLModel, Field, create_engine, Session
from sqlalchemy import Engine
from pydantic import BaseModel, EmailStr




class UserSchema(BaseModel):
    name: str
    email: EmailStr
    password: str



class UserDB(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str
    password: str




# rohit = UserDB(name="rohit", email="rohit@gmail.com", password='pass')

def get_engine() -> Engine:
    return create_engine("sqlite:///database.db")



def createdb_and_tables():
    SQLModel.metadata.create_all(get_engine())


def get_session():
    session = Session(get_engine())
    try:
        yield session
    finally:
        session.close()

