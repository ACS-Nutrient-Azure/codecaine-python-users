-- ============================================================
-- codecaine-python-users 서비스 전체 DB 초기화 스크립트
-- PostgreSQL (TIMESTAMPTZ, JSONB, BIGSERIAL)
-- ============================================================

-- ============================================================
-- 1. 인증 / 유저
-- ============================================================

-- 유저 (AWS Cognito 연동)
CREATE TABLE IF NOT EXISTS users (
    cognito_id  VARCHAR(36)  NOT NULL,
    email       VARCHAR(255) NOT NULL,
    created_at  TIMESTAMPTZ  DEFAULT NOW(),
    last_login_at TIMESTAMPTZ,
    CONSTRAINT pk_users PRIMARY KEY (cognito_id),
    CONSTRAINT uq_users_email UNIQUE (email)
);

-- 유저 프로필
CREATE TABLE IF NOT EXISTS user_profile (
    profile_id    BIGSERIAL    NOT NULL,
    cognito_id    VARCHAR(36)  NOT NULL,
    name          VARCHAR(100),
    birth_dt      DATE,
    gender        INTEGER,            -- 0: 남, 1: 여
    phone         VARCHAR(20),
    height        NUMERIC(5,1),
    weight        NUMERIC(5,1),
    allergies     VARCHAR(255),
    chron_diseases VARCHAR(255),
    created_at    TIMESTAMPTZ  DEFAULT NOW(),
    updated_at    TIMESTAMPTZ  DEFAULT NOW(),
    CONSTRAINT pk_user_profile PRIMARY KEY (profile_id),
    CONSTRAINT fk_user_profile_users FOREIGN KEY (cognito_id) REFERENCES users (cognito_id) ON DELETE CASCADE
);

-- 유저 상태 스냅샷
CREATE TABLE IF NOT EXISTS user_condition_snapshots (
    snapshot_id BIGSERIAL   NOT NULL,
    cognito_id  VARCHAR(36) NOT NULL,
    status      VARCHAR(255),          -- 유저 현재 상태 정보
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT pk_user_condition_snapshots PRIMARY KEY (snapshot_id),
    CONSTRAINT fk_user_condition_snapshots_users FOREIGN KEY (cognito_id) REFERENCES users (cognito_id) ON DELETE CASCADE
);

-- 동의 내역
CREATE TABLE IF NOT EXISTS consents (
    consent_id BIGSERIAL   NOT NULL,
    cognito_id VARCHAR(36) NOT NULL,
    type       VARCHAR(50),           -- 동의 유형 (예: marketing, privacy)
    agree_dt   DATE,
    CONSTRAINT pk_consents PRIMARY KEY (consent_id),
    CONSTRAINT fk_consents_users FOREIGN KEY (cognito_id) REFERENCES users (cognito_id) ON DELETE CASCADE
);

-- ============================================================
-- 2. 영양제 복용 관리
-- ============================================================

-- 현재 복용 중인 영양제 (메인 DB)
CREATE TABLE IF NOT EXISTS current_supplements (
    current_id          BIGSERIAL    NOT NULL,
    cognito_id          VARCHAR(36)  NOT NULL,
    product_name        VARCHAR(255),
    serving_amount      INTEGER,                   -- 1회 복용량(정/캡슐 수)
    serving_per_day     INTEGER,                   -- 하루 복용 횟수
    daily_total_amount  INTEGER,                   -- 하루 총 복용량
    total_quantity      INTEGER,                   -- 총 수량
    is_active           BOOLEAN,
    ingredients         JSONB,                     -- { 성분명: 함량 } 딕셔너리
    purchased_dt        DATE,
    estimated_end_dt    DATE,
    start_dt            DATE,
    end_dt              DATE,
    created_at          TIMESTAMPTZ  DEFAULT NOW(),
    updated_at          TIMESTAMPTZ  DEFAULT NOW(),
    CONSTRAINT pk_current_supplements PRIMARY KEY (current_id),
    CONSTRAINT fk_current_supplements_users FOREIGN KEY (cognito_id) REFERENCES users (cognito_id) ON DELETE CASCADE
);

-- 영양제 성분 상세 (current_supplements.ingredients JSONB 보완용)
CREATE TABLE IF NOT EXISTS current_ingredients (
    ingredient_id   BIGSERIAL    NOT NULL,
    current_id      BIGINT       NOT NULL,         -- current_supplements 참조
    ingredient_name VARCHAR(255),
    nutrient_amount INTEGER,
    created_at      TIMESTAMPTZ  DEFAULT NOW(),
    CONSTRAINT pk_current_ingredients PRIMARY KEY (ingredient_id),
    CONSTRAINT fk_current_ingredients_supplement FOREIGN KEY (current_id) REFERENCES current_supplements (current_id) ON DELETE CASCADE
);

-- ============================================================
-- 3. CODEF 외부 건강 데이터 연동
-- ============================================================

-- 외부 건강 데이터 임포트 요청 이력
CREATE TABLE IF NOT EXISTS external_healthcheck_import (
    import_id    BIGSERIAL    NOT NULL,
    cognito_id   VARCHAR(36)  NOT NULL,
    api_kind     VARCHAR(50),                      -- healthcheck / rx_prescription
    source_s3_url TEXT,                            -- 원본 데이터 S3 경로
    exprires_at  TIMESTAMPTZ,                      -- 1개월 후 삭제 (컬럼명 오타 모델과 동일하게 유지)
    created_at   TIMESTAMPTZ  DEFAULT NOW(),
    CONSTRAINT pk_external_healthcheck_import PRIMARY KEY (import_id),
    CONSTRAINT fk_external_healthcheck_import_users FOREIGN KEY (cognito_id) REFERENCES users (cognito_id) ON DELETE CASCADE
);

-- CODEF API 호출 로그
CREATE TABLE IF NOT EXISTS codef_api_call_log (
    log_id            BIGSERIAL    NOT NULL,
    import_id         BIGINT       NOT NULL,
    cognito_id        VARCHAR(36)  NOT NULL,
    api_kind          VARCHAR(50),                 -- healthcheck / rx_prescription
    agred_dt          DATE,                        -- 동의 일자 (컬럼명 오타 모델과 동일하게 유지)
    phone_hash        VARCHAR(64),                 -- SHA-256 해시 암호화된 전화번호
    codef_request_id  VARCHAR(255),               -- CODEF requestID / transactionID
    status            BOOLEAN,                     -- TRUE = 성공
    expires_at        TIMESTAMPTZ,                 -- 3년 보관 후 삭제
    created_at        TIMESTAMPTZ  DEFAULT NOW(),
    updated_at        TIMESTAMPTZ  DEFAULT NOW(),
    CONSTRAINT pk_codef_api_call_log PRIMARY KEY (log_id),
    CONSTRAINT fk_codef_api_call_log_import FOREIGN KEY (import_id) REFERENCES external_healthcheck_import (import_id) ON DELETE CASCADE
);

-- 처방전 / 건강검진 수치 데이터
DROP TABLE IF EXISTS prescription_medications CASCADE;
CREATE TABLE prescription_medications (
    med_id          BIGSERIAL    NOT NULL,
    import_id       BIGINT       NOT NULL,
    cognito_id      VARCHAR(36)  NOT NULL,
    api_kind        VARCHAR(50),                   -- healthcheck / rx_prescription
    data_type       VARCHAR(50),                   -- drug / blood_pressure / cholesterol / glucose 등
    name            VARCHAR(255),                  -- 약품명 또는 검진 항목명
    value           VARCHAR(255),                  -- 복용량(예: "100mg 1T") 또는 측정값(예: "140")
    unit            VARCHAR(20),                   -- mg / mmHg / mg/dL 등
    period_start_dt DATE,
    period_end_dt   DATE,
    expires_at      TIMESTAMPTZ,                   -- 1개월 후 삭제
    created_at      TIMESTAMPTZ  DEFAULT NOW(),
    updated_at      TIMESTAMPTZ  DEFAULT NOW(),
    CONSTRAINT pk_prescription_medications PRIMARY KEY (med_id),
    CONSTRAINT fk_prescription_medications_import FOREIGN KEY (import_id) REFERENCES external_healthcheck_import (import_id) ON DELETE CASCADE
);

-- ============================================================
-- 4. 참조 테이블
-- ============================================================

-- 단위 변환 기준 (µg ↔ mg 등)
CREATE TABLE IF NOT EXISTS unit_convertor (
    vitamin_name  VARCHAR(255)  NOT NULL,          -- 비타민/영양소명
    convert_unit  NUMERIC(12,8),                   -- 변환 계수 (예: 0.00100000)
    CONSTRAINT pk_unit_convertor PRIMARY KEY (vitamin_name)
);

-- ============================================================
-- 5. 인덱스
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_user_profile_cognito_id         ON user_profile (cognito_id);
CREATE INDEX IF NOT EXISTS idx_user_condition_snapshots_cognito ON user_condition_snapshots (cognito_id);
CREATE INDEX IF NOT EXISTS idx_consents_cognito_id              ON consents (cognito_id);
CREATE INDEX IF NOT EXISTS idx_current_supplements_cognito_id   ON current_supplements (cognito_id);
CREATE INDEX IF NOT EXISTS idx_current_supplements_is_active    ON current_supplements (cognito_id, is_active);
CREATE INDEX IF NOT EXISTS idx_current_ingredients_current_id   ON current_ingredients (current_id);
CREATE INDEX IF NOT EXISTS idx_ext_healthcheck_cognito_id       ON external_healthcheck_import (cognito_id);
CREATE INDEX IF NOT EXISTS idx_codef_log_import_id              ON codef_api_call_log (import_id);
CREATE INDEX IF NOT EXISTS idx_prescription_med_import_id       ON prescription_medications (import_id);

-- ============================================================
-- 6. 테스트 데이터
-- ============================================================

INSERT INTO users (cognito_id, email, created_at)
VALUES
    ('test-user-001', 'testuser@example.com', NOW()),
    ('dev-user-001',  'dev@test.com',         NOW())
ON CONFLICT (cognito_id) DO NOTHING;

INSERT INTO user_profile (cognito_id, name, birth_dt, gender, phone, height, weight, allergies, chron_diseases)
VALUES
    ('test-user-001', '테스트유저', '1990-01-10', 0, '010-1234-5678', 175.0, 72.0, '땅콩,새우', '고혈압,당뇨'),
    ('dev-user-001',  '개발자',    '1990-01-01', 0, '010-0000-0000', 170.0, 65.0, '',         '')
ON CONFLICT DO NOTHING;

INSERT INTO current_supplements (cognito_id, product_name, serving_amount, serving_per_day, daily_total_amount, total_quantity, is_active, ingredients, purchased_dt, estimated_end_dt)
VALUES
    ('test-user-001', 'Omega-3 (EPA/DHA)',  1, 1, 1, 60, true,  '{"EPA": 300, "DHA": 200}', '2024-04-10', '2024-06-10'),
    ('test-user-001', 'Vitamin B Complex',  1, 2, 2, 60, true,  '{"비타민B1": 1, "비타민B6": 1, "비타민B12": 2}', '2025-07-01', '2025-08-01'),
    ('test-user-001', 'Vitamin C 1000mg',   1, 1, 1, 30, false, '{"비타민C": 1000}', '2024-04-05', '2024-05-05')
ON CONFLICT DO NOTHING;

INSERT INTO unit_convertor (vitamin_name, convert_unit)
VALUES
    ('비타민D',  0.02500000),   -- IU → µg (1 IU = 0.025 µg)
    ('비타민A',  0.30000000),   -- IU → µg RE
    ('비타민E',  0.67000000)    -- IU → mg α-TE
ON CONFLICT (vitamin_name) DO NOTHING;
