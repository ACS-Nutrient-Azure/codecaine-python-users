from datetime import datetime, date
from decimal import Decimal
from pydantic import BaseModel, field_validator


class UserProfileResponse(BaseModel):
    cognito_id: str
    email: str
    name: str | None = None
    birth_dt: date | None = None
    gender: int | None = None
    gender_display: str | None = None
    phone: str | None = None
    height: float | None = None
    weight: float | None = None
    allergies: list[str] = []
    chron_diseases: list[str] = []
    created_at: datetime | None = None

    class Config:
        from_attributes = True


class UserProfileUpdateRequest(BaseModel):
    name: str | None = None
    birth_dt: date | None = None
    gender: int | None = None
    phone: str | None = None
    height: float | None = None
    weight: float | None = None
    allergies: list[str] | None = None
    chron_diseases: list[str] | None = None

    @field_validator("phone")
    @classmethod
    def phone_format(cls, v):
        if v and len(v) > 20:
            raise ValueError("전화번호는 20자 이하여야 합니다.")
        return v


class SupplementResponse(BaseModel):
    current_id: int
    cognito_id: str
    product_name: str | None = None
    serving_amount: int | None = None
    serving_per_day: int | None = None
    daily_total_amount: int | None = None
    total_quantity: int | None = None
    is_active: bool | None = None
    purchased_dt: date | None = None
    estimated_end_dt: date | None = None
    start_dt: date | None = None
    end_dt: date | None = None
    created_at: datetime | None = None

    class Config:
        from_attributes = True


class SupplementCreateRequest(BaseModel):
    product_name: str
    serving_amount: int | None = None
    serving_per_day: int | None = None
    daily_total_amount: int | None = None
    total_quantity: int | None = None
    is_active: bool = True
    purchased_dt: date | None = None
    estimated_end_dt: date | None = None
    start_dt: date | None = None
    end_dt: date | None = None


class SupplementUpdateRequest(BaseModel):
    product_name: str | None = None
    serving_amount: int | None = None
    serving_per_day: int | None = None
    daily_total_amount: int | None = None
    total_quantity: int | None = None
    is_active: bool | None = None
    purchased_dt: date | None = None
    estimated_end_dt: date | None = None
    start_dt: date | None = None
    end_dt: date | None = None


class UserDeleteResponse(BaseModel):
    message: str = "회원 탈퇴가 완료되었습니다."
