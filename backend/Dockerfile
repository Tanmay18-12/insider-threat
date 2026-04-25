FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y libpq-dev gcc

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Createml dir
RUN mkdir -p /app/ml/models

# The rest is mounted in docker-compose, but we can copy it for standalone
COPY . .

ENV PYTHONPATH=/app
