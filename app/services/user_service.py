import logging

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserProfile, UserConditionSnapshot
from app.models.supplement import CurrentSupplement
from app.schemas.user import (
    UserProfileResponse,
    UserProfileUpdateRequest,
    SupplementResponse,
    SupplementCreateRequest,
    SupplementUpdateRequest,
    SupplementStatusRequest,
)

logger = logging.getLogger(__name__)


class UserService:

    async def get_or_create_user(self, db: AsyncSession, cognito_id: str, email: str = "") -> User:
        result = await db.execute(select(User).where(User.cognito_id == cognito_id))
        user = result.scalar_one_or_none()
        if not user:
            # 동일 email이 다른 cognito_id에 이미 존재하는 경우 unique constraint 위반 방지
            if email:
                existing = await db.execute(select(User).where(User.email == email))
                existing_user = existing.scalar_one_or_none()
                if existing_user and existing_user.cognito_id != cognito_id:
                    # 이미 다른 계정에 등록된 이메일 — 빈 문자열로 대체하여 충돌 방지
                    logger.warning(
                        "[USER] email=%s 이미 cognito_id=%s 에 등록됨. 신규 유저 email 비워서 생성.",
                        email, existing_user.cognito_id,
                    )
                    email = ""
            user = User(cognito_id=cognito_id, email=email)
            db.add(user)
            try:
                await db.flush()
            except IntegrityError:
                await db.rollback()
                # 동시 요청으로 이미 생성된 경우 재조회
                result = await db.execute(select(User).where(User.cognito_id == cognito_id))
                user = result.scalar_one_or_none()
                if not user:
                    raise
        elif email and user.email != email:
            # Cognito 토큰의 이메일이 DB와 다르면 최신 이메일로 동기화
            try:
                user.email = email
                db.add(user)
                await db.flush()
            except IntegrityError:
                await db.rollback()
                # 다른 계정에 동일 이메일이 있으면 업데이트 생략
                logger.warning("[USER] email=%s 이미 다른 계정에 존재. 이메일 동기화 생략.", email)
                result = await db.execute(select(User).where(User.cognito_id == cognito_id))
                user = result.scalar_one_or_none()
        return user

    async def get_or_create_profile(self, db: AsyncSession, cognito_id: str) -> UserProfile:
        result = await db.execute(
            select(UserProfile).where(UserProfile.cognito_id == cognito_id)
        )
        profile = result.scalars().first()
        if not profile:
            profile = UserProfile(cognito_id=cognito_id)
            db.add(profile)
            await db.flush()
        return profile

    async def get_profile(self, db: AsyncSession, cognito_id: str, email: str = "") -> UserProfileResponse:
        user = await self.get_or_create_user(db, cognito_id, email)
        profile = await self.get_or_create_profile(db, cognito_id)

        return UserProfileResponse(
            cognito_id=user.cognito_id,
            email=user.email,
            ans_birth_dt=profile.birth_dt,
            ans_gender=profile.gender,
            ans_height=float(profile.height) if profile.height else None,
            ans_weight=float(profile.weight) if profile.weight else None,
            ans_allergies=profile.allergies,
            ans_chron_diseases=profile.chron_diseases,
            ans_current_conditions=None,
            created_at=user.created_at,
            updated_at=profile.updated_at,
        )

    async def update_profile(
        self, db: AsyncSession, cognito_id: str, data: UserProfileUpdateRequest, email: str = ""
    ) -> UserProfileResponse:
        await self.get_or_create_user(db, cognito_id, email)
        profile = await self.get_or_create_profile(db, cognito_id)

        # ans_ prefix를 DB 컬럼명으로 변환
        field_map = {
            "ans_birth_dt": "birth_dt",
            "ans_gender": "gender",
            "ans_height": "height",
            "ans_weight": "weight",
            "ans_allergies": "allergies",
            "ans_chron_diseases": "chron_diseases",
        }
        update_data = data.model_dump(exclude_none=True)
        for ans_field, value in update_data.items():
            db_field = field_map.get(ans_field)
            if db_field:
                setattr(profile, db_field, value)

        db.add(profile)
        await db.flush()
        return await self.get_profile(db, cognito_id, email)

    # --- Supplements ---

    async def get_supplements(
        self, db: AsyncSession, cognito_id: str, is_active: bool | None = None, email: str = ""
    ) -> list[SupplementResponse]:
        await self.get_or_create_user(db, cognito_id, email)
        query = select(CurrentSupplement).where(CurrentSupplement.cognito_id == cognito_id)
        if is_active is not None:
            query = query.where(CurrentSupplement.is_active == is_active)
        query = query.order_by(CurrentSupplement.created_at.desc())
        result = await db.execute(query)
        supplements = result.scalars().all()
        return [SupplementResponse.model_validate(s) for s in supplements]

    async def create_supplement(
        self, db: AsyncSession, cognito_id: str, data: SupplementCreateRequest,
        email: str = ""
    ) -> SupplementResponse:
        await self.get_or_create_user(db, cognito_id, email)
        supplement = CurrentSupplement(
            cognito_id=cognito_id,
            product_name=data.ans_product_name,
            serving_amount=data.ans_serving_amount,
            serving_per_day=data.ans_serving_per_day,
            daily_total_amount=data.ans_daily_total_amount,
            is_active=data.ans_is_active,
            ingredients=data.ans_ingredients,
        )
        db.add(supplement)
        await db.flush()
        return SupplementResponse.model_validate(supplement)

    async def update_supplement(
        self, db: AsyncSession, cognito_id: str, current_id: int, data: SupplementUpdateRequest,
    ) -> SupplementResponse:
        result = await db.execute(
            select(CurrentSupplement).where(
                CurrentSupplement.current_id == current_id,
                CurrentSupplement.cognito_id == cognito_id,
            )
        )
        supplement = result.scalar_one_or_none()
        if not supplement:
            raise HTTPException(status_code=404, detail="영양제를 찾을 수 없습니다.")

        field_map = {
            "ans_product_name": "product_name",
            "ans_serving_amount": "serving_amount",
            "ans_serving_per_day": "serving_per_day",
            "ans_daily_total_amount": "daily_total_amount",
            "ans_is_active": "is_active",
            "ans_ingredients": "ingredients",
        }
        update_data = data.model_dump(exclude_none=True)
        for ans_field, value in update_data.items():
            db_field = field_map.get(ans_field)
            if db_field:
                setattr(supplement, db_field, value)

        db.add(supplement)
        await db.flush()
        return SupplementResponse.model_validate(supplement)

    async def toggle_supplement_status(
        self, db: AsyncSession, cognito_id: str, current_id: int, data: SupplementStatusRequest,
    ) -> SupplementResponse:
        result = await db.execute(
            select(CurrentSupplement).where(
                CurrentSupplement.current_id == current_id,
                CurrentSupplement.cognito_id == cognito_id,
            )
        )
        supplement = result.scalar_one_or_none()
        if not supplement:
            raise HTTPException(status_code=404, detail="영양제를 찾을 수 없습니다.")

        supplement.is_active = data.ans_is_active
        db.add(supplement)
        await db.flush()
        return SupplementResponse.model_validate(supplement)

    async def delete_supplement(
        self, db: AsyncSession, cognito_id: str, current_id: int,
    ) -> None:
        result = await db.execute(
            select(CurrentSupplement).where(
                CurrentSupplement.current_id == current_id,
                CurrentSupplement.cognito_id == cognito_id,
            )
        )
        supplement = result.scalar_one_or_none()
        if not supplement:
            raise HTTPException(status_code=404, detail="영양제를 찾을 수 없습니다.")
        await db.delete(supplement)

    async def save_condition_snapshot(self, db: AsyncSession, cognito_id: str, purposes: list[str]) -> None:
        status = ", ".join(purposes) if purposes else ""
        snapshot = UserConditionSnapshot(cognito_id=cognito_id, status=status)
        db.add(snapshot)

    async def delete_user(self, db: AsyncSession, cognito_id: str) -> None:
        result = await db.execute(select(User).where(User.cognito_id == cognito_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="사용자를 찾을 수 없습니다.")
        await db.delete(user)


user_service = UserService()
