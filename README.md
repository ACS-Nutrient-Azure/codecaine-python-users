# 마이페이지 마이크로서비스

영양제 추천 서비스(MSA)의 마이페이지 담당 서비스입니다.
프론트엔드(React)와 백엔드(FastAPI)를 포함한 풀스택 구성입니다.

## 기술 스택

| 구분 | 기술 |
|------|------|
| **프론트엔드** | React 18, Vite, TypeScript, Tailwind CSS, Radix UI |
| **백엔드** | Python 3.11, FastAPI, SQLAlchemy 2.0 (async) |
| **DB** | PostgreSQL 16 (팀 공용 원격 서버) |
| **인증** | JWT (AWS Cognito 연동 구조) |
| **컨테이너** | Docker, Docker Compose |

## API 목록

| Method | 엔드포인트 | 설명 | 응답 |
|--------|-----------|------|------|
| GET | `/api/users/{cognito_id}` | 마이페이지 정보 조회 | 프로필 전체 |
| PUT | `/api/users/{cognito_id}` | 사용자 정보 수정 | `{ success, message }` |
| DELETE | `/api/users/{cognito_id}` | 회원 탈퇴 | `{ message }` |
| GET | `/api/supplements?cognito_id=...&is_active=...` | 영양제 목록 조회 | `{ supplements: [...] }` |
| POST | `/api/supplements` | 영양제 추가 | `{ ans_current_id, success, message }` |
| PUT | `/api/supplements/{ans_current_id}` | 영양제 수정 | 영양제 정보 |
| DELETE | `/api/supplements/{ans_current_id}` | 영양제 삭제 | 204 No Content |
| PATCH | `/api/supplements/{ans_current_id}/status` | 영양제 활성화/비활성화 | 영양제 정보 |
| GET | `/health` | 헬스체크 | `{ status: "ok" }` |
| GET | `/dev/token/{cognito_id}` | 개발용 JWT 토큰 발급 | `{ access_token }` |

> 모든 API는 `Authorization: Bearer {token}` 헤더 필요
> 에러 응답 형식: `{ "error": true, "message": "...", "code": "..." }`

## 응답 필드명 규칙

API-SPEC.md 기준으로 `ans_` prefix를 사용합니다.

| API 필드명 | DB 컬럼명 | 설명 |
|-----------|----------|------|
| `ans_birth_dt` | `birth_dt` | 생년월일 |
| `ans_gender` | `gender` | 성별 (0=남, 1=여) |
| `ans_height` | `height` | 키 |
| `ans_weight` | `weight` | 체중 |
| `ans_allergies` | `allergies` | 알러지 (쉼표 구분 문자열) |
| `ans_chron_diseases` | `chron_diseases` | 기저질환 (쉼표 구분 문자열) |
| `ans_current_id` | `current_id` | 영양제 ID |
| `ans_product_name` | `product_name` | 영양제명 |
| `ans_is_active` | `is_active` | 복용 여부 |
| `ans_ingredients` | `ingredients` | 성분 (JSONB) |

## 프로젝트 구조

```
svc-mypage/
├── app/                          # 백엔드 (FastAPI)
│   ├── api/v1/
│   │   ├── router.py             # API 라우터 등록 (prefix: /api)
│   │   └── endpoints/
│   │       └── users.py          # 유저 + 영양제 엔드포인트
│   ├── core/
│   │   ├── config.py             # 환경변수 설정 (pydantic-settings)
│   │   └── security.py           # JWT 인증/토큰 생성
│   ├── db/
│   │   └── database.py           # async DB 엔진/세션
│   ├── models/
│   │   ├── user.py               # Users, UserProfile, Consent 모델
│   │   └── supplement.py         # 복용 영양제 모델
│   ├── schemas/
│   │   └── user.py               # Pydantic 요청/응답 스키마 (ans_ prefix)
│   ├── services/
│   │   └── user_service.py       # 비즈니스 로직 (DB 필드 ↔ API 필드 매핑)
│   └── main.py                   # FastAPI 앱 진입점 + 글로벌 에러 핸들러
├── frontend/                     # 프론트엔드 (React + Vite)
│   ├── src/app/
│   │   ├── api.ts                # API 클라이언트 (401 자동 재발급 처리)
│   │   ├── pages/
│   │   │   ├── MyPage.tsx        # 내 정보 관리 (API 연동)
│   │   │   └── ...
│   │   └── components/
│   │       ├── MyPageEditModal.tsx # 내 정보 수정 모달
│   │       └── ...
│   ├── vite.config.ts            # Vite 설정 (/api, /dev 프록시 → localhost:8000)
│   └── package.json
├── Dockerfile
├── docker-compose.yml            # 백엔드 컨테이너
├── requirements.txt
└── .env                          # 환경변수 (git 제외)
```

## DB 연결 정보

팀 공용 원격 PostgreSQL 서버를 사용합니다.

| DB | 용도 | 이 서비스 사용 여부 |
|----|------|-------------------|
| `vitamin_user` | 유저 프로필, 영양제 | ✅ 사용 |
| `vitamin_analysis` | 분석 결과 | ❌ 별도 서비스 |
| `vitamin_history` | 복용 기록 | ❌ 별도 서비스 |
| `http://13.125.230.157:8000` | 챗봇 API | ❌ 별도 서비스 |

`.env` 설정:
```env
DATABASE_URL=postgresql+asyncpg://vitamin_user:vitamin_user123%21@13.125.230.157:5432/vitamin_user
```

> 비밀번호의 `!`는 URL 인코딩 `%21`로 작성해야 합니다.

## DB 스키마 (마이페이지 관련)

| 테이블 | 설명 |
|--------|------|
| `Users` | 유저 기본 정보 (cognito_id, email) |
| `user_profile` | 프로필 상세 (생년월일, 성별, 키, 체중, 알러지, 기저질환) |
| `1-7. 복용중인 영양제` | 현재 복용중인 영양제 목록 |
| `user_condition_snapshots` | 건강 상태 스냅샷 |
| `consents` | 동의 이력 |

## 실행 방법

### 백엔드 (Docker)
```bash
# 백엔드만 실행 (DB는 원격 서버 사용)
docker-compose up mypage-service --build -d
```

### 백엔드 (로컬 직접 실행)
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 프론트엔드
```bash
cd frontend
npm install
npm run dev
```

### 접속 URL
| 용도 | URL |
|------|-----|
| 프론트엔드 | http://localhost:5173 |
| 마이페이지 | http://localhost:5173/my-page |
| API 문서 (Swagger) | http://localhost:8000/docs |

## 인증 (개발 모드)

프론트엔드 접속 시 `/dev/token/test-user-001`에서 JWT 토큰을 자동 발급합니다.
토큰은 `localStorage`에 저장되며, 401 응답 시 자동으로 재발급합니다.

> `APP_ENV=development` 일 때만 동작합니다.
