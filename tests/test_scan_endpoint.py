"""
POST /api/supplements/scan 엔드포인트 통합 테스트

AWS Textract는 unittest.mock.patch로 mock 처리하고
FastAPI TestClient로 HTTP 레벨 동작을 검증합니다.
"""
import io
import pytest
from unittest.mock import patch, AsyncMock, MagicMock

from tests.conftest import app


# ---------------------------------------------------------------------------
# 헬퍼: 가짜 이미지 바이트 생성
# ---------------------------------------------------------------------------

def _make_image(size_bytes: int = 1024, content: bytes = b"\xff\xd8\xff") -> bytes:
    """JPEG 시그니처로 시작하는 가짜 이미지 데이터"""
    return content + b"\x00" * max(0, size_bytes - len(content))


def _make_scan_multipart(image_bytes: bytes, content_type: str = "image/jpeg"):
    """TestClient.post()에 전달할 files + data 튜플 반환"""
    files = {"image": ("test.jpg", io.BytesIO(image_bytes), content_type)}
    data = {"cognito_id": "test-user-001"}
    return files, data


MOCK_TEXTRACT_FULL = """\
제품명: 종근당 오메가3 플러스
1회 섭취량: 2캡슐
1일 섭취횟수: 1회
오메가3지방산 1000mg
EPA(에이코사펜타엔산) 480mg
DHA(도코사헥사엔산) 360mg
비타민E 10mg
"""

MOCK_TEXTRACT_EMPTY = "   "


# ---------------------------------------------------------------------------
# 1. 정상 이미지 업로드 + 파싱 성공
# ---------------------------------------------------------------------------

class TestScanSuccess:
    def test_200_response_on_valid_image(self, client):
        """유효한 이미지 + Textract 정상 반환 → 200 OK"""
        with patch("app.services.scan_service.extract_text", new=AsyncMock(return_value=MOCK_TEXTRACT_FULL)):
            files, data = _make_scan_multipart(_make_image())
            resp = client.post("/api/supplements/scan", files=files, data=data)
        assert resp.status_code == 200

    def test_response_contains_success_true(self, client):
        """응답 JSON에 success: true 포함"""
        with patch("app.services.scan_service.extract_text", new=AsyncMock(return_value=MOCK_TEXTRACT_FULL)):
            files, data = _make_scan_multipart(_make_image())
            resp = client.post("/api/supplements/scan", files=files, data=data)
        assert resp.json()["success"] is True

    def test_response_contains_raw_text(self, client):
        """응답 JSON에 raw_text 필드 포함"""
        with patch("app.services.scan_service.extract_text", new=AsyncMock(return_value=MOCK_TEXTRACT_FULL)):
            files, data = _make_scan_multipart(_make_image())
            resp = client.post("/api/supplements/scan", files=files, data=data)
        body = resp.json()
        assert "raw_text" in body
        assert len(body["raw_text"]) > 0

    def test_response_parsed_has_product_name(self, client):
        """파싱 결과에 제품명 포함"""
        with patch("app.services.scan_service.extract_text", new=AsyncMock(return_value=MOCK_TEXTRACT_FULL)):
            files, data = _make_scan_multipart(_make_image())
            resp = client.post("/api/supplements/scan", files=files, data=data)
        parsed = resp.json()["parsed"]
        assert parsed["ans_product_name"] == "종근당 오메가3 플러스"

    def test_response_confidence_fields_present(self, client):
        """응답에 confidence 객체 및 3개 필드 포함"""
        with patch("app.services.scan_service.extract_text", new=AsyncMock(return_value=MOCK_TEXTRACT_FULL)):
            files, data = _make_scan_multipart(_make_image())
            resp = client.post("/api/supplements/scan", files=files, data=data)
        confidence = resp.json()["confidence"]
        assert "product_name" in confidence
        assert "serving_info" in confidence
        assert "ingredients" in confidence

    def test_response_warnings_is_list(self, client):
        """응답에 warnings 리스트 포함"""
        with patch("app.services.scan_service.extract_text", new=AsyncMock(return_value=MOCK_TEXTRACT_FULL)):
            files, data = _make_scan_multipart(_make_image())
            resp = client.post("/api/supplements/scan", files=files, data=data)
        assert isinstance(resp.json()["warnings"], list)

    def test_png_image_accepted(self, client):
        """PNG 이미지도 정상 처리"""
        with patch("app.services.scan_service.extract_text", new=AsyncMock(return_value=MOCK_TEXTRACT_FULL)):
            files = {"image": ("test.png", io.BytesIO(_make_image()), "image/png")}
            data = {"cognito_id": "test-user-001"}
            resp = client.post("/api/supplements/scan", files=files, data=data)
        assert resp.status_code == 200

    def test_webp_image_accepted(self, client):
        """WEBP 이미지도 정상 처리"""
        with patch("app.services.scan_service.extract_text", new=AsyncMock(return_value=MOCK_TEXTRACT_FULL)):
            files = {"image": ("test.webp", io.BytesIO(_make_image()), "image/webp")}
            data = {"cognito_id": "test-user-001"}
            resp = client.post("/api/supplements/scan", files=files, data=data)
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# 2. 지원하지 않는 파일 형식 → 400
# ---------------------------------------------------------------------------

class TestUnsupportedFileType:
    def test_pdf_returns_400(self, client):
        """PDF 업로드 → 400 Bad Request"""
        files = {"image": ("test.pdf", io.BytesIO(b"%PDF-1.4"), "application/pdf")}
        data = {"cognito_id": "test-user-001"}
        resp = client.post("/api/supplements/scan", files=files, data=data)
        assert resp.status_code == 400

    def test_pdf_error_message(self, client):
        """400 응답에 에러 메시지 포함"""
        files = {"image": ("test.pdf", io.BytesIO(b"%PDF-1.4"), "application/pdf")}
        data = {"cognito_id": "test-user-001"}
        resp = client.post("/api/supplements/scan", files=files, data=data)
        body = resp.json()
        # 글로벌 에러 핸들러 형식: {"error": true, "message": "...", "code": "..."}
        assert body.get("error") is True
        assert "JPEG" in body.get("message", "") or "PNG" in body.get("message", "")

    def test_gif_returns_400(self, client):
        """GIF 업로드 → 400 Bad Request"""
        files = {"image": ("test.gif", io.BytesIO(b"GIF89a"), "image/gif")}
        data = {"cognito_id": "test-user-001"}
        resp = client.post("/api/supplements/scan", files=files, data=data)
        assert resp.status_code == 400

    def test_text_file_returns_400(self, client):
        """텍스트 파일 업로드 → 400 Bad Request"""
        files = {"image": ("test.txt", io.BytesIO(b"hello"), "text/plain")}
        data = {"cognito_id": "test-user-001"}
        resp = client.post("/api/supplements/scan", files=files, data=data)
        assert resp.status_code == 400


# ---------------------------------------------------------------------------
# 3. 5MB 초과 이미지 → 400
# ---------------------------------------------------------------------------

class TestFileSizeLimit:
    def test_over_5mb_returns_400(self, client):
        """5MB 초과 이미지 → 400 Bad Request"""
        over_5mb = _make_image(size_bytes=5 * 1024 * 1024 + 1)
        with patch("app.services.scan_service.extract_text", new=AsyncMock(return_value=MOCK_TEXTRACT_FULL)):
            files, data = _make_scan_multipart(over_5mb)
            resp = client.post("/api/supplements/scan", files=files, data=data)
        assert resp.status_code == 400

    def test_over_5mb_error_message(self, client):
        """5MB 초과 시 에러 메시지에 '5MB' 언급"""
        over_5mb = _make_image(size_bytes=5 * 1024 * 1024 + 1)
        with patch("app.services.scan_service.extract_text", new=AsyncMock(return_value=MOCK_TEXTRACT_FULL)):
            files, data = _make_scan_multipart(over_5mb)
            resp = client.post("/api/supplements/scan", files=files, data=data)
        body = resp.json()
        assert "5MB" in body.get("message", "")

    def test_exactly_5mb_is_accepted(self, client):
        """정확히 5MB는 허용"""
        exactly_5mb = _make_image(size_bytes=5 * 1024 * 1024)
        with patch("app.services.scan_service.extract_text", new=AsyncMock(return_value=MOCK_TEXTRACT_FULL)):
            files, data = _make_scan_multipart(exactly_5mb)
            resp = client.post("/api/supplements/scan", files=files, data=data)
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# 4. Textract 빈 텍스트 반환 → 400
# ---------------------------------------------------------------------------

class TestEmptyTextractResponse:
    def test_empty_text_returns_400(self, client):
        """Textract가 공백만 반환하면 400"""
        with patch("app.services.scan_service.extract_text", new=AsyncMock(return_value=MOCK_TEXTRACT_EMPTY)):
            files, data = _make_scan_multipart(_make_image())
            resp = client.post("/api/supplements/scan", files=files, data=data)
        assert resp.status_code == 400

    def test_empty_text_error_message(self, client):
        """빈 텍스트 에러 메시지에 '텍스트' 포함"""
        with patch("app.services.scan_service.extract_text", new=AsyncMock(return_value=MOCK_TEXTRACT_EMPTY)):
            files, data = _make_scan_multipart(_make_image())
            resp = client.post("/api/supplements/scan", files=files, data=data)
        body = resp.json()
        assert "텍스트" in body.get("message", "")


# ---------------------------------------------------------------------------
# 5. 인증 없이 요청 → 401
# ---------------------------------------------------------------------------

class TestAuthRequired:
    def test_no_token_returns_401(self, client_no_auth):
        """Authorization 헤더 없이 요청 → 401"""
        files, data = _make_scan_multipart(_make_image())
        resp = client_no_auth.post("/api/supplements/scan", files=files, data=data)
        assert resp.status_code == 401

    def test_invalid_token_returns_401(self, db_override):
        """유효하지 않은 토큰 → 401"""
        from fastapi.testclient import TestClient
        tc = TestClient(app)
        files, data = _make_scan_multipart(_make_image())
        resp = tc.post(
            "/api/supplements/scan",
            files=files,
            data=data,
            headers={"Authorization": "Bearer invalid.token.here"},
        )
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# 6. scan 라우트가 /{ans_current_id} 보다 앞에 등록되어 충돌 없음
# ---------------------------------------------------------------------------

class TestRouteOrdering:
    def test_scan_path_not_parsed_as_integer_id(self, client):
        """'scan' 문자열이 /{ans_current_id} 정수 파라미터로 파싱되지 않아야 함.
        만약 라우트 순서가 잘못되면 PUT /api/supplements/scan 이 422를 반환할 수 있음.
        POST /api/supplements/scan 은 200 또는 400(파일 없음)을 반환해야 함 — 422/404는 안 됨."""
        with patch("app.services.scan_service.extract_text", new=AsyncMock(return_value=MOCK_TEXTRACT_FULL)):
            files, data = _make_scan_multipart(_make_image())
            resp = client.post("/api/supplements/scan", files=files, data=data)
        # 라우트 충돌 시 422(validation error)가 발생하므로 이를 명시적으로 배제
        assert resp.status_code != 422
        assert resp.status_code != 404

    def test_integer_supplement_id_route_still_works(self, client):
        """정수 ID 라우트(/api/supplements/123)는 별도로 동작해야 함.
        라우터가 '123'을 정수 ID로 올바르게 해석하여 핸들러에 도달하는지 검증합니다.
        핸들러 로직 오류(500)는 허용하되 라우팅 실패(404/422)는 허용하지 않습니다."""
        from fastapi import HTTPException as FastAPIHTTPException

        # SupplementResponse의 validation_alias 필드명을 사용해야 Pydantic 직렬화 통과
        mock_result = MagicMock()
        mock_result.current_id = 123
        mock_result.cognito_id = "test-user-001"
        mock_result.product_name = "test"
        mock_result.serving_amount = None
        mock_result.serving_per_day = None
        mock_result.daily_total_amount = None
        mock_result.is_active = True
        mock_result.ingredients = None  # validation_alias="ingredients"
        mock_result.created_at = None

        with patch(
            "app.services.user_service.user_service.update_supplement",
            new=AsyncMock(return_value=mock_result),
        ):
            resp = client.put(
                "/api/supplements/123",
                json={"ans_product_name": "test"},
            )
        # 라우터 해석 자체는 성공해야 함 (404/422 아님)
        assert resp.status_code not in (404, 422)
