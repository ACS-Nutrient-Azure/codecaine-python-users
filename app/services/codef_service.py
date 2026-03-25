import json
import logging
import requests
from app.core.config import settings

logger = logging.getLogger(__name__)

CODEF_TOKEN_URL = "https://oauth.codef.io/oauth/token"
CODEF_BASE_URL = "https://development.codef.io"

def _parse_response(resp: requests.Response) -> dict:
    """CODEF 응답 파싱 — 빈 응답·비JSON·URL인코딩 응답 모두 처리"""
    text = resp.text.strip()
    if not text:
        raise ValueError(f"CODEF 빈 응답 (HTTP {resp.status_code})")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        try:
            from urllib.parse import unquote
            decoded = unquote(text)
            return json.loads(decoded)
        except Exception:
            raise ValueError(f"CODEF 응답 파싱 실패: {text[:300]}")


def get_access_token() -> str:
    resp = requests.post(
        CODEF_TOKEN_URL,
        data={"grant_type": "client_credentials", "scope": "read"},
        auth=(settings.codef_client_id, settings.codef_client_secret),
        timeout=10,
    )
    resp.raise_for_status()
    text = resp.text.strip()
    if not text:
        raise ValueError(f"CODEF 토큰 응답 비어있음 (HTTP {resp.status_code})")
    try:
        return json.loads(text)["access_token"]
    except (json.JSONDecodeError, KeyError):
        pass
    try:
        from urllib.parse import parse_qs
        parsed = parse_qs(text)
        return parsed["access_token"][0]
    except (KeyError, Exception):
        raise ValueError(f"CODEF 토큰 파싱 실패: {text[:300]}")


def request_health_check(token: str, user_name: str, phone_no: str, identity: str, nhis_id: str, start_year: str, end_year: str) -> dict:
    payload = {
        "organization": "0002",
        "loginType": "5",
        "loginTypeLevel": "1",
        "userName": user_name,
        "phoneNo": phone_no,
        "id": nhis_id,
        "identity": identity,
        "inquiryType": "4",
        "searchStartYear": start_year,
        "searchEndYear": end_year,
        "type": "1",
    }
    resp = requests.post(
        f"{CODEF_BASE_URL}/v1/kr/public/pp/nhis-health-checkup/result",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
        timeout=120,
    )
    resp.raise_for_status()
    return _parse_response(resp)


def fetch_health_check(token: str, user_name: str, phone_no: str, identity: str, nhis_id: str, start_year: str, end_year: str, two_way_info: dict) -> dict:
    payload = {
        "organization": "0002",
        "loginType": "5",
        "loginTypeLevel": "1",
        "userName": user_name,
        "phoneNo": phone_no,
        "id": nhis_id,
        "identity": identity,
        "inquiryType": "4",
        "searchStartYear": start_year,
        "searchEndYear": end_year,
        "type": "1",
        "simpleAuth": "1",
        "secureNo": "",
        "secureNoRefresh": "",
        "is2Way": True,
        "twoWayInfo": two_way_info,
    }
    resp = requests.post(
        f"{CODEF_BASE_URL}/v1/kr/public/pp/nhis-health-checkup/result",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
        timeout=120,
    )
    resp.raise_for_status()
    return _parse_response(resp)


def request_prescription(token: str, user_name: str, phone_no: str, identity: str, nhis_id: str, start_date: str, end_date: str) -> dict:
    payload = {
        "organization": "0002",
        "loginType": "5",
        "id": nhis_id,
        "identity": identity,
        "userName": user_name,
        "loginTypeLevel": "1",
        "phoneNo": phone_no,
        "timeOut": "170",
        "startDate": start_date,
        "endDate": end_date,
        "type": "1",
        "drugImageYN": "0",
        "medicationDirectionYN": "1",
        "detailYN": "1",
    }
    resp = requests.post(
        f"{CODEF_BASE_URL}/v1/kr/public/pp/nhis-treatment/information",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
        timeout=180,
    )
    resp.raise_for_status()
    result = _parse_response(resp)
    logger.info("[CODEF presc-init raw response] type=%s keys=%s", type(result).__name__, list(result.keys()) if isinstance(result, dict) else result[:2] if isinstance(result, list) else result)
    if isinstance(result, dict):
        data = result.get("data")
        logger.info("[CODEF presc-init data] type=%s value=%s", type(data).__name__, str(data)[:300])
    return result


def fetch_prescription(token: str, user_name: str, phone_no: str, identity: str, nhis_id: str, start_date: str, end_date: str, two_way_info: dict) -> dict:
    payload = {
        "organization": "0002",
        "loginType": "5",
        "id": nhis_id,
        "identity": identity,
        "userName": user_name,
        "loginTypeLevel": "1",
        "phoneNo": phone_no,
        "timeOut": "170",
        "startDate": start_date,
        "endDate": end_date,
        "type": "1",
        "drugImageYN": "0",
        "medicationDirectionYN": "1",
        "detailYN": "1",
        "simpleAuth": "1",
        "is2Way": True,
        "twoWayInfo": two_way_info,
    }
    resp = requests.post(
        f"{CODEF_BASE_URL}/v1/kr/public/pp/nhis-treatment/information",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
        timeout=120,
    )
    resp.raise_for_status()
    return _parse_response(resp)


def _get_exam_list(data: dict) -> list:
    inner = data.get("data") or {}
    logger.info("[CODEF raw data keys]: %s", list(inner.keys()) if isinstance(inner, dict) else type(inner))

    for key in ("resCheckupList", "resPreviewList", "resResultList", "resExamList", "resList"):
        val = inner.get(key) if isinstance(inner, dict) else None
        if val and isinstance(val, list) and len(val) > 0:
            logger.info("[CODEF] 리스트 키 '%s' 사용, 항목 수: %d", key, len(val))
            # 가장 최근 검진 결과가 먼저 오도록 연도 내림차순 정렬
            val = sorted(val, key=lambda x: (str(x.get("resCheckupYear") or ""), str(x.get("resCheckupDate") or "")), reverse=True)
            return val

    if isinstance(inner, dict) and inner.get("resHeight"):
        logger.info("[CODEF] data 직하위 단일 검진 결과 사용")
        return [inner]

    logger.warning("[CODEF] 검진 결과 리스트를 찾지 못함. data: %s", str(inner)[:300])
    return []


def extract_health_summary(data: dict) -> dict:
    exam_list = _get_exam_list(data)
    if not exam_list:
        return {}

    latest = exam_list[0]
    summary = {}

    if latest.get("resHeight"):
        summary["height"] = str(latest["resHeight"])
    if latest.get("resWeight"):
        summary["weight"] = str(latest["resWeight"])

    year = str(latest.get("resCheckupYear") or "")
    raw_date = str(latest.get("resCheckupDate") or "")

    if len(raw_date) == 8:
        summary["exam_date"] = f"{raw_date[:4]}-{raw_date[4:6]}-{raw_date[6:]}"
    elif len(raw_date) == 4 and len(year) == 4:
        summary["exam_date"] = f"{year}-{raw_date[:2]}-{raw_date[2:]}"
    elif len(year) == 4:
        summary["exam_date"] = f"{year}-01-01"

    return summary


def _determine_status(key: str, value: str) -> str:
    try:
        v = float(value.split("/")[0].strip())
    except (ValueError, AttributeError):
        return "정상"

    thresholds = {
        "resFastingBloodSuger": (None, 100),
        "resTotalCholesterol":  (None, 200),
        "resHDLCholesterol":    (60, None),
        "resLDLCholesterol":    (None, 130),
        "resTriglyceride":      (None, 150),
        "resHemoglobin":        (13, 16.5),
        "resSerumCreatinine":   (None, 1.6),
        "resGFR":               (60, None),
        "resAST":               (None, 40),
        "resALT":               (None, 35),
        "resyGPT":              (None, 63),
        "resWaist":             (None, 90),
        "resBMI":               (18.5, 24.9),
    }
    if key not in thresholds:
        return "정상"

    low, high = thresholds[key]
    if high is not None and v >= high:
        return "과잉"
    if low is not None and v < low:
        return "부족"
    return "정상"


def parse_health_check(data: dict) -> list:
    items = []
    exam_list = _get_exam_list(data)
    if not exam_list:
        return items

    latest = exam_list[0]

    field_map = [
        ("resBloodPressure",    "혈압",           "mmHg",          "120/80 미만"),
        ("resFastingBloodSuger","공복혈당",        "mg/dL",         "100 미만"),
        ("resTotalCholesterol", "총콜레스테롤",    "mg/dL",         "200 미만"),
        ("resHDLCholesterol",   "HDL콜레스테롤",  "mg/dL",         "60 이상"),
        ("resLDLCholesterol",   "LDL콜레스테롤",  "mg/dL",         "130 미만"),
        ("resTriglyceride",     "중성지방",        "mg/dL",         "150 미만"),
        ("resHemoglobin",       "혈색소",          "g/dL",          "남:13~16.5 / 여:12~15.5"),
        ("resSerumCreatinine",  "크레아티닌",      "mg/dL",         "1.6 이하"),
        ("resGFR",              "사구체여과율",    "mL/min/1.73m2", "60 이상"),
        ("resAST",              "AST",             "U/L",           "40 이하"),
        ("resALT",              "ALT",             "U/L",           "35 이하"),
        ("resyGPT",             "감마지티피",      "U/L",           "남:11~63 / 여:8~35"),
        ("resWaist",            "허리둘레",        "cm",            "남:90 미만 / 여:85 미만"),
        ("resBMI",              "체질량지수",      "kg/m²",         "18.5~24.9"),
    ]

    for idx, (key, name, unit, range_str) in enumerate(field_map):
        value = latest.get(key)
        if value:
            items.append({
                "id": idx + 1,
                "name": name,
                "value": str(value),
                "unit": unit,
                "status": _determine_status(key, str(value)),
                "range": range_str,
            })

    return items


def parse_prescription(data) -> list:
    meds = []
    if isinstance(data, list):
        d = {}
    else:
        d = data.get("data", {}) if isinstance(data, dict) else {}

    if isinstance(d, list):
        treat_list = d
    else:
        treat_list = d.get("resTreatList") or d.get("resList") or []

    # 가장 최신 날짜의 처방 기록만 사용
    if treat_list:
        date_keys = ("resTreatDate", "resPrescribeDate", "resVisitDate", "resTreatYmd", "resDate")
        def get_date(treat):
            for k in date_keys:
                v = treat.get(k)
                if v:
                    return str(v)
            return ""
        latest_date = max(get_date(t) for t in treat_list)
        if latest_date:
            treat_list = [t for t in treat_list if get_date(t) == latest_date]
            logger.info("[CODEF presc] 최신 처방일 '%s' 기준 %d건 필터링", latest_date, len(treat_list))

    seen = set()
    for treat in treat_list:
        med_list = treat.get("resMedicineList") or treat.get("resMediDetailList") or []
        for med in med_list:
            name = med.get("resProductName") or med.get("resDrugName") or med.get("resPrescribeDrugName") or ""
            if not name or name in seen:
                continue
            seen.add(name)
            meds.append({
                "id": len(meds) + 1,
                "name": name,
                "dose": med.get("resOneDayDose") or med.get("resDose") or med.get("resPrescribeDays") or "-",
                "schedule": med.get("resMedicationInfo") or med.get("resUsage") or med.get("resPrescribeDrugEffect") or "-",
            })

    if not meds:
        for med in (d.get("resMediDetailList") if isinstance(d, dict) else None) or []:
            name = med.get("resProductName") or med.get("resDrugName") or med.get("resPrescribeDrugName") or ""
            if not name or name in seen:
                continue
            seen.add(name)
            meds.append({
                "id": len(meds) + 1,
                "name": name,
                "dose": med.get("resOneDayDose") or med.get("resDose") or "-",
                "schedule": med.get("resMedicationInfo") or med.get("resUsage") or "-",
            })

    return meds
