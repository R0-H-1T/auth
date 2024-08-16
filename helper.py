from passlib.hash import pbkdf2_sha256
from passlib.handlers import pbkdf2

def hash_password(password: str) -> str:
    return pbkdf2.pbkdf2_sha256.hash(password)

def verify_password(password: str, hashed_passowrd: str) -> bool:
    return pbkdf2.pbkdf2_sha256.verify(password, hash=hashed_passowrd)