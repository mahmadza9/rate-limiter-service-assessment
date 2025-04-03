FROM python:3.10

WORKDIR /app

COPY requirements.txt requirements.txt
COPY deps /deps
RUN pip install --no-index --find-links=/deps -r requirements.txt

COPY . .

CMD ["uvicorn", "RateLimiter:app", "--host", "0.0.0.0", "--port", "8000"]
