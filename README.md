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

---

## 트러블슈팅 히스토리

### 2026-03-09

#### 🐛 페이지 접속 시 "유효하지 않은 토큰" 오류

**원인**
`localStorage`에 이전에 저장된 만료/무효 토큰이 있으면 `getToken()`이 그것을 반환하고, `if (!getToken())` 조건이 `false`가 되어 새 토큰을 발급받지 않음. 해당 토큰으로 API 호출 시 백엔드에서 401 반환.

**수정 내용**
- `frontend/src/app/api.ts`: 401 응답 수신 시 `clearAuth()`로 localStorage 토큰 즉시 삭제
- `frontend/src/app/pages/MyPage.tsx`: 401 에러 감지 시 토큰 재발급 후 자동 재시도

```
// 수정 전: 토큰이 있으면 무조건 사용
if (!getToken()) { fetchDevToken() }

// 수정 후: 401 발생 시 재발급
catch (e) {
  if (e.message === '401') { clearAuth() → fetchDevToken() → 재시도 }
}
```

---

#### 🐛 API-SPEC.md와 구현 불일치

**원인**
초기 구현이 API-SPEC.md와 다른 구조로 개발됨.

**수정 내용 1 - API 경로 변경**

| 구분 | 수정 전 | 수정 후 |
|------|--------|--------|
| prefix | `/api/v1` | `/api` |
| 사용자 조회/수정 | `/users/me` | `/users/{cognito_id}` |
| 영양제 목록 | `/users/me/supplements` | `/supplements?cognito_id=...` |
| 영양제 상태 변경 | `PUT` + `is_active` 필드 | `PATCH /supplements/{id}/status` |

**수정 내용 2 - 응답 필드명 변경**

API-SPEC.md 기준 `ans_` prefix 적용.

| 수정 전 | 수정 후 |
|--------|--------|
| `birth_dt`, `gender`, `height` | `ans_birth_dt`, `ans_gender`, `ans_height` |
| `current_id`, `product_name` | `ans_current_id`, `ans_product_name` |
| `allergies`, `chron_diseases` (배열) | `ans_allergies`, `ans_chron_diseases` (쉼표 구분 문자열) |

**수정 내용 3 - 응답 형식 변경**

| 엔드포인트 | 수정 전 | 수정 후 |
|-----------|--------|--------|
| `PUT /users/{cognito_id}` | 프로필 전체 반환 | `{ success, message }` |
| `POST /supplements` | 영양제 전체 반환 | `{ ans_current_id, success, message }` |
| 에러 응답 | `{ detail: "..." }` | `{ error: true, message, code }` |

**수정 파일 목록**
- `app/api/v1/router.py` — prefix 변경
- `app/api/v1/endpoints/users.py` — 엔드포인트 경로/응답 변경, supplement_router 분리
- `app/schemas/user.py` — `ans_` prefix 스키마, `UserUpdateResponse`, `SupplementCreateResponse` 추가
- `app/services/user_service.py` — DB 필드 ↔ API 필드 매핑, `toggle_supplement_status` 추가
- `app/main.py` — 글로벌 에러 핸들러 추가
- `frontend/src/app/api.ts` — 경로 변경, `clearAuth` / `setCognitoId` 추가
- `frontend/src/app/pages/MyPage.tsx` — 필드명 변경, PUT 후 GET 재조회
- `frontend/src/app/components/MyPageEditModal.tsx` — 필드명 변경

---

#### 🐛 빈 응답 body 파싱 오류 (`Unexpected end of JSON input`)

**원인**
`DELETE /supplements/{id}` 등 응답 body가 없는 엔드포인트에서 `res.json()`을 호출하면 파싱 실패.

**수정 내용**
- `frontend/src/app/api.ts`: `res.json()` → `res.text()` 후 비어있으면 `null` 반환, 있으면 `JSON.parse()`

---

#### 🐛 `MultipleResultsFound` 오류 (500 에러)

**원인**
`user_profile` 테이블에 동일 `cognito_id`로 행이 여러 개 존재할 경우 `scalar_one_or_none()`이 예외 발생.

**수정 내용**
- `app/services/user_service.py`: `scalar_one_or_none()` → `scalars().first()`

---

#### 🔧 DB 연결 변경 (로컬 → 팀 원격 서버)

**내용**
로컬 Docker PostgreSQL에서 팀 공용 원격 서버(`13.125.230.157`)로 변경.

**주의사항**
비밀번호에 포함된 특수문자 `!`는 SQLAlchemy URL에서 `%21`로 URL 인코딩 필요.

```env
# 수정 전
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/mypage_db

# 수정 후
DATABASE_URL=postgresql+asyncpg://vitamin_user:vitamin_user123%21@13.125.230.157:5432/vitamin_user
```

**수정 파일**
- `.env` — DATABASE_URL 변경
