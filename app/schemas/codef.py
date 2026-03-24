from pydantic import BaseModel
from typing import Optional, Dict


class CodefUserInfo(BaseModel):
    user_name: str
    phone_no: str
    identity: str        # 생년월일 YYYYMMDD
    nhis_id: str         # NHIS 해시 ID
    year: str = "2025"
    start_date: str = "20250101"
    end_date: str = "20251231"


class CodefInitResponse(BaseModel):
    health_check_two_way: Optional[Dict] = None
    token: str
    hc_start_year: str = ""
    hc_end_year: str = ""


class CodefFetchRequest(BaseModel):
    cognito_id: str
    user_info: CodefUserInfo
    health_check_two_way: Dict
    token: str
    hc_start_year: Optional[str] = None
    hc_end_year: Optional[str] = None


class CodefPrescInitResponse(BaseModel):
    prescription_two_way: Dict
    token: str
    presc_start: str = ""
    presc_end: str = ""


class CodefPrescFetchRequest(BaseModel):
    cognito_id: str
    user_info: CodefUserInfo
    prescription_two_way: Dict
    token: str
    presc_start: Optional[str] = None
    presc_end: Optional[str] = None


class CodefPrescInitResponse(BaseModel):
    prescription_two_way: Optional[Dict] = None
    token: str
    presc_start: str = ""
    presc_end: str = ""


class CodefPrescFetchRequest(BaseModel):
    cognito_id: str
    user_info: CodefUserInfo
    prescription_two_way: Dict
    token: str
    presc_start: Optional[str] = None
    presc_end: Optional[str] = None
