from sqlmodel import SQLModel, Field, create_engine, Session
from sqlalchemy import Engine, URL
from pydantic import EmailStr, BaseModel
import uuid
import os


class UserBase(SQLModel):
    name: str
    email: EmailStr


class UserSchema(UserBase):
    password: str


class UserDB(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
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
    refresh_token: str


class TokenData(BaseModel):
    email: EmailStr | None = None


def get_engine() -> Engine:
    url = URL.create(
        drivername="postgresql+psycopg2",
        username=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
    )
    return create_engine(url, echo=True)


def createdb_and_tables():
    SQLModel.metadata.create_all(get_engine())


def get_session():
    with Session(get_engine()) as session:
        yield session
