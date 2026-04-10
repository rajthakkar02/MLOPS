
FROM python:3.12-slim AS builder

WORKDIR /app

COPY requirements.txt .

RUN pip wheel --no-cache-dir --wheel-dir /app/wheels -r requirements.txt

FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /app/wheels /wheels

RUN pip install --no-cache-dir /wheels/*

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]