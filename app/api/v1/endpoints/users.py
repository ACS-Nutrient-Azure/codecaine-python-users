from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user_id
from app.db.database import get_db
from app.schemas.user import (
    UserProfileResponse,
    UserProfileUpdateRequest,
    UserUpdateResponse,
    SupplementResponse,
    SupplementListResponse,
    SupplementCreateRequest,
    SupplementCreateResponse,
    SupplementUpdateRequest,
    SupplementStatusRequest,
    UserDeleteResponse,
)
from app.services.user_service import user_service

# --- Users Router ---
router = APIRouter(prefix="/users", tags=["마이페이지"])


@router.get("/{cognito_id}", response_model=UserProfileResponse)
async def get_profile(
    cognito_id: str,
    _: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """마이페이지 정보 조회"""
    return await user_service.get_profile(db, cognito_id)


@router.put("/{cognito_id}", response_model=UserUpdateResponse)
async def update_profile(
    cognito_id: str,
    data: UserProfileUpdateRequest,
    _: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """사용자 정보 수정"""
    await user_service.update_profile(db, cognito_id, data)
    return UserUpdateResponse()


@router.delete("/{cognito_id}", response_model=UserDeleteResponse, status_code=status.HTTP_200_OK)
async def delete_account(
    cognito_id: str,
    _: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """회원 탈퇴"""
    await user_service.delete_user(db, cognito_id)
    return UserDeleteResponse()


# --- Supplements Router ---
supplement_router = APIRouter(prefix="/supplements", tags=["영양제"])


@supplement_router.get("", response_model=SupplementListResponse)
async def get_supplements(
    cognito_id: str = Query(...),
    is_active: bool | None = Query(None),
    _: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """현재 복용 중인 영양제 목록 조회"""
    supplements = await user_service.get_supplements(db, cognito_id, is_active)
    return SupplementListResponse(supplements=supplements)


@supplement_router.post("", response_model=SupplementCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_supplement(
    data: SupplementCreateRequest,
    _: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """영양제 추가"""
    created = await user_service.create_supplement(db, data.cognito_id, data)
    return SupplementCreateResponse(ans_current_id=created.ans_current_id)


@supplement_router.put("/{ans_current_id}", response_model=SupplementResponse)
async def update_supplement(
    ans_current_id: int,
    data: SupplementUpdateRequest,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """영양제 수정"""
    return await user_service.update_supplement(db, current_user_id, ans_current_id, data)


@supplement_router.delete("/{ans_current_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_supplement(
    ans_current_id: int,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """영양제 삭제"""
    await user_service.delete_supplement(db, current_user_id, ans_current_id)


@supplement_router.patch("/{ans_current_id}/status", response_model=SupplementResponse)
async def toggle_supplement_status(
    ans_current_id: int,
    data: SupplementStatusRequest,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """영양제 활성화/비활성화"""
    return await user_service.toggle_supplement_status(db, current_user_id, ans_current_id, data)
