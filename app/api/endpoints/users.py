from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user, get_current_user_id, CurrentUser
from app.db.database import get_db, get_history_db
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
    SupplementScanResponse,
    UserDeleteResponse,
)
from app.services.scan_service import scan_supplement_image
from app.services.user_service import user_service

# --- Users Router ---
router = APIRouter(prefix="/users", tags=["마이페이지"])


@router.get("/{cognito_id}", response_model=UserProfileResponse)
async def get_profile(
    cognito_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """마이페이지 정보 조회"""
    if current_user.cognito_id != cognito_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="본인의 정보만 조회할 수 있습니다.")
    return await user_service.get_profile(db, cognito_id, current_user.email)


@router.put("/{cognito_id}", response_model=UserUpdateResponse)
async def update_profile(
    cognito_id: str,
    data: UserProfileUpdateRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """사용자 정보 수정"""
    if current_user.cognito_id != cognito_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="본인의 정보만 수정할 수 있습니다.")
    await user_service.update_profile(db, cognito_id, data, current_user.email)
    return UserUpdateResponse()


@router.delete("/{cognito_id}", response_model=UserDeleteResponse, status_code=status.HTTP_200_OK)
async def delete_account(
    cognito_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """회원 탈퇴"""
    if current_user_id != cognito_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="본인 계정만 탈퇴할 수 있습니다.")
    await user_service.delete_user(db, cognito_id)
    return UserDeleteResponse()


# --- Supplements Router ---
supplement_router = APIRouter(prefix="/users/supplements", tags=["영양제"])


@supplement_router.get("", response_model=SupplementListResponse)
async def get_supplements(
    cognito_id: str = Query(...),
    is_active: bool | None = Query(None),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """현재 복용 중인 영양제 목록 조회"""
    if current_user.cognito_id != cognito_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="본인의 영양제 목록만 조회할 수 있습니다.")
    supplements = await user_service.get_supplements(db, cognito_id, is_active, current_user.email)
    return SupplementListResponse(supplements=supplements)


@supplement_router.post("", response_model=SupplementCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_supplement(
    data: SupplementCreateRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    history_db: AsyncSession = Depends(get_history_db),
):
    """영양제 추가"""
    if current_user.cognito_id != data.cognito_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="본인의 영양제만 추가할 수 있습니다.")
    created = await user_service.create_supplement(db, data.cognito_id, data, current_user.email, history_db)
    return SupplementCreateResponse(ans_current_id=created.ans_current_id)


@supplement_router.post("/scan", response_model=SupplementScanResponse)
async def scan_supplement(
    image: UploadFile = File(..., description="영양제 성분표 이미지 (JPEG/PNG, 최대 5MB)"),
    cognito_id: str = Form(...),
    _: str = Depends(get_current_user_id),
):
    """영양제 성분표 이미지를 AWS Textract로 분석하여 성분 정보 추출"""
    # MIME 타입 검사
    allowed_types = {"image/jpeg", "image/png", "image/webp"}
    if image.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="JPEG, PNG, WEBP 형식의 이미지만 지원합니다.",
        )
    image_bytes = await image.read()
    return await scan_supplement_image(image_bytes)


@supplement_router.put("/{ans_current_id}", response_model=SupplementResponse)
async def update_supplement(
    ans_current_id: int,
    data: SupplementUpdateRequest,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    history_db: AsyncSession = Depends(get_history_db),
):
    """영양제 수정"""
    return await user_service.update_supplement(db, current_user_id, ans_current_id, data, history_db)


@supplement_router.delete("/{ans_current_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_supplement(
    ans_current_id: int,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    history_db: AsyncSession = Depends(get_history_db),
):
    """영양제 삭제"""
    await user_service.delete_supplement(db, current_user_id, ans_current_id, history_db)


@supplement_router.patch("/{ans_current_id}/status", response_model=SupplementResponse)
async def toggle_supplement_status(
    ans_current_id: int,
    data: SupplementStatusRequest,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    history_db: AsyncSession = Depends(get_history_db),
):
    """영양제 활성화/비활성화"""
    return await user_service.toggle_supplement_status(db, current_user_id, ans_current_id, data, history_db)
