from datetime import datetime
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt

from app.core.config import settings

bearer_scheme = HTTPBearer()


def decode_token(token: str) -> dict:
    """JWT 토큰을 디코딩해서 payload 반환"""
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 토큰입니다.",
        )


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> str:
    """
    API 엔드포인트에서 현재 로그인한 유저 ID를 가져오는 의존성.
    
    MSA 구조에서 인증은 API Gateway 또는 Auth 서비스에서 처리하고
    이 서비스는 JWT만 검증해서 user_id를 추출합니다.
    
    사용법:
        @router.get("/me")
        async def get_my_profile(user_id: str = Depends(get_current_user_id)):
            ...
    """
    payload = decode_token(credentials.credentials)
    user_id: str = payload.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="토큰에 사용자 정보가 없습니다.",
        )
    return user_id
