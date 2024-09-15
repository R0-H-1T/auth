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