FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

# 의존성 먼저 설치 (레이어 캐싱 활용)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# OTel 추가 (aws-opentelemetry-distro: X-Ray ID 생성 포함)
RUN pip install --no-cache-dir aws-opentelemetry-distro opentelemetry-exporter-otlp
RUN opentelemetry-bootstrap -a install

# 소스 코드 복사
COPY . .

# 포트 오픈
EXPOSE 8000

# opentelemetry-instrument 앞에 추가
CMD ["opentelemetry-instrument", "gunicorn", "app.main:app", "-k", "uvicorn.workers.UvicornWorker", "--workers", "2", "--bind", "0.0.0.0:8000", "--timeout", "120"]
