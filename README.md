> What you'll do in the holidays

1. Buid your portfolio
2. Redis and quizz application
3. Git Submodules -> auth, quizz
4. Your project - docker, __init__ module
5. API gateway?
6. Deploying your microservice - You have AWS right.
7. what is service discovery
8. More on asynchronous in service, what is it really. Asynchronous Programming?
9. Git tree workflow


## Quizz Application

---

**Microservice Architecture**
> Tech Used:
1. FastAPI
2. SQLModel
3. ---Coming up



**Endpoints**
auth:
1. /signin - return a token after validating the user.
2. /signup - user data stored in DB
3. /token - 
4. /users/me

qna:
1. /question






@TODO An endpoint to get the current user, so that you associate the questionnaire with the user or answer.

/question
    - Validates the user from **auth service** @ /token
    - creates the questionnaire



### Scenario 1:
auth service maintains a DB, storing the users roles.

