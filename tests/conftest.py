"""
pytest 공통 픽스처 및 테스트 환경 설정

주요 처리:
  - .env 없이 테스트 가능하도록 환경변수 강제 설정 (Settings 로딩 전)
  - Python 3.14에서 사라진 pkg_resources를 sys.modules로 stub
  - OpenTelemetry instrumentation 및 DB engine 생성을 sys.modules/mock으로 bypass
  - 인증 의존성(get_current_user_id)을 bypass하는 픽스처 제공
"""
import os
import sys
from unittest.mock import MagicMock, AsyncMock, patch

# ── 1. 필수 환경변수 (Settings 로딩 전 설정) ──────────────────────────────
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost:5432/test_db")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-unit-tests-only")
os.environ.setdefault("APP_ENV", "development")
os.environ.setdefault("AWS_ACCESS_KEY_ID", "test-key")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "test-secret")

# ── 2. pkg_resources stub (Python 3.14에서 제거됨) ───────────────────────
if "pkg_resources" not in sys.modules:
    sys.modules["pkg_resources"] = MagicMock()

# ── 3. opentelemetry 전체 stub (Python 3.14와 호환되지 않는 C 확장 우회) ──
# grpcio/protobuf/pkg_resources 의존 모듈을 모두 sys.modules로 차단
_otel_modules_to_stub = [
    "opentelemetry.instrumentation.sqlalchemy",
    "opentelemetry.instrumentation.fastapi",
    "opentelemetry.instrumentation.httpx",
    "opentelemetry.exporter.otlp.proto.grpc",
    "opentelemetry.exporter.otlp.proto.grpc.metric_exporter",
    "opentelemetry.exporter.otlp.proto.grpc.trace_exporter",
    "opentelemetry.exporter.otlp.proto.common",
    "opentelemetry.exporter.otlp.proto.common.metrics_encoder",
    "opentelemetry.exporter.otlp.proto.common._internal",
    "opentelemetry.exporter.otlp.proto.common._internal.metrics_encoder",
    "opentelemetry.proto",
    "opentelemetry.proto.common",
    "opentelemetry.proto.common.v1",
    "opentelemetry.proto.common.v1.common_pb2",
    "google.protobuf",
    "google.protobuf.descriptor",
    "google.protobuf.internal",
    "google.protobuf.internal.api_implementation",
    "grpc",
    "grpcio",
    "google._upb._message",
]
for _mod in _otel_modules_to_stub:
    if _mod not in sys.modules:
        sys.modules[_mod] = MagicMock()

# telemetry 모듈 자체를 stub으로 대체 (setup_telemetry가 no-op이 되도록)
_telemetry_stub = MagicMock()
_telemetry_stub.setup_telemetry = lambda: None
sys.modules["app.core.telemetry"] = _telemetry_stub

# ── 4. DB engine stub (asyncpg 연결 없이 동작) ───────────────────────────
_engine_mock = MagicMock()
_engine_mock.sync_engine = MagicMock()

_create_engine_patcher = patch(
    "sqlalchemy.ext.asyncio.create_async_engine",
    return_value=_engine_mock,
)
_create_engine_patcher.start()

# ── 5. app 임포트 (위 stub이 모두 적용된 후) ──────────────────────────────
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.security import get_current_user_id
from app.db.database import get_db


# ── 6. 공통 픽스처 ───────────────────────────────────────────────────────

@pytest.fixture
def auth_override():
    """get_current_user_id 의존성을 'test-user-001' 고정값으로 대체"""
    async def _fake_user():
        return "test-user-001"
    app.dependency_overrides[get_current_user_id] = _fake_user
    yield
    app.dependency_overrides.pop(get_current_user_id, None)


@pytest.fixture
def db_override():
    """DB 세션 의존성을 AsyncMock으로 대체"""
    async def _fake_db():
        yield AsyncMock()
    app.dependency_overrides[get_db] = _fake_db
    yield
    app.dependency_overrides.pop(get_db, None)


@pytest.fixture
def client(auth_override, db_override):
    """인증 + DB를 mock한 TestClient"""
    return TestClient(app)


@pytest.fixture
def client_no_auth(db_override):
    """인증 없는 TestClient (401 테스트용)"""
    return TestClient(app)
