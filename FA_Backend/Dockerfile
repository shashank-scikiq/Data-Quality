FROM python:3.11.9-slim

# ARG POSTGRES_SCHEMA='dev_v3'

WORKDIR /app
WORKDIR /app/Webapp

COPY FA_BACKEND/ /app/Webapp/
COPY requirements.txt /app/Webapp/

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN python manage.py collectstatic --noinput

# CMD ["fastapi", "run", "main.py", "0.0.0.0:8001"]
CMD ["uvicorn", "main:app", "--port", "8001"]