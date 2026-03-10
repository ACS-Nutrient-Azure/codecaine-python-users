# 마이페이지 마이크로서비스 (백엔드)

영양제 추천 서비스(MSA)의 마이페이지 담당 백엔드 서비스입니다.
프론트엔드는 [source-frontend](https://github.com/ACS-Nutrients/source-frontend) 레포를 사용합니다.

## 기술 스택

| 구분 | 기술 |
|------|------|
| **백엔드** | Python 3.11, FastAPI, SQLAlchemy 2.0 (async) |
| **DB** | PostgreSQL 16 |
| **인증** | JWT (AWS Cognito 연동 구조) |
| **OCR** | AWS Textract (한국어/영어 성분표 지원) |
| **컨테이너** | Docker, Docker Compose |

## 실행 방법

### Docker (프론트 + 백엔드 + DB 전체)

```bash
# 두 레포를 같은 디렉토리에 클론
git clone https://github.com/ACS-Nutrients/codecaine-python-mypage
git clone https://github.com/ACS-Nutrients/source-frontend

cd codecaine-python-mypage
docker compose up -d --build
```

| 서비스 | URL |
|--------|-----|
| 프론트엔드 | http://localhost:5173 |
| 마이페이지 | http://localhost:5173/my-page |
| API 문서 (Swagger) | http://localhost:8000/docs |

### 백엔드 로컬 직접 실행

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## 환경변수 (.env)

```env
DATABASE_URL=postgresql+asyncpg://...
JWT_SECRET_KEY=...
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=ap-northeast-2
```

**AWS IAM 권한 (OCR 스캔 기능 필요)**
```json
{ "Action": ["textract:DetectDocumentText"], "Effect": "Allow", "Resource": "*" }
```

## API 목록

| Method | 엔드포인트 | 설명 |
|--------|-----------|------|
| GET | `/api/users/{cognito_id}` | 마이페이지 정보 조회 |
| PUT | `/api/users/{cognito_id}` | 사용자 정보 수정 |
| DELETE | `/api/users/{cognito_id}` | 회원 탈퇴 |
| GET | `/api/supplements?cognito_id=...` | 영양제 목록 조회 |
| POST | `/api/supplements` | 영양제 추가 |
| PUT | `/api/supplements/{id}` | 영양제 수정 |
| DELETE | `/api/supplements/{id}` | 영양제 삭제 |
| PATCH | `/api/supplements/{id}/status` | 활성화/비활성화 |
| POST | `/api/supplements/scan` | 성분표 이미지 OCR 스캔 |
| GET | `/health` | 헬스체크 |
| GET | `/dev/token/{cognito_id}` | 개발용 JWT 발급 |

> 모든 API는 `Authorization: Bearer {token}` 헤더 필요

## 프로젝트 구조

```
codecaine-python-mypage/
├── app/
│   ├── api/v1/
│   │   ├── router.py             # API 라우터 (prefix: /api)
│   │   └── endpoints/
│   │       └── users.py          # 유저 + 영양제 엔드포인트
│   ├── core/
│   │   ├── config.py             # 환경변수 (pydantic-settings)
│   │   └── security.py           # JWT 인증/토큰 생성
│   ├── db/database.py            # async DB 엔진/세션
│   ├── models/
│   │   ├── user.py               # Users, UserProfile 모델
│   │   └── supplement.py         # 복용 영양제 모델
│   ├── schemas/user.py           # Pydantic 스키마 (ans_ prefix)
│   ├── services/
│   │   ├── user_service.py       # 비즈니스 로직
│   │   └── scan_service.py       # AWS Textract + 성분표 파싱
│   └── main.py
├── tests/
│   ├── conftest.py
│   ├── test_scan_service.py
│   └── test_scan_endpoint.py
├── Dockerfile
├── docker-compose.yml            # frontend(source-frontend) + backend + db
├── requirements.txt
└── .env
```

## docker-compose 구성

```
frontend (source-frontend)  → http://localhost:5173
mypage-service (FastAPI)    → http://localhost:8000
db (PostgreSQL 16)          → 내부 전용
```

프론트 → 백엔드 API 프록시는 Vite dev server가 처리 (`/api`, `/dev` → `mypage-service:8000`).

## 인증 (개발 모드)

`APP_ENV=development`일 때 `/dev/token/{cognito_id}` 엔드포인트로 JWT 자동 발급.
프론트엔드 접속 시 `test-user-001`로 자동 로그인됩니다.

## OCR 스캔 기능

영양제 성분표 사진 → AWS Textract → 자동 파싱 → 등록 폼 자동 완성.

- 한국어/영어 라벨 모두 지원
- 성분명·수치가 다른 줄에 있는 멀티라인 OCR 포맷 처리
- 제품명, 1회 복용량, 성분 목록 자동 추출

**사용 흐름**: 마이페이지 → 영양제 → 스캔하기 → 이미지 업로드 → 결과 확인/수정 → 저장

## 응답 필드명 규칙

API-SPEC.md 기준 `ans_` prefix 사용.

| API 필드명 | DB 컬럼명 |
|-----------|----------|
| `ans_birth_dt` | `birth_dt` |
| `ans_gender` | `gender` |
| `ans_height` / `ans_weight` | `height` / `weight` |
| `ans_current_id` | `current_id` |
| `ans_product_name` | `product_name` |
| `ans_ingredients` | `ingredients` (JSONB) |

---

## 트러블슈팅 히스토리

### 2026-03-09

#### 🐛 페이지 접속 시 "유효하지 않은 토큰" 오류

`localStorage`에 만료 토큰이 있으면 갱신 안 됨 → 401 응답 시 `clearAuth()` + 자동 재발급으로 수정.

#### 🐛 API-SPEC.md와 구현 불일치

| 구분 | 수정 전 | 수정 후 |
|------|--------|--------|
| prefix | `/api/v1` | `/api` |
| 사용자 조회 | `/users/me` | `/users/{cognito_id}` |
| 영양제 목록 | `/users/me/supplements` | `/supplements?cognito_id=...` |
| 상태 변경 | `PUT` + `is_active` | `PATCH /supplements/{id}/status` |

#### 🐛 빈 응답 body JSON 파싱 오류

`DELETE` 등 204 응답에서 `res.json()` 호출 → `res.text()` 후 비어있으면 `null` 반환으로 수정.

#### 🐛 `MultipleResultsFound` (500 에러)

`user_profile` 중복 행 → `scalar_one_or_none()` → `scalars().first()`로 수정.

---

### 2026-03-10

#### ✨ AWS Textract OCR 영양제 스캔 기능 추가

성분표 이미지에서 제품명·복용량·성분 자동 추출. `scan_service.py` 신규 추가.

#### ✨ Docker Compose에 프론트엔드 서비스 추가

`source-frontend` 레포를 Docker Compose로 함께 실행.
Vite proxy target 환경변수화 (`VITE_API_URL`).

#### 🐛 Docker 네트워크 미연결로 DB 접속 불가

첫 실행 실패(포트 충돌) 후 db 컨테이너가 네트워크에 연결되지 않는 문제 → `docker compose down && up`으로 해결.

#### 🐛 OCR 파싱 실패 (영어 라벨 + 멀티라인)

- 영어 성분명 30자 초과 → 길이 제한 60자로 확대
- 영어 노이즈 라인(Calories, Total Fat 등) 필터 추가
- 성분명과 수치가 별도 줄에 있는 멀티라인 포맷 파싱 추가

#### 🔧 .gitignore 추가 및 .pyc 파일 추적 제거

기존에 git에 추적되던 `__pycache__/*.pyc` 파일 46개 제거.
