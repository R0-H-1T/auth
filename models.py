from typing import Optional
from sqlmodel import SQLModel, Field, create_engine, Session
from sqlalchemy import Engine
from pydantic import EmailStr, BaseModel


class UserBase(SQLModel):
    name: str 
    email: EmailStr


class UserSchema(UserBase):
    password: str 


class UserDB(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str = Field()


class UserSchemaSignIn(SQLModel):
    password: str
    email: EmailStr


class UserSchemaFlex(UserSchema):
    id: int


# class UserschemaUpdate(SQLModel):
#     name: str | None = None
#     email: EmailStr | None = None
#     password: str | None = None


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: EmailStr | None = None



# rohit = UserDB(name="rohit", email="rohit@gmail.com", password='pass')

def get_engine() -> Engine:
    return create_engine("sqlite:///database.db")



def createdb_and_tables():
    SQLModel.metadata.create_all(get_engine())


def get_session():
    with Session(get_engine()) as session:
        yield session

