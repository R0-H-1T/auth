from passlib.handlers import pbkdf2
from datetime import timedelta, datetime, timezone
from joserfc import jwt
from dotenv import load_dotenv, find_dotenv
from sqlmodel import Session, select
import os
from typing import Dict
from fastapi import HTTPException, status
from joserfc.jwk import OctKey
from joserfc.jwt import JWTClaimsRegistry
from joserfc.errors import ExpiredTokenError
from models import UserDB
import redis
from uuid import uuid4


redis_client = redis.Redis(
    host="localhost", port=6379, charset="utf-8", decode_responses=True, db=2
)

load_dotenv(find_dotenv())


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(seconds=300)
    to_encode.update({"exp": expire, "jti": str(uuid4())})
    print(to_encode)
    encoded_jwt = jwt.encode(
        claims=to_encode,
        header={"alg": "HS256"},
        key=OctKey.import_key(os.getenv("SECRET")),
    )
    return encoded_jwt


def deacode_access_token(token: str):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentialss",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, key=OctKey.import_key(os.getenv("SECRET")))

        JWTClaimsRegistry(exp={"essential": True}, jti={"essential": True}).validate(
            payload.claims
        )

        email = payload.claims.get("sub")
        if email is None:
            print("*" * 10, "no email")
            raise credentials_exception
    except ExpiredTokenError:
        print("*" * 10, "expired")
        raise credentials_exception
    return payload.claims


def validate_user_token(token, session: Session):
    claims = deacode_access_token(token)

    token_in_blocklist(claims)

    db_user = session.exec(
        select(UserDB).where(UserDB.email == claims.get("sub"))
    ).first()

    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="No user found!"
        )
    return claims


def token_in_blocklist(claims: Dict):
    if redis_client.get(name=claims.get("jti")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="REVOKED \nCould not validate credentials",
        )


def revoke_token(claims: Dict):
    redis_client.set(
        name=claims.get("jti"),
        value="name",
        ex=timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MIN"))),
    )


def hash_password(password: str) -> str:
    return pbkdf2.pbkdf2_sha256.hash(password)


def verify_password(password: str, hashed_passowrd: str) -> bool:
    return pbkdf2.pbkdf2_sha256.verify(password, hash=hashed_passowrd)
