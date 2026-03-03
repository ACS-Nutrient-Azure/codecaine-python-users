from datetime import datetime
from pydantic import BaseModel, EmailStr, field_validator


class UserProfileResponse(BaseModel):
    """GET /users/me 응답"""
    id: str
    nickname: str
    email: str
    profile_image_url: str | None
    bio: str | None
    age: int | None
    gender: str | None
    health_goals: str | None
    push_notification: bool
    email_notification: bool
    created_at: datetime

    class Config:
        from_attributes = True  # SQLAlchemy 모델 → Pydantic 자동 변환


class UserProfileUpdateRequest(BaseModel):
    """PUT /users/me 요청 바디"""
    nickname: str | None = None
    bio: str | None = None
    age: int | None = None
    gender: str | None = None
    health_goals: str | None = None

    @field_validator("nickname")
    @classmethod
    def nickname_length(cls, v):
        if v and (len(v) < 2 or len(v) > 50):
            raise ValueError("닉네임은 2자 이상 50자 이하여야 합니다.")
        return v

    @field_validator("bio")
    @classmethod
    def bio_length(cls, v):
        if v and len(v) > 200:
            raise ValueError("소개글은 200자 이하여야 합니다.")
        return v

    @field_validator("gender")
    @classmethod
    def gender_value(cls, v):
        if v and v not in ("male", "female", "other"):
            raise ValueError("gender는 male | female | other 중 하나여야 합니다.")
        return v


class NotificationSettingsUpdateRequest(BaseModel):
    """PUT /users/me/settings 요청 바디"""
    push_notification: bool | None = None
    email_notification: bool | None = None


class UserDeleteResponse(BaseModel):
    """DELETE /users/me 응답"""
    message: str = "회원 탈퇴가 완료되었습니다."
