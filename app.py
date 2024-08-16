from fastapi import FastAPI, Query, HTTPException, status, Depends
from contextlib import asynccontextmanager
from models import createdb_and_tables, UserSchema, get_session, UserDB, UserschemaUpdate, UserSchemaSignIn
from pydantic import ValidationError
from sqlmodel import select, Session
from helper import hash_password, verify_password


@asynccontextmanager
async def lifespan(app: FastAPI):
    createdb_and_tables()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/", tags=['root'])
async def root() -> dict:
    return {"hello": "world"}


@app.post('/signup', tags=['user'], response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserSchema, session: Session = Depends(get_session)):

    hash_pass = hash_password(user.password)
    try:
        db_user = UserDB.model_validate(user, update={'hashed_password': hash_pass})        
        # manually call the next session
        # Fix? -> read on dependency injection in fastapi
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
    except ValidationError as e:
        print('Not of the correct type: ',e)
    
    return user



@app.post('/signin', tags=['user'], status_code=status.HTTP_200_OK)
async def signup(user: UserSchemaSignIn, session: Session = Depends(get_session)) -> None:
    db_user = session.exec(select(UserDB).where(UserDB.email == user.email)).first()

    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    
    if not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Wrong Password')
    


@app.get('/users', tags=['user'], response_model=list[UserDB])
async def get_user(offset: int = 0, limit: int = Query(default=100, le=100),  session: Session = Depends(get_session)) -> list:
    return session.exec(select(UserDB).offset(offset).limit(limit)).all()


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

