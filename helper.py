from passlib.handlers import pbkdf2
from datetime import timedelta, datetime, timezone
from joserfc import jwt
from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()     
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(claims=to_encode, header={'alg': 'HS256'}, key=os.getenv("SECRET"))
    return encoded_jwt
    

def hash_password(password: str) -> str:
    return pbkdf2.pbkdf2_sha256.hash(password)


def verify_password(password: str, hashed_passowrd: str) -> bool:
    return pbkdf2.pbkdf2_sha256.verify(password, hash=hashed_passowrd)