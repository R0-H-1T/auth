from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel, ValidationError
from models import createdb_and_tables, UserSchema, get_session, UserDB
from sqlmodel import select


app = FastAPI()


class Person(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None


class PostSchema(BaseModel):
    id: int
    title: str
    content: Union[str | None]





posts: list[dict] = []
posts = [
    {
        "id": 1,
        "title": "Pancake",
        "content": "lorem"
    }
]

@app.on_event("startup")
def on_startup():
    createdb_and_tables()


@app.get("/", tags=['root'])
async def root() -> dict:
    return {"hello": "world"}

@app.get('/posts', tags=['post'])
async def get_posts() -> dict:
    return { "data": posts}


@app.get('/post/{post_id}')
async def get_one_post(post_id: int) -> dict:
    if post_id > len(posts):
        return {"error": "Not found"}
    
    for post in posts:
        if post["id"] == post_id:
            return {
                "data": post
            }


@app.post('/post', tags=['post'])
async def create_post(post: PostSchema) -> dict:
    posts.append(post)
    return {
        "success": "inserted successfully"
    }


@app.post('/create_user', tags=['user'])
async def create_user(user: UserSchema) -> dict:
    try:
        user = UserDB.model_validate(user)
    except ValidationError as e:
        print('Received an error: ',e)
    else:
        print('Real cool')

    
    # manually call the next session
    # Fix? -> read on dependency injection in fastapi
    session = next(get_session())

    session.add(user)
    session.commit()
    session.refresh(user)
    

    return {
        "data": user
    }



@app.get('/users', tags=['user'])
async def get_user() -> list:

    data = []

    session = next(get_session())
    statement = select(UserDB)
    results = session.exec(statement)
    for user in results:
        data.append(user)
    return data
    

# if __name__ == "__main__":
#     # app.run(port=3000, debug=False)
#     pass   

