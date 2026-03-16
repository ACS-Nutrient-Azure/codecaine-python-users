# MyPage 서비스

사용자 프로필, 영양제 목록 관리, 영양제 성분표 OCR 스캔을 담당하는 FastAPI 마이크로서비스.
AWS Cognito JWT를 검증하여 인증하며, 첫 로그인 시 users 테이블에 자동 등록한다.

---

## 기술 스택

| 구분 | 기술 |
|------|------|
| 언어 | Python 3.11 |
| 프레임워크 | FastAPI 0.111 |
| ORM | SQLAlchemy 2.0 (async) + asyncpg |
| DB | PostgreSQL (`vitamin_user` DB) |
| 인증 | AWS Cognito (RS256 JWT via JWKS) |
| OCR | AWS Textract |
| 모니터링 | OpenTelemetry |

---

## 실행

```bash
cd services/mypage

# 가상환경 생성
python3.11 -m venv .venv
source .venv/bin/activate

# 의존성 설치
pip install -r requirements.txt

# 환경변수 설정
cp .env.example .env
# .env 값 입력

# 서버 시작
uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload
```

---

## 환경변수 (`.env`)

```env
# PostgreSQL
DATABASE_URL=postgresql+asyncpg://<user>:<password>@<host>:5432/vitamin_user

# AWS Cognito (JWT 검증용)
COGNITO_USER_POOL_ID=<User Pool ID>
COGNITO_CLIENT_ID=<App Client ID>
AWS_REGION=ap-northeast-2

# AWS (Textract OCR 사용 시)
AWS_ACCESS_KEY_ID=<IAM Access Key>
AWS_SECRET_ACCESS_KEY=<IAM Secret Key>

# CORS
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

---

## 프로젝트 구조

```
app/
├── main.py                    # FastAPI 앱 + CORS + 라우터 등록
├── api/v1/
│   ├── router.py              # 라우터 집계
│   └── endpoints/
│       └── users.py           # User + Supplement 엔드포인트
├── core/
│   ├── config.py              # pydantic-settings 환경변수
│   └── security.py            # JWT 검증 (Cognito RS256 / dev HS256 fallback)
├── db/
│   └── database.py            # async SQLAlchemy 엔진 + 세션
├── models/
│   ├── user.py                # User, UserProfile ORM 모델
│   └── supplement.py          # CurrentSupplement ORM 모델
├── schemas/
│   └── user.py                # Pydantic 요청/응답 스키마
└── services/
    ├── user_service.py        # 비즈니스 로직 (유저/영양제 CRUD)
    └── scan_service.py        # Textract OCR 호출
```

---

## API 엔드포인트

### 공통

| 메서드 | 경로 | 인증 | 설명 |
|--------|------|------|------|
| `GET` | `/health` | ❌ | 헬스체크 |
| `GET` | `/dev/token/{cognito_id}` | ❌ | 개발용 JWT 발급 (development 환경 전용) |

### 사용자 정보

| 메서드 | 경로 | 인증 | 설명 |
|--------|------|------|------|
| `GET` | `/api/users/{cognito_id}` | ✅ | 프로필 조회 (없으면 자동 생성) |
| `PUT` | `/api/users/{cognito_id}` | ✅ | 프로필 수정 |
| `DELETE` | `/api/users/{cognito_id}` | ✅ | 회원 탈퇴 |

### 영양제 관리

| 메서드 | 경로 | 인증 | 설명 |
|--------|------|------|------|
| `GET` | `/api/users/supplements` | ✅ | 영양제 목록 조회 |
| `POST` | `/api/users/supplements` | ✅ | 영양제 추가 |
| `PUT` | `/api/users/supplements/{id}` | ✅ | 영양제 수정 |
| `DELETE` | `/api/users/supplements/{id}` | ✅ | 영양제 삭제 |
| `PATCH` | `/api/users/supplements/{id}/status` | ✅ | 복용 여부 토글 |
| `POST` | `/api/users/supplements/scan` | ✅ | 성분표 이미지 OCR 분석 |

#### `GET /api/users/supplements`

**Query Params** `cognito_id`, `is_active` (optional: `true` / `false`)

```json
{
  "supplements": [
    {
      "current_id": 1,
      "cognito_id": "string",
      "product_name": "string",
      "serving_amount": 2,
      "serving_per_day": 1,
      "is_active": true
    }
  ]
}
```

#### `POST /api/users/supplements/scan`

**Request** `multipart/form-data`
- `image`: 이미지 파일 (JPEG / PNG / WEBP, 최대 5MB)
- `cognito_id`: string

```json
{
  "ingredients": [
    { "name": "비타민C", "amount": 500, "unit": "mg" }
  ]
}
```

---

## DB 스키마

`db-sql/userTable.sql` 참고.

| 테이블 | 설명 |
|--------|------|
| `users` | Cognito 유저 (cognito_id PK, email) |
| `user_profile` | 유저 상세 정보 (생년월일, 성별, 키, 몸무게 등) |
| `current_supplements` | 현재 복용 중인 영양제 |
| `user_condition_snapshots` | 건강 상태 스냅샷 |
| `consents` | 약관 동의 내역 |

---

## 인증 방식

### Cognito 환경 (운영)

`COGNITO_USER_POOL_ID` 설정 시 JWKS 엔드포인트에서 공개키를 받아 RS256 토큰 검증.

### 개발 환경 fallback

`COGNITO_USER_POOL_ID` 미설정 시 HS256 방식으로 대체.
`GET /dev/token/{cognito_id}`로 테스트용 토큰 발급 가능.

### 첫 로그인 자동 등록

신규 Cognito 유저가 API를 호출하면 JWT의 `sub`(cognito_id)와 `email` 클레임으로 `users` 테이블에 자동 INSERT된다.

---

## IAM 권한

| 권한 | 용도 |
|------|------|
| `textract:DetectDocumentText` | 영양제 성분표 OCR |
