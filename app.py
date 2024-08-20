from fastapi import FastAPI, Query, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from contextlib import asynccontextmanager
from models import createdb_and_tables, UserSchema, get_session, UserDB, UserSchemaSignIn, Token, TokenData
from pydantic import ValidationError
from sqlmodel import select, Session
from helper import hash_password, verify_password, create_access_token
from dotenv import load_dotenv, find_dotenv
from typing import Annotated
from datetime import timedelta
import os
from joserfc import jwt
from jwt.exceptions import InvalidTokenError

@asynccontextmanager
async def lifespan(app: FastAPI):
    createdb_and_tables()
    yield


app = FastAPI(lifespan=lifespan)

load_dotenv(find_dotenv())


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="signin")


@app.get("/", tags=['root'])
async def root() -> dict:
    return {"hello": "world"}


async def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)], 
        session: Session = Depends(get_session)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={'WWW-Authenticate': 'Bearer'}
    )

    try:
        payload = jwt.decode(token, os.getenv('SECRET'), algorithms=[os.getenv('ALGORITHM')])
        email = payload.claims.get('sub')        
        print(payload.claims.get('exp'))
        if email is None:
            raise credentials_exception
        token_data = TokenData(email = email)
    except InvalidTokenError:
        raise credentials_exception

    db_user = session.exec(select(UserDB).where(UserDB.email == token_data.email)).first()
    if db_user is None:
        raise credentials_exception
    
    return db_user
    


@app.post('/signup', tags=['user'], response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def signup(user: UserSchema, session: Session = Depends(get_session)):

    hash_pass = hash_password(user.password)
    try:
        db_user = UserDB.model_validate(user, update={'hashed_password': hash_pass})
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
    except ValidationError as e:
        print('Wrong type: ', e.title)

    return user


@app.post('/signin', tags=['user'], status_code=status.HTTP_200_OK)
async def signin(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: Session = Depends(get_session)) -> Token:

    # form_data.username contains email
    db_user = session.exec(select(UserDB).where(UserDB.email == form_data.username)).first()

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='User not found')

    if not verify_password(form_data.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Incorrect username or password', headers={'WWW-Authenticate': 'Bearer'}
            )

    access_token_expires = timedelta(
        minutes=int(os.getenv('ACCESS_TOKEN_EXPIRE_MIN')))
    access_token = create_access_token(
        data={"sub": db_user.email}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type='bearer')


@app.get('/allusers', tags=['user'], response_model=list[UserDB])
async def get_user(offset: int = 0, limit: int = Query(default=100, le=100), session: Session = Depends(get_session)) -> list:
    return session.exec(select(UserDB).offset(offset).limit(limit)).all()



@app.get('/users/me', tags=['user'], response_model=UserDB)
def read_usesrs_me(user: Annotated[UserDB, Depends(get_current_user)]):
    return user

# @TODO - patch for email and password
# @app.patch('/users/{user_id}', response_model=UserSchema, tags=['user'])
# def update_user(user_id: int, user: UserschemaUpdate):
#     session = next(get_session())
#     db_user = session.get(UserDB, user_id)
#     if not db_user:
#         raise HTTPException(status_code=404, detail='User not found')

#     user_data = user.model_dump(exclude_unset=True)
#     if 'password' in user_data:
#         user_data['hashed_password'] = hash_password(user_data['password'])

#     # if hash_pass:
#     #     user_data['hashed_password'] = hash_pass
#     db_user.sqlmodel_update(user_data)
#     session.add(db_user)
#     session.commit()
#     session.refresh(db_user)
#     return db_user


# if __name__ == "__main__":
#     # app.run(port=3000, debug=False)
#     pass
