from fastapi import HTTPException, status, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import boto3

from app.core.config import settings
from app.models.user import User
from app.schemas.user import UserProfileUpdateRequest, NotificationSettingsUpdateRequest


class UserService:
    """
    마이페이지 비즈니스 로직.
    엔드포인트(router)에서 직접 DB를 건드리지 않고 이 서비스를 통해서만 접근.
    """

    async def get_user_or_404(self, db: AsyncSession, user_id: str) -> User:
        """유저 조회 - 없으면 404"""
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="사용자를 찾을 수 없습니다.",
            )
        return user

    async def get_profile(self, db: AsyncSession, user_id: str) -> User:
        return await self.get_user_or_404(db, user_id)

    async def update_profile(
        self,
        db: AsyncSession,
        user_id: str,
        data: UserProfileUpdateRequest,
    ) -> User:
        user = await self.get_user_or_404(db, user_id)

        # None이 아닌 필드만 업데이트 (부분 수정 지원)
        update_data = data.model_dump(exclude_none=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        db.add(user)
        return user

    async def update_notification_settings(
        self,
        db: AsyncSession,
        user_id: str,
        data: NotificationSettingsUpdateRequest,
    ) -> User:
        user = await self.get_user_or_404(db, user_id)

        update_data = data.model_dump(exclude_none=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        db.add(user)
        return user

    async def upload_profile_image(
        self,
        db: AsyncSession,
        user_id: str,
        file: UploadFile,
    ) -> User:
        """프로필 이미지를 S3에 업로드하고 URL을 DB에 저장"""
        # 파일 타입 검증
        if file.content_type not in ("image/jpeg", "image/png", "image/webp"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="jpg, png, webp 형식만 가능합니다.",
            )

        # S3 업로드
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.aws_region,
        )
        s3_key = f"profile-images/{user_id}/{file.filename}"
        s3_client.upload_fileobj(
            file.file,
            settings.s3_bucket_name,
            s3_key,
            ExtraArgs={"ContentType": file.content_type},
        )

        image_url = f"https://{settings.s3_bucket_name}.s3.{settings.aws_region}.amazonaws.com/{s3_key}"

        user = await self.get_user_or_404(db, user_id)
        user.profile_image_url = image_url
        db.add(user)
        return user

    async def delete_user(self, db: AsyncSession, user_id: str) -> None:
        """회원 탈퇴 - soft delete (is_active = False)"""
        user = await self.get_user_or_404(db, user_id)
        user.is_active = False
        db.add(user)


# 싱글톤처럼 사용
user_service = UserService()
