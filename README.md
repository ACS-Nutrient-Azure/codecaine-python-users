# 마이페이지 마이크로서비스

영양제 추천 서비스(MSA)의 마이페이지 담당 서비스입니다.
프론트엔드(React)와 백엔드(FastAPI)를 포함한 풀스택 구성입니다.

## 기술 스택

| 구분 | 기술 |
|------|------|
| **프론트엔드** | React 18, Vite, TypeScript, Tailwind CSS, Radix UI |
| **백엔드** | Python 3.11, FastAPI, SQLAlchemy 2.0 (async) |
| **DB** | PostgreSQL 16 (로컬: Docker / 운영: AWS RDS) |
| **인증** | JWT (AWS Cognito 연동 구조) |
| **컨테이너** | Docker, Docker Compose |

## API 목록

| Method | 엔드포인트 | 설명 |
|--------|-----------|------|
| GET | `/api/v1/users/me` | 내 프로필 조회 |
| PUT | `/api/v1/users/me` | 프로필 수정 (이름, 생년월일, 성별, 연락처, 키, 체중, 알러지, 기저질환) |
| DELETE | `/api/v1/users/me` | 회원 탈퇴 |
| GET | `/api/v1/users/me/supplements` | 복용 영양제 목록 조회 |
| POST | `/api/v1/users/me/supplements` | 영양제 추가 |
| PUT | `/api/v1/users/me/supplements/{id}` | 영양제 수정 |
| DELETE | `/api/v1/users/me/supplements/{id}` | 영양제 삭제 |
| GET | `/health` | 헬스체크 (AWS ALB용) |
| GET | `/dev/token/{cognito_id}` | 개발용 JWT 토큰 발급 |

## 프로젝트 구조

```
svc-mypage/
├── app/                          # 백엔드 (FastAPI)
│   ├── api/v1/
│   │   ├── router.py             # API 라우터 등록
│   │   └── endpoints/
│   │       └── users.py          # 유저/영양제 API 엔드포인트
│   ├── core/
│   │   ├── config.py             # 환경변수 설정 (pydantic-settings)
│   │   └── security.py           # JWT 인증/토큰 생성
│   ├── db/
│   │   └── database.py           # async DB 엔진/세션
│   ├── models/
│   │   ├── user.py               # Users, UserProfile, Consent 모델
│   │   └── supplement.py         # 복용 영양제 모델
│   ├── schemas/
│   │   └── user.py               # Pydantic 요청/응답 스키마
│   ├── services/
│   │   └── user_service.py       # 비즈니스 로직
│   └── main.py                   # FastAPI 앱 진입점
├── frontend/                     # 프론트엔드 (React + Vite)
│   ├── src/app/
│   │   ├── api.ts                # API 클라이언트 (fetch 기반)
│   │   ├── pages/
│   │   │   ├── MyPage.tsx        # 내 정보 관리 (API 연동)
│   │   │   ├── Recommendation.tsx # 분석하기 (프로필 연동)
│   │   │   └── ...
│   │   └── components/
│   │       ├── MyPageEditModal.tsx # 내 정보 수정 모달 (API 연동)
│   │       └── ...
│   ├── vite.config.ts            # Vite 설정 (API 프록시 포함)
│   └── package.json
├── db_init/
│   └── init.sql                  # DB 초기화 (테이블 생성 + 테스트 데이터)
├── Dockerfile
├── docker-compose.yml            # 백엔드 + PostgreSQL
├── requirements.txt
├── .env.example
└── .env                          # 로컬 환경변수 (git 제외)
```

## DB 스키마 (마이페이지 관련)

| 테이블 | 설명 |
|--------|------|
| `Users` | 유저 기본 정보 (cognito_id, email) |
| `user_profile` | 프로필 상세 (이름, 생년월일, 성별, 키, 체중, 알러지, 기저질환) |
| `1-7. 복용중인 영양제` | 현재 복용중인 영양제 목록 |
| `user_condition_snapshots` | 건강 상태 스냅샷 |
| `consents` | 동의 이력 |

## 로컬 실행 방법

```bash
# 1. 백엔드 + DB 실행 (Docker)
docker-compose up --build -d

# 2. 프론트엔드 실행 (별도 터미널)
cd frontend
npm install
npm run dev

# 3. 브라우저 접속
#    프론트엔드: http://localhost:5173
#    마이페이지: http://localhost:5173/my-page
#    분석하기:   http://localhost:5173/recommendation
#    API 문서:   http://localhost:8000/docs
```

## 테스트 데이터

Docker 실행 시 `db_init/init.sql`이 자동 실행되어 아래 테스트 데이터가 삽입됩니다:

- **유저**: `test-user-001` / `testuser@example.com`
- **프로필**: 테스트유저, 1990-01-10, 남성, 175cm, 72kg, 알러지(땅콩,새우), 기저질환(고혈압,당뇨)
- **영양제**: Omega-3, Vitamin B Complex, Vitamin C 1000mg

프론트엔드 접속 시 자동으로 개발용 JWT 토큰이 발급되어 로그인 없이 테스트할 수 있습니다.

## 서비스 종료

```bash
# 컨테이너 중지 (데이터 유지)
docker-compose down

# 컨테이너 + DB 데이터 삭제
docker-compose down -v
```
