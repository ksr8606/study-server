FROM python:3.11-slim

WORKDIR /app

# 의존성 먼저 (코드보다 덜 바뀌어서 → 레이어 캐싱 이득)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 앱 코드 복사
COPY . .

EXPOSE 8000
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
