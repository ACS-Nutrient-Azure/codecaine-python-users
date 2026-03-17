import time
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from typing import NamedTuple

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from app.core.config import settings

bearer_scheme = HTTPBearer()


class CurrentUser(NamedTuple):
    cognito_id: str
    email: str


# ── Cognito JWKS ──────────────────────────────────────────────────────────────

_jwks_cache: dict = {"keys": [], "expires_at": 0.0}
_JWKS_TTL = 3600  # 1시간마다 갱신


def _get_cognito_jwks() -> list:
    now = time.monotonic()
    if now < _jwks_cache["expires_at"] and _jwks_cache["keys"]:
        return _jwks_cache["keys"]
    url = (
        f"https://cognito-idp.{settings.aws_region}.amazonaws.com"
        f"/{settings.cognito_user_pool_id}/.well-known/jwks.json"
    )
    resp = httpx.get(url, timeout=5)
    resp.raise_for_status()
    keys = resp.json()["keys"]
    _jwks_cache["keys"] = keys
    _jwks_cache["expires_at"] = now + _JWKS_TTL
    return keys


def _verify_cognito_token(token: str) -> dict:
    keys = _get_cognito_jwks()
    headers = jwt.get_unverified_headers(token)
    key = next((k for k in keys if k["kid"] == headers.get("kid")), None)
    if not key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token key")
    payload = jwt.decode(
        token,
        key,
        algorithms=["RS256"],
        audience=settings.cognito_client_id,
    )
    return payload


# ── Dev fallback (HS256) ───────────────────────────────────────────────────────

def create_test_token(cognito_id: str) -> str:
    """개발환경 전용 — Cognito 미설정 시 HS256 토큰 발급"""
    payload = {
        "sub": cognito_id,
        "exp": datetime.now(timezone.utc) + timedelta(hours=24),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm="HS256")


def _verify_dev_token(token: str) -> dict:
    if not settings.jwt_secret_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="JWT_SECRET_KEY가 설정되지 않았습니다.")
    try:
        return jwt.decode(token, settings.jwt_secret_key, algorithms=["HS256"])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="유효하지 않은 토큰입니다.")


# ── Public dependency ─────────────────────────────────────────────────────────

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> CurrentUser:
    token = credentials.credentials

    if settings.cognito_user_pool_id:
        try:
            payload = _verify_cognito_token(token)
        except Exception as e:
            import logging
            logging.getLogger(__name__).error("[AUTH] Cognito 검증 실패: %s", e, exc_info=True)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="유효하지 않은 토큰입니다.")
    else:
        payload = _verify_dev_token(token)

    cognito_id: str = payload.get("sub")
    if not cognito_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="토큰에 사용자 정보가 없습니다.")

    email: str = payload.get("email", "")
    return CurrentUser(cognito_id=cognito_id, email=email)


async def get_current_user_id(
    current_user: CurrentUser = Depends(get_current_user),
) -> str:
    return current_user.cognito_id
