from fastapi import FastAPI, Query, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from contextlib import asynccontextmanager
from . models import createdb_and_tables, UserSchema, get_session, UserDB, Token
from pydantic import ValidationError
from sqlmodel import select, Session
from . helper import (
    hash_password,
    verify_password,
    create_access_token,
    deacode_access_token,
    validate_user_token,
    revoke_token,
    token_in_blocklist,
)
from dotenv import load_dotenv, find_dotenv
from typing import Annotated
from datetime import timedelta
import os


@asynccontextmanager
async def lifespan(app: FastAPI):
    createdb_and_tables()
    yield


app = FastAPI(lifespan=lifespan, title="Auth Service")

load_dotenv(find_dotenv())


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="signin")


@app.get("/", tags=["root"])
async def root() -> dict:
    return {"hello": "world"}


"""
could raise email errror, expiredtoken, db_user none
"""


async def validate_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Session = Depends(get_session),
):

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


@app.post(
    "/signup",
    tags=["user"],
    response_model=UserSchema,
    status_code=status.HTTP_201_CREATED,
)
async def signup(user: UserSchema, session: Session = Depends(get_session)):

    hash_pass = hash_password(user.password)
    try:
        db_user = UserDB.model_validate(user, update={"hashed_password": hash_pass})
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Model Validation failed: UserDB",
        )

    return user


@app.post("/signin", tags=["user"], status_code=status.HTTP_200_OK)
async def signin(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Session = Depends(get_session),
) -> Token:
    print("@/signin")
    # form_data.username contains email
    db_user = session.exec(
        select(UserDB).where(UserDB.email == form_data.username)
    ).first()

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if not verify_password(form_data.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    print(db_user.email)
    access_token = create_access_token(
        data={"sub": db_user.email},
        expires_delta=timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MIN"))),
    )
    return Token(access_token=access_token, token_type="bearer")


@app.get("/signout", tags=["user"], status_code=status.HTTP_200_OK)
async def signout(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Session = Depends(get_session),
):
    # Handle for - If already signed out?
    claims = validate_user_token(token, session)
    revoke_token(claims)


@app.get("/allusers", tags=["user"])
async def get_user(
    offset: int = 0,
    limit: int = Query(default=100, le=100),
    session: Session = Depends(get_session),
) -> list:
    users = session.exec(select(UserDB).offset(offset).limit(limit)).all()
    all_users = []
    for user in users:
        all_users.append(user.name)

    return all_users


@app.get("/token", tags=["user"], status_code=status.HTTP_200_OK)
async def validate_token(res=Depends(validate_user)):
    if not res:
        return {"detail", "Error in /token endpoint"}
    return res


@app.get("/users/me", tags=["user"], response_model=UserDB)
def read_usesrs_me(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Session = Depends(get_session),
):
    claims = validate_user_token(token, session)
    db_user = session.exec(
        select(UserDB).where(UserDB.email == claims.get("sub"))
    ).first()
    return db_user


@app.get("/host_role", tags=["roles"], status_code=status.HTTP_200_OK)
async def host_role(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Session = Depends(get_session),
):
    claims = validate_user_token(token, session)
    return claims


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


"""
curl -X 'GET' \
  'http://localhost:8000/token' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -H 'Authorization:bearer ' 

"""
