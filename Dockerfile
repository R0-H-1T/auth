FROM python:3.10

WORKDIR /auth

COPY ./requirements.txt /auth/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /auth/requirements.txt

COPY ./app /auth/app

EXPOSE 80

# CMD ["fastapi", "run", "app/main.py", "--port", "8082", "--host", "0.0.0.0"]
CMD ["uvicorn", "app.main:app", "--port", "80", "--host", "0.0.0.0"]
