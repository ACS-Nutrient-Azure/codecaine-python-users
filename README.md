# MyPage 서비스

사용자 프로필, 영양제 목록 관리, 영양제 성분표 OCR 스캔, 건강검진/처방기록 조회(CODEF)를 담당하는 FastAPI 마이크로서비스.
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
| 외부 API | CODEF (건강보험공단 건강검진/처방기록 조회) |
| 스토리지 | AWS S3 (CODEF 원본 데이터 저장) |

---

## Docker 로컬 실행 (권장)

`docker-compose.yml`이 `codecaine-python-mypage` 루트에 있으며, `../source-frontend` 프론트엔드와 함께 3-서비스 스택으로 실행된다.

```bash
cd codecaine-python-mypage
docker compose up --build
```

| 서비스 | 포트 | 설명 |
|--------|------|------|
| frontend | 5173 → 8080 | nginx + Vite 빌드 결과물 |
| mypage-service | 8003 | FastAPI 백엔드 |
| db | 5432 | PostgreSQL (로컬 개발용) |

> **참고** 실제 환경에서는 `.env`의 `DATABASE_URL`을 외부 DB로 설정한다. `docker-compose.yml`의 `environment` 섹션에 `DATABASE_URL`을 넣으면 `.env` 값이 덮어씌워지므로 주의.

---

## 직접 실행

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env   # .env 값 입력
uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload
```

> **Windows 주의** `source` 명령은 Linux/macOS 전용이다. Windows에서는 `.venv\Scripts\activate`를 사용할 것.

---

## 환경변수 (`.env`)

```env
# PostgreSQL
DATABASE_URL=postgresql+asyncpg://<user>:<password>@<host>:5432/<db>

# AWS Cognito (JWT 검증용)
COGNITO_USER_POOL_ID=<User Pool ID>
COGNITO_CLIENT_ID=<App Client ID>
AWS_REGION=ap-northeast-2

# AWS (Textract OCR, S3 사용 시)
AWS_ACCESS_KEY_ID=<IAM Access Key>
AWS_SECRET_ACCESS_KEY=<IAM Secret Key>
S3_BUCKET_NAME=<버킷명>

# CODEF (건강보험공단 API)
CODEF_CLIENT_ID=<CODEF Client ID>
CODEF_CLIENT_SECRET=<CODEF Client Secret>

# CORS
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

### CODEF 크리덴셜 발급

1. [CODEF 개발자 포털](https://developer.codef.io) 계정 생성
2. 앱 등록 후 `client_id` / `client_secret` 발급
3. Base64 인코딩 확인: `echo -n "client_id:client_secret" | base64`
4. 토큰 발급 테스트:
   ```bash
   curl -X POST 'https://oauth.codef.io/oauth/token?grant_type=client_credentials&scope=read' \
     -H 'Authorization: Basic <Base64(client_id:client_secret)>'
   ```

---

## 프로젝트 구조

```
app/
├── main.py
├── api/
│   ├── router.py
│   └── endpoints/
│       ├── users.py       # 프로필 + 영양제
│       ├── history.py     # 복용 기록
│       └── codef.py       # 건강검진 / 처방기록 (CODEF)
├── core/
│   ├── config.py          # pydantic-settings 환경변수
│   └── security.py        # JWT 검증 (Cognito RS256 / dev HS256 fallback)
├── db/
│   └── database.py
├── models/
│   ├── user.py
│   └── supplement.py
├── schemas/
│   ├── user.py
│   └── codef.py           # CodefUserInfo, CodefInitResponse, CodefFetchRequest
│                          # CodefPrescInitResponse, CodefPrescFetchRequest
└── services/
    ├── user_service.py
    ├── scan_service.py    # Textract OCR
    ├── codef_service.py   # CODEF API 호출 + 데이터 파싱
    └── s3_service.py      # S3 업로드 / 다운로드
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

### CODEF (건강보험공단 연동)

| 메서드 | 경로 | 인증 | 설명 |
|--------|------|------|------|
| `POST` | `/api/users/codef/init` | ✅ | 건강검진 카카오 인증 요청 (1단계) |
| `POST` | `/api/users/codef/fetch` | ✅ | 건강검진 데이터 조회 (2단계) |
| `POST` | `/api/users/codef/presc-init` | ✅ | 처방기록 카카오 인증 요청 (1단계) |
| `POST` | `/api/users/codef/presc-fetch` | ✅ | 처방기록 데이터 조회 (2단계) |
| `GET` | `/api/users/codef/health-data/{cognito_id}` | ✅ | S3에 저장된 건강 요약 조회 |

#### CODEF 플로우 — 건강검진 (1차 인증)

```
1. POST /api/users/codef/init
   입력: user_name, phone_no, identity(생년월일 YYYYMMDD), nhis_id(주민번호 SHA256 해시)
   처리: CODEF OAuth 토큰 발급 → 건강검진 카카오 인증 요청
         연도 범위 자동 계산 (최근 5년: current_year-4 ~ current_year)
   반환: health_check_two_way, token, hc_start_year, hc_end_year

2. 사용자가 카카오 앱에서 인증 완료

3. POST /api/users/codef/fetch
   입력: init 응답값 전체 + cognito_id
   처리: 건강검진 결과 조회 → S3 저장 (codef_hc_raw.json, health_summary.json)
   반환: exam_items(검진 수치), health_summary(키/몸무게/검진일)
```

#### CODEF 플로우 — 처방기록 (2차 인증, 별도)

> **설계 결정**: CODEF API는 건강검진과 처방기록을 별개 API로 제공하며, 각각 독립적인 카카오 인증이 필요하다.
> 하나의 카카오 인증으로 두 API를 동시에 조회하는 것은 불가능하다.

```
1. POST /api/users/codef/presc-init
   입력: user_name, phone_no, identity, nhis_id
   처리: CODEF OAuth 토큰 발급 → 처방기록 카카오 인증 요청
         날짜 범위 자동 계산 (전년도 1월 1일 ~ 오늘)
   반환: prescription_two_way, token, presc_start, presc_end

2. 사용자가 카카오 앱에서 인증 완료

3. POST /api/users/codef/presc-fetch
   입력: presc-init 응답값 전체 + cognito_id
   처리: 처방기록 조회 → S3 저장 (codef_presc_raw.json)
   반환: medications(처방약 목록), success: true
```

> **주의** 2-way 인증은 init 요청과 fetch 요청의 파라미터(날짜 범위 포함)가 완전히 동일해야 한다.

---

## DB 스키마

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

> **주의** `COGNITO_USER_POOL_ID`가 설정된 상태에서 dev 토큰(HS256)으로 요청하면 401 반환.

### 첫 로그인 자동 등록

신규 Cognito 유저가 API를 호출하면 JWT의 `sub`(cognito_id)와 `email` 클레임으로 `users` 테이블에 자동 INSERT된다.

---

## IAM 권한

| 권한 | 용도 |
|------|------|
| `textract:DetectDocumentText` | 영양제 성분표 OCR |
| `s3:PutObject`, `s3:GetObject` | CODEF 원본 데이터 및 건강 요약 저장 |

---

## 트러블슈팅

### Docker 빌드 시 `vite: not found`

**원인**: Windows에서 `node_modules`가 존재하면 `COPY . .` 단계에서 Windows 바이너리가 Linux 컨테이너 안으로 복사됨.
**해결**: `source-frontend/.dockerignore`에 `node_modules`, `dist`, `.vite` 추가.

### nginx `host not found in upstream`

**원인**: `nginx.conf`의 `proxy_pass` 호스트명이 docker-compose 서비스명과 불일치.
**해결**: `proxy_pass` 대상을 docker-compose 서비스명(`mypage-service`)으로 통일.

### 모든 API 요청에서 403

**원인**: Cognito 토큰 검증 실패 → `clearAuth()` 호출로 토큰 삭제 → 이후 요청에 Authorization 헤더 없음 → `HTTPBearer`가 403 반환.
**해결**: docker-compose `environment`에 `COGNITO_USER_POOL_ID`, `COGNITO_CLIENT_ID` 추가.

### 프론트엔드 흰 화면

**원인**: 빌드 타임에 `VITE_COGNITO_*` 환경변수가 undefined → `CognitoUserPool` 생성자 오류.
**해결**: `source-frontend/Dockerfile`에 `ARG`/`ENV` 추가, docker-compose `build.args`에 실제 Cognito 값 전달.

### `relation "users" does not exist`

**원인**: SQLAlchemy 모델의 `__tablename__` 대소문자와 실제 DB 스키마 불일치.
**해결**: 외부 DB의 실제 테이블명(소문자 `users`)에 맞춰 모델 수정.

### `DATABASE_URL` 외부 DB 무시

**원인**: docker-compose `environment` 섹션에 `DATABASE_URL` 하드코딩 → `.env` 파일 값 덮어씌움.
**해결**: docker-compose `environment`에서 `DATABASE_URL` 제거, `.env`에서만 관리.

### `pip install -r requirements.txt` UnicodeDecodeError (Windows)

**원인**: `requirements.txt`에 한글 주석이 포함된 경우 Windows 기본 인코딩(cp949)에서 읽기 실패.
**해결**: `requirements.txt`에서 한글 주석 제거.

### `POST /api/users/codef/init` 500 에러

**원인**: `.env`에 `CODEF_CLIENT_ID` / `CODEF_CLIENT_SECRET` 미설정 → OAuth 토큰 발급 실패.
**해결**: CODEF 개발자 포털에서 발급한 크리덴셜을 `.env`에 추가 후 컨테이너 재시작.

### CODEF 건강검진 기록이 표시되지 않음

**원인**: `searchStartYear`와 `searchEndYear`를 모두 현재 연도로 고정 → 이전 연도 기록 누락.
**해결**: 백엔드에서 현재 연도 기준 최근 5년 범위 자동 계산 (`current_year - 4` ~ `current_year`).

### CODEF에서 가장 오래된 검진 결과가 표시됨

**원인**: CODEF API 응답 배열이 연도 오름차순 → `exam_list[0]`이 가장 오래된 결과.
**해결**: `resCheckupYear` / `resCheckupDate` 기준 내림차순 정렬 후 첫 번째 항목 사용.

### CODEF 처방기록 `prescription_two_way.jti` 가 비어있음 / 타임아웃

**원인**: 건강검진(`nhis-health-checkup`)과 처방기록(`nhis-treatment`) API는 각각 독립적인 카카오 인증이 필요하다. 카카오 인증은 1회만 발송되므로 하나의 인증으로 두 API를 동시에 조회할 수 없다.
**해결**: 건강검진과 처방기록 인증을 분리 (`/codef/init` + `/codef/fetch` / `/codef/presc-init` + `/codef/presc-fetch`).

### CODEF CF-13001 에러 (날짜 범위 오류)

**원인**: 처방기록 API의 `endDate`에 미래 날짜(예: `20261231`) 전달.
**해결**: `endDate`를 오늘 날짜(`date.today().strftime("%Y%m%d")`)로 설정.

### CODEF 처방기록 응답 파싱 실패 (`'list' object has no attribute 'get'`)

**원인**: `nhis-treatment` API의 `data` 필드가 dict가 아닌 list로 반환됨. 약품명 필드도 `resProductName`이 아닌 `resPrescribeDrugName`을 사용.
**해결**: `parse_prescription`에서 `data["data"]`가 list인 경우 방어 처리 및 `resPrescribeDrugName` 필드 추가.

### `sqlalchemy.exc.MultipleResultsFound` (이메일 중복)

**원인**: DB에 동일 email을 가진 cognito_id가 여러 개 존재.
**해결**: 중복 레코드를 정리하는 스크립트 실행 (자식 테이블 먼저 삭제 후 `users` 삭제).
```sql
-- 중복 확인
SELECT email, COUNT(*) FROM users GROUP BY email HAVING COUNT(*) > 1;
```
