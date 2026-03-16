from datetime import datetime, date
from pydantic import BaseModel, Field, ConfigDict


class UserProfileResponse(BaseModel):
    cognito_id: str
    email: str
    ans_birth_dt: date | None = None
    ans_gender: int | None = None
    ans_height: float | None = None
    ans_weight: float | None = None
    ans_allergies: str | None = None
    ans_chron_diseases: str | None = None
    ans_current_conditions: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class UserProfileUpdateRequest(BaseModel):
    ans_birth_dt: date | None = None
    ans_gender: int | None = None
    ans_height: float | None = None
    ans_weight: float | None = None
    ans_allergies: str | None = None
    ans_chron_diseases: str | None = None
    ans_current_conditions: str | None = None


class SupplementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    ans_current_id: int = Field(validation_alias="current_id")
    cognito_id: str
    ans_product_name: str | None = Field(None, validation_alias="product_name")
    ans_serving_amount: int | None = Field(None, validation_alias="serving_amount")
    ans_serving_per_day: int | None = Field(None, validation_alias="serving_per_day")
    ans_daily_total_amount: int | None = Field(None, validation_alias="daily_total_amount")
    ans_is_active: bool | None = Field(None, validation_alias="is_active")
    ans_ingredients: dict | None = Field(None, validation_alias="ingredients")
    created_at: datetime | None = None


class SupplementListResponse(BaseModel):
    supplements: list[SupplementResponse]


class SupplementCreateRequest(BaseModel):
    cognito_id: str
    ans_product_name: str
    ans_serving_amount: int | None = None
    ans_serving_per_day: int | None = None
    ans_daily_total_amount: int | None = None
    ans_is_active: bool = True
    ans_ingredients: dict | None = None


class SupplementUpdateRequest(BaseModel):
    ans_product_name: str | None = None
    ans_serving_amount: int | None = None
    ans_serving_per_day: int | None = None
    ans_daily_total_amount: int | None = None
    ans_is_active: bool | None = None
    ans_ingredients: dict | None = None


class SupplementStatusRequest(BaseModel):
    ans_is_active: bool


class UserUpdateResponse(BaseModel):
    success: bool = True
    message: str = "사용자 정보가 업데이트되었습니다."


class SupplementCreateResponse(BaseModel):
    ans_current_id: int
    success: bool = True
    message: str = "영양제가 추가되었습니다."


class UserDeleteResponse(BaseModel):
    message: str = "회원 탈퇴가 완료되었습니다."


class SupplementScanParsedResult(BaseModel):
    """파싱된 영양제 정보"""
    ans_product_name: str | None = None
    ans_serving_amount: int | None = None
    ans_serving_per_day: int | None = None
    ans_daily_total_amount: int | None = None
    ans_ingredients: dict[str, float] | None = None


class SupplementScanConfidence(BaseModel):
    """각 필드 파싱 신뢰도 0.0~1.0"""
    product_name: float = 0.0
    serving_info: float = 0.0
    ingredients: float = 0.0


class SupplementScanResponse(BaseModel):
    success: bool = True
    raw_text: str
    parsed: SupplementScanParsedResult
    confidence: SupplementScanConfidence
    warnings: list[str] = []
