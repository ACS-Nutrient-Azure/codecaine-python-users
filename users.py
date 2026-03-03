from fastapi import APIRouter, Depends, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user_id
from app.db.database import get_db
from app.schemas.user import (
    UserProfileResponse,
    UserProfileUpdateRequest,
    NotificationSettingsUpdateRequest,
    UserDeleteResponse,
)
from app.services.user_service import user_service

router = APIRouter(prefix="/users", tags=["마이페이지"])


@router.get("/me", response_model=UserProfileResponse)
async def get_my_profile(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """내 프로필 조회"""
    return await user_service.get_profile(db, user_id)


@router.put("/me", response_model=UserProfileResponse)
async def update_my_profile(
    data: UserProfileUpdateRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """내 프로필 수정 (닉네임, 소개글, 나이, 성별, 건강 목표)"""
    return await user_service.update_profile(db, user_id, data)


@router.post("/me/profile-image", response_model=UserProfileResponse)
async def upload_profile_image(
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """프로필 이미지 업로드 (S3 저장)"""
    return await user_service.upload_profile_image(db, user_id, file)


@router.put("/me/settings", response_model=UserProfileResponse)
async def update_notification_settings(
    data: NotificationSettingsUpdateRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """알림 설정 변경"""
    return await user_service.update_notification_settings(db, user_id, data)


@router.delete("/me", response_model=UserDeleteResponse, status_code=status.HTTP_200_OK)
async def delete_my_account(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """회원 탈퇴 (Soft Delete)"""
    await user_service.delete_user(db, user_id)
    return UserDeleteResponse()
