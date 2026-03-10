"""영양제 성분표 스캔 서비스 - AWS Textract + 정규식 파싱"""
import asyncio
import re
import unicodedata
from functools import partial

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from fastapi import HTTPException

from app.core.config import settings
from app.schemas.user import SupplementScanConfidence, SupplementScanParsedResult, SupplementScanResponse

MAX_IMAGE_BYTES = 5 * 1024 * 1024  # 5MB

# 정규식 패턴 (한국어 영양성분표 기준)
_PRODUCT_PATTERNS = [
    re.compile(r"제품명\s*[:：]\s*(.+)"),
    re.compile(r"품\s*명\s*[:：]\s*(.+)"),
]

_SERVING_AMOUNT_PATTERNS = [
    re.compile(r"1회\s*섭취량\s*[:：]?\s*(\d+)\s*(?:정|캡슐|알|tablet|capsule)", re.I),
    re.compile(r"1회\s*분량\s*[:：]?\s*(\d+)\s*(?:정|캡슐|알)", re.I),
    re.compile(r"serving\s*size\s*[:：]?\s*(\d+)", re.I),
]

_SERVING_PER_DAY_PATTERNS = [
    re.compile(r"1일\s*(?:섭취|복용|권장)\s*횟수\s*[:：]?\s*(\d+)\s*회"),
    re.compile(r"하루\s*(\d+)\s*회"),
    re.compile(r"1일\s*(\d+)\s*회"),
    re.compile(r"daily\s*intake\s*[:：]?\s*(\d+)", re.I),
]

# 성분명 mg량 패턴 (2~30자 한글/영문 + 숫자 + 단위)
_INGREDIENT_PATTERN = re.compile(
    r"^([가-힣a-zA-Z0-9·（）()\-\s·]{2,30}?)\s+"
    r"(\d+(?:\.\d+)?)\s*"
    r"(mg|μg|mcg|IU|g|㎍|㎎)\b"
)

# 노이즈 라인 패턴 (표 헤더, 열량 등 제외 대상)
_NOISE_PATTERNS = [
    re.compile(r"^(성분명|1회분량|1일섭취량|%영양성분기준치|구분)$"),
    re.compile(r"(열량|칼로리|나트륨|탄수화물|당류|단백질|지방|포화지방|트랜스지방)"),
]


def _is_noise_line(line: str) -> bool:
    line = line.strip()
    return any(p.search(line) for p in _NOISE_PATTERNS)


def _call_textract(image_bytes: bytes) -> str:
    """AWS Textract 동기 호출 (run_in_executor로 감싸서 사용)"""
    client = boto3.client(
        "textract",
        region_name=settings.aws_region,
        aws_access_key_id=settings.aws_access_key_id or None,
        aws_secret_access_key=settings.aws_secret_access_key or None,
    )
    response = client.detect_document_text(Document={"Bytes": image_bytes})
    lines = [
        block["Text"]
        for block in response["Blocks"]
        if block["BlockType"] == "LINE"
    ]
    return "\n".join(lines)


async def extract_text(image_bytes: bytes) -> str:
    """Textract로 텍스트 추출 (async 래퍼)"""
    loop = asyncio.get_event_loop()
    try:
        return await loop.run_in_executor(None, partial(_call_textract, image_bytes))
    except ClientError as e:
        code = e.response["Error"]["Code"]
        raise HTTPException(status_code=503, detail=f"AWS Textract 오류: {code}")
    except BotoCoreError as e:
        raise HTTPException(status_code=503, detail=f"AWS 연결 오류: {str(e)}")


def _parse_text(raw_text: str) -> tuple[SupplementScanParsedResult, SupplementScanConfidence, list[str]]:
    """추출된 텍스트를 파싱하여 영양제 정보 구조화"""
    lines = [unicodedata.normalize("NFC", l.strip()) for l in raw_text.split("\n") if l.strip()]
    warnings: list[str] = []

    # 제품명 파싱
    product_name: str | None = None
    product_confidence = 0.0
    for line in lines:
        for pat in _PRODUCT_PATTERNS:
            m = pat.search(line)
            if m:
                product_name = m.group(1).strip()
                product_confidence = 0.85
                break
        if product_name:
            break
    if not product_name:
        warnings.append("제품명을 인식하지 못했습니다. 직접 입력해주세요.")

    # 1회 섭취량 파싱
    serving_amount: int | None = None
    serving_per_day: int | None = None
    serving_confidence = 0.0

    for line in lines:
        for pat in _SERVING_AMOUNT_PATTERNS:
            m = pat.search(line)
            if m and serving_amount is None:
                serving_amount = int(m.group(1))
                serving_confidence += 0.4
                break

    for line in lines:
        for pat in _SERVING_PER_DAY_PATTERNS:
            m = pat.search(line)
            if m and serving_per_day is None:
                serving_per_day = int(m.group(1))
                serving_confidence += 0.4
                break

    serving_confidence = min(serving_confidence, 1.0)

    daily_total: int | None = None
    if serving_amount is not None and serving_per_day is not None:
        daily_total = serving_amount * serving_per_day
    elif serving_amount is not None:
        daily_total = serving_amount

    # 성분 파싱
    ingredients: dict[str, float] = {}
    for line in lines:
        if _is_noise_line(line):
            continue
        m = _INGREDIENT_PATTERN.match(line)
        if m:
            name = m.group(1).strip()
            amount = float(m.group(2))
            unit = m.group(3)
            # μg/mcg → mg 변환 (1000:1)
            if unit in ("μg", "mcg", "㎍"):
                amount = round(amount / 1000, 4)
            ingredients[name] = amount

    ingredient_confidence = 0.0
    if len(ingredients) >= 5:
        ingredient_confidence = 0.9
    elif len(ingredients) >= 2:
        ingredient_confidence = 0.7
    elif len(ingredients) >= 1:
        ingredient_confidence = 0.5

    if not ingredients:
        warnings.append("성분 정보를 인식하지 못했습니다. 직접 입력해주세요.")

    parsed = SupplementScanParsedResult(
        ans_product_name=product_name,
        ans_serving_amount=serving_amount,
        ans_serving_per_day=serving_per_day,
        ans_daily_total_amount=daily_total,
        ans_ingredients=ingredients if ingredients else None,
    )
    confidence = SupplementScanConfidence(
        product_name=product_confidence,
        serving_info=serving_confidence,
        ingredients=ingredient_confidence,
    )
    return parsed, confidence, warnings


async def scan_supplement_image(image_bytes: bytes) -> SupplementScanResponse:
    """이미지에서 영양제 정보 추출 전체 파이프라인"""
    if len(image_bytes) > MAX_IMAGE_BYTES:
        raise HTTPException(status_code=400, detail="이미지 크기는 5MB를 초과할 수 없습니다.")

    raw_text = await extract_text(image_bytes)
    if not raw_text.strip():
        raise HTTPException(status_code=400, detail="이미지에서 텍스트를 추출할 수 없습니다.")

    parsed, confidence, warnings = _parse_text(raw_text)
    return SupplementScanResponse(
        raw_text=raw_text,
        parsed=parsed,
        confidence=confidence,
        warnings=warnings,
    )
