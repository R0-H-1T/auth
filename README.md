# Auth Service

### Work In Progress


> @TODOS

1. Blocklist JWT tokens (Redis)
2. Git Submodule -> auth, qna, analytics
3. Your project - docker, __init__ module
4. API gateway?
5. Deploying your microservice.
6. More on service discovery?




## Endpoints

| **Endpoint** | **Desc**
--- | ---
`/signin` | return a token after validating the user.
`/signup` |  user data stored in DB
`/signout` |  token revoked and added to blocklist 
`/token`  |  credential validation 
`/users/me` |  details about logged in user
`/allusers` |  List of all usernames





### How is the token blocklist implemented?
**Understanding the flow of the token.**
1. User signs in, a token holding the `jti` claim(Registered), used for uniquely identifying the token, is sent back. 
2. Upon each request to the API endpoints, the token is checked against the blocklist of invalid tokens. 
3. If the token is present in the list, a `401 Unauthorized` status is sent back.
4. User signs out, the token is added to the blocklist, with the key as the `jti` value and its value as an empty string.



**Implementation**
1. **REVOKE**: The token is stored in `Redis` as key value pair. <br>
    key : `JTI` claim<br>
    value : ''
    ```python
    # ex - seconds
    redis_client.set(name=claims.get('jti'), value='', ex=120)
    ```
2. **VALIDATE**: On each request the token is checked agains the block list. If the token is present in the list, an unauthorized status is sent back.
    ```python
    redis_client.get(claims.get('jti'))
    ```
**File:** [View](https://github.com/R0-H-1T/auth/blob/dev/helper.py)



## TODOS:
1. Implement refresh tokens
2. PyTest?
3. Redis Caching? - qna-svc(Questionnaires)

## Refresh token issues - 
When the user signs in [/signin]
    Access token (5 mins)
    Refresh token (10 mins)
returned to user

When user signs out [/signout]
    Access token is added to redis - blacklist token in redis using the JTI claim.
    
SECRET=1e44f1b78146dd8dca235a0cb06c78858e6171384f079662f78d88b9e5d089d3
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MIN=10
REFRESH_TOKEN_EXPIRE_MIN=20
TEST_DB_NAME=test.db
DB_HOST=localhost
DB_USER=postgres
DB_PASS=1226
DB_NAME=quiz
