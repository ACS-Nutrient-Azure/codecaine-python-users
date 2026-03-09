from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserProfile
from app.models.supplement import CurrentSupplement
from app.schemas.user import (
    UserProfileResponse,
    UserProfileUpdateRequest,
    SupplementResponse,
    SupplementCreateRequest,
    SupplementUpdateRequest,
    SupplementStatusRequest,
)


class UserService:

    async def get_user_or_404(self, db: AsyncSession, cognito_id: str) -> User:
        result = await db.execute(select(User).where(User.cognito_id == cognito_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="사용자를 찾을 수 없습니다.",
            )
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

    async def get_profile(self, db: AsyncSession, cognito_id: str) -> UserProfileResponse:
        user = await self.get_user_or_404(db, cognito_id)
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
        self, db: AsyncSession, cognito_id: str, data: UserProfileUpdateRequest
    ) -> UserProfileResponse:
        await self.get_user_or_404(db, cognito_id)
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
        return await self.get_profile(db, cognito_id)

    # --- Supplements ---

    async def get_supplements(
        self, db: AsyncSession, cognito_id: str, is_active: bool | None = None
    ) -> list[SupplementResponse]:
        await self.get_user_or_404(db, cognito_id)
        query = select(CurrentSupplement).where(CurrentSupplement.cognito_id == cognito_id)
        if is_active is not None:
            query = query.where(CurrentSupplement.is_active == is_active)
        query = query.order_by(CurrentSupplement.created_at.desc())
        result = await db.execute(query)
        supplements = result.scalars().all()
        return [SupplementResponse.model_validate(s) for s in supplements]

    async def create_supplement(
        self, db: AsyncSession, cognito_id: str, data: SupplementCreateRequest
    ) -> SupplementResponse:
        await self.get_user_or_404(db, cognito_id)
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
        self, db: AsyncSession, cognito_id: str, current_id: int, data: SupplementUpdateRequest
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
        self, db: AsyncSession, cognito_id: str, current_id: int, data: SupplementStatusRequest
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

    async def delete_supplement(self, db: AsyncSession, cognito_id: str, current_id: int) -> None:
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

    async def delete_user(self, db: AsyncSession, cognito_id: str) -> None:
        user = await self.get_user_or_404(db, cognito_id)
        await db.delete(user)


user_service = UserService()
