import os
from datetime import timedelta
import pytest
from dotenv import load_dotenv
from app.helper import create_token
from app.models import Token
from app.models import UserDB
from sqlmodel import create_engine, SQLModel, Session
from sqlalchemy import Engine

load_dotenv()

"""
Testing with dependencies
check is database is connected?
check if redis is on?
"""

class Database:
    __engine = create_engine(url=f"sqlite:///{os.getenv('TEST_DB_NAME')}", echo=True)

    def __init__(self):
        pass
        
    def __call__():
        SQLModel.metadata.create_all(__class__)

    @staticmethod
    def get_session():
        with Session(Database.__engine) as session:
            yield session

    

def get_engine() -> Engine:
    return create_engine(url=f"sqlite:///{os.getenv('TEST_DB_NAME')}", echo=True)


SQLModel.metadata.create_all(get_engine())

def get_session():
    with Session(get_engine()) as session:
        yield session


@pytest.fixture()
def access_token(email: str):
    return create_token(
        data={"sub": email},
        expires_delta=timedelta(minutes=os.getenv("ACCESS_TOKEN_EXPIRE_MIN")),
    )


@pytest.fixture()
def refresh_token(email: str):
    return create_token(
        data={"sub": email},
        expires_delta=timedelta(minutes=os.getenv("REFRESH_TOKEN_EXPIRE_MIN")),
    )


@pytest.fixture()
def token(access_token, refresh_token) -> Token:
    return Token(access_token, "bearer", refresh_token)
