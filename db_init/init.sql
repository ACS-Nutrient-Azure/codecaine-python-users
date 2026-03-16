-- Users 테이블 (인증 서비스 연동)
CREATE TABLE IF NOT EXISTS "Users" (
    "cognito_id" VARCHAR(36) NOT NULL,
    "email" VARCHAR(255) NOT NULL,
    "created_at" TIMESTAMPTZ DEFAULT NOW(),
    "last_login_at" TIMESTAMPTZ,
    CONSTRAINT "PK_USERS" PRIMARY KEY ("cognito_id")
);

-- user_profile 테이블
CREATE TABLE IF NOT EXISTS "user_profile" (
    "profile_id" BIGSERIAL NOT NULL,
    "cognito_id" VARCHAR(36) NOT NULL,
    "name" VARCHAR(100),
    "birth_dt" DATE,
    "gender" INTEGER,
    "phone" VARCHAR(20),
    "height" NUMERIC(5,1),
    "weight" NUMERIC(5,1),
    "allergies" VARCHAR(255),
    "chron_diseases" VARCHAR(255),
    "created_at" TIMESTAMPTZ DEFAULT NOW(),
    "updated_at" TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT "PK_USER_PROFILE" PRIMARY KEY ("profile_id", "cognito_id"),
    CONSTRAINT "FK_Users_TO_user_profile" FOREIGN KEY ("cognito_id") REFERENCES "Users" ("cognito_id")
);

-- user_condition_snapshots 테이블
CREATE TABLE IF NOT EXISTS "user_condition_snapshots" (
    "snapshot_id" BIGSERIAL NOT NULL,
    "cognito_id" VARCHAR(36) NOT NULL,
    "내 상태 정보" VARCHAR(255),
    "created_at" TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT "PK_USER_CONDITION_SNAPSHOTS" PRIMARY KEY ("snapshot_id", "cognito_id"),
    CONSTRAINT "FK_Users_TO_user_condition_snapshots" FOREIGN KEY ("cognito_id") REFERENCES "Users" ("cognito_id")
);

-- consents 테이블
CREATE TABLE IF NOT EXISTS "consents" (
    "consent_id" BIGSERIAL NOT NULL,
    "cognito_id" VARCHAR(36) NOT NULL,
    "type" VARCHAR(50),
    "agree_dt" DATE,
    CONSTRAINT "PK_CONSENTS" PRIMARY KEY ("consent_id", "cognito_id"),
    CONSTRAINT "FK_Users_TO_consents" FOREIGN KEY ("cognito_id") REFERENCES "Users" ("cognito_id")
);

-- 1-7. 복용중인 영양제 테이블
CREATE TABLE IF NOT EXISTS "1-7. 복용중인 영양제" (
    "current_id" BIGSERIAL NOT NULL,
    "cognito_id" VARCHAR(36) NOT NULL,
    "product_name" VARCHAR(255),
    "serving_amount" INTEGER,
    "serving_per_day" INTEGER,
    "daily_total_amount" INTEGER,
    "total_quantity" INTEGER,
    "is_active" BOOLEAN,
    "ingredients" JSONB,
    "purchased_dt" DATE,
    "estimated_end_dt" DATE,
    "start_dt" DATE,
    "end_dt" DATE,
    "created_at" TIMESTAMPTZ DEFAULT NOW(),
    "updated_at" TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT "PK_current_supplements" PRIMARY KEY ("current_id", "cognito_id"),
    CONSTRAINT "FK_Users_TO_current_supplements" FOREIGN KEY ("cognito_id") REFERENCES "Users" ("cognito_id")
);

-- intake_supplements 테이블
CREATE TABLE IF NOT EXISTS "intake_supplements" (
    "cognito_id" VARCHAR(36) NOT NULL,
    "itk_product_name" VARCHAR(255),
    "itk_serving_amount" INTEGER,
    "itk_serving_per_day" INTEGER,
    "itk_daily_total_amount" INTEGER,
    "itk_total_quantity" INTEGER,
    "is_active" BOOLEAN,
    "itk_purchased_dt" DATE,
    "itk_estimated_end_dt" DATE,
    "created_at" TIMESTAMPTZ DEFAULT NOW(),
    "updated_at" TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT "PK_INTAKE_SUPPLEMENTS" PRIMARY KEY ("cognito_id"),
    CONSTRAINT "FK_Users_TO_intake_supplements" FOREIGN KEY ("cognito_id") REFERENCES "Users" ("cognito_id")
);

-- 테스트용 유저 데이터 삽입
INSERT INTO "Users" ("cognito_id", "email", "created_at")
VALUES ('test-user-001', 'testuser@example.com', NOW())
ON CONFLICT ("cognito_id") DO NOTHING;

INSERT INTO "Users" ("cognito_id", "email", "created_at")
VALUES ('dev-user-001', 'dev@test.com', NOW())
ON CONFLICT ("cognito_id") DO NOTHING;

INSERT INTO "user_profile" ("cognito_id", "name", "birth_dt", "gender", "phone", "height", "weight", "allergies", "chron_diseases")
VALUES ('test-user-001', '테스트유저', '1990-01-10', 0, '010-1234-5678', 175.0, 72.0, '땅콩,새우', '고혈압,당뇨')
ON CONFLICT DO NOTHING;

INSERT INTO "user_profile" ("cognito_id", "name", "birth_dt", "gender", "phone", "height", "weight", "allergies", "chron_diseases")
VALUES ('dev-user-001', '개발자', '1990-01-01', 0, '010-0000-0000', 170.0, 65.0, '', '')
ON CONFLICT DO NOTHING;

INSERT INTO "1-7. 복용중인 영양제" ("cognito_id", "product_name", "serving_amount", "serving_per_day", "daily_total_amount", "total_quantity", "is_active", "purchased_dt", "estimated_end_dt")
VALUES
    ('test-user-001', 'Omega-3 (EPA/DHA)', 1, 1, 1, 60, true, '2024-04-10', '2024-06-10'),
    ('test-user-001', 'Vitamin B Complex', 1, 2, 2, 60, true, '2025-07-01', '2025-08-01'),
    ('test-user-001', 'Vitamin C 1000mg', 1, 1, 1, 30, false, '2024-04-05', '2024-05-05')
ON CONFLICT DO NOTHING;
