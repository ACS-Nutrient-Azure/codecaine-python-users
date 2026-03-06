from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserProfile, UserConditionSnapshot
from app.models.supplement import CurrentSupplement
from app.schemas.user import (
    UserProfileResponse,
    UserProfileUpdateRequest,
    SupplementResponse,
    SupplementCreateRequest,
    SupplementUpdateRequest,
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
        profile = result.scalar_one_or_none()
        if not profile:
            profile = UserProfile(cognito_id=cognito_id)
            db.add(profile)
            await db.flush()
        return profile

    async def get_profile(self, db: AsyncSession, cognito_id: str) -> UserProfileResponse:
        user = await self.get_user_or_404(db, cognito_id)
        profile = await self.get_or_create_profile(db, cognito_id)

        allergies = [a.strip() for a in profile.allergies.split(",") if a.strip()] if profile.allergies else []
        diseases = [d.strip() for d in profile.chron_diseases.split(",") if d.strip()] if profile.chron_diseases else []

        gender_map = {0: "남성", 1: "여성"}

        return UserProfileResponse(
            cognito_id=user.cognito_id,
            email=user.email,
            name=profile.name,
            birth_dt=profile.birth_dt,
            gender=profile.gender,
            gender_display=gender_map.get(profile.gender) if profile.gender is not None else None,
            phone=profile.phone,
            height=float(profile.height) if profile.height else None,
            weight=float(profile.weight) if profile.weight else None,
            allergies=allergies,
            chron_diseases=diseases,
            created_at=user.created_at,
        )

    async def update_profile(
        self, db: AsyncSession, cognito_id: str, data: UserProfileUpdateRequest
    ) -> UserProfileResponse:
        await self.get_user_or_404(db, cognito_id)
        profile = await self.get_or_create_profile(db, cognito_id)

        update_data = data.model_dump(exclude_none=True)

        if "allergies" in update_data:
            update_data["allergies"] = ",".join(update_data["allergies"])
        if "chron_diseases" in update_data:
            update_data["chron_diseases"] = ",".join(update_data["chron_diseases"])

        for field, value in update_data.items():
            setattr(profile, field, value)

        db.add(profile)
        await db.flush()
        return await self.get_profile(db, cognito_id)

    # --- Supplements ---

    async def get_supplements(self, db: AsyncSession, cognito_id: str) -> list[SupplementResponse]:
        await self.get_user_or_404(db, cognito_id)
        result = await db.execute(
            select(CurrentSupplement)
            .where(CurrentSupplement.cognito_id == cognito_id)
            .order_by(CurrentSupplement.created_at.desc())
        )
        supplements = result.scalars().all()
        return [SupplementResponse.model_validate(s) for s in supplements]

    async def create_supplement(
        self, db: AsyncSession, cognito_id: str, data: SupplementCreateRequest
    ) -> SupplementResponse:
        await self.get_user_or_404(db, cognito_id)
        supplement = CurrentSupplement(
            cognito_id=cognito_id,
            **data.model_dump(),
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

        update_data = data.model_dump(exclude_none=True)
        for field, value in update_data.items():
            setattr(supplement, field, value)
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
