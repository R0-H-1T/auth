from passlib.handlers import pbkdf2
from datetime import timedelta, datetime, timezone
from joserfc import jwt
from joserfc.jwk import OctKey
from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())


'''
expired_delta expect time min/sec that is passed by the calling function.

If time is set by env:
    then set expire 
else 
    default to 60s
'''
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()     
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(seconds=120)
    to_encode.update({'exp': expire})
    print(to_encode)
    encoded_jwt = jwt.encode(claims=to_encode, header={'alg': 'HS256'}, key=OctKey.import_key(os.getenv("SECRET")))
    print(encoded_jwt)  
    return encoded_jwt
    

def hash_password(password: str) -> str:
    return pbkdf2.pbkdf2_sha256.hash(password)


def verify_password(password: str, hashed_passowrd: str) -> bool:
    return pbkdf2.pbkdf2_sha256.verify(password, hash=hashed_passowrd)