# 마이페이지 마이크로서비스

영양제 추천 서비스(MSA)의 마이페이지 담당 서비스입니다.

## 기술 스택
- **언어**: Python 3.11
- **프레임워크**: FastAPI
- **ORM**: SQLAlchemy 2.0 (async)
- **DB**: PostgreSQL (AWS RDS)
- **스토리지**: AWS S3 (프로필 이미지)
- **컨테이너**: Docker

## API 목록

| Method | 엔드포인트 | 설명 |
|--------|-----------|------|
| GET | `/api/v1/users/me` | 내 프로필 조회 |
| PUT | `/api/v1/users/me` | 프로필 수정 |
| POST | `/api/v1/users/me/profile-image` | 프로필 이미지 업로드 |
| PUT | `/api/v1/users/me/settings` | 알림 설정 변경 |
| DELETE | `/api/v1/users/me` | 회원 탈퇴 |
| GET | `/health` | 헬스체크 (AWS ALB용) |

## 프로젝트 구조

```
mypage-service/
├── app/
│   ├── api/v1/endpoints/
│   │   └── users.py        # API 라우터
│   ├── core/
│   │   ├── config.py       # 환경변수 설정
│   │   └── security.py     # JWT 인증
│   ├── db/
│   │   └── database.py     # DB 연결
│   ├── models/
│   │   └── user.py         # SQLAlchemy 모델
│   ├── schemas/
│   │   └── user.py         # Pydantic 스키마 (요청/응답)
│   ├── services/
│   │   └── user_service.py # 비즈니스 로직
│   └── main.py             # FastAPI 앱 진입점
├── tests/
├── Dockerfile
├── docker-compose.yml      # 로컬 개발용
├── requirements.txt
└── .env.example
```

## 로컬 실행 방법

```bash
# 1. 환경변수 설정
cp .env.example .env
# .env 파일에서 DB, JWT, AWS 설정 수정

# 2. Docker로 실행 (DB 포함)
docker-compose up --build

# 3. API 문서 확인
open http://localhost:8000/docs
```

## DB 마이그레이션

```bash
# 마이그레이션 파일 생성
alembic revision --autogenerate -m "create users table"

# 마이그레이션 적용
alembic upgrade head
```
