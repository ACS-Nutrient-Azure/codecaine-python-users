from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user_id
from app.db.database import get_db
from app.schemas.user import (
    UserProfileResponse,
    UserProfileUpdateRequest,
    SupplementResponse,
    SupplementCreateRequest,
    SupplementUpdateRequest,
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
    """내 프로필 수정"""
    return await user_service.update_profile(db, user_id, data)


@router.delete("/me", response_model=UserDeleteResponse, status_code=status.HTTP_200_OK)
async def delete_my_account(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """회원 탈퇴"""
    await user_service.delete_user(db, user_id)
    return UserDeleteResponse()


# --- Supplements ---

@router.get("/me/supplements", response_model=list[SupplementResponse])
async def get_my_supplements(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """내 영양제 목록 조회"""
    return await user_service.get_supplements(db, user_id)


@router.post("/me/supplements", response_model=SupplementResponse, status_code=status.HTTP_201_CREATED)
async def create_supplement(
    data: SupplementCreateRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """영양제 추가"""
    return await user_service.create_supplement(db, user_id, data)


@router.put("/me/supplements/{current_id}", response_model=SupplementResponse)
async def update_supplement(
    current_id: int,
    data: SupplementUpdateRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """영양제 수정"""
    return await user_service.update_supplement(db, user_id, current_id, data)


@router.delete("/me/supplements/{current_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_supplement(
    current_id: int,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """영양제 삭제"""
    await user_service.delete_supplement(db, user_id, current_id)
