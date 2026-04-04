import asyncio
import hashlib
import logging
from datetime import date, datetime, timezone, timedelta
from functools import partial
from fastapi import APIRouter, Depends, HTTPException

logger = logging.getLogger(__name__)
from app.schemas.codef import (
    CodefUserInfo, CodefInitResponse, CodefFetchRequest,
    CodefPrescInitResponse, CodefPrescFetchRequest,
)
from app.core.config import settings
from app.models.codef import ExternalHealthcheckImport, PrescriptionMedication, CodefApiCallLog
from app.models.user import UserProfile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.security import get_current_user_id
from app.db.database import get_db
from app.services import codef_service, s3_service

router = APIRouter(prefix="/users/codef", tags=["CODEF"])


def _extract_two_way(resp: dict) -> dict:
    data = resp.get("data") if isinstance(resp, dict) else None
    # CODEF가 data를 list로 반환하는 경우 첫 번째 요소 사용
    if isinstance(data, list) and len(data) > 0:
        data = data[0]
    if not isinstance(data, dict):
        data = {}
    return {
        "jobIndex": data.get("jobIndex", 0),
        "threadIndex": data.get("threadIndex", 0),
        "jti": data.get("jti", ""),
        "twoWayTimestamp": data.get("twoWayTimestamp", 0),
    }


@router.post("/init", response_model=CodefInitResponse)
async def codef_init(
    user_info: CodefUserInfo,
    _: str = Depends(get_current_user_id),
):
    """CODEF 카카오 인증 요청 (1단계) — 건강검진만"""
    try:
        loop = asyncio.get_running_loop()
        token = await loop.run_in_executor(None, codef_service.get_access_token)

        current_year = date.today().year
        hc_start_year = str(current_year - 4)
        hc_end_year = str(current_year)

        hc_resp = await loop.run_in_executor(
            None,
            partial(
                codef_service.request_health_check,
                token=token,
                user_name=user_info.user_name,
                phone_no=user_info.phone_no,
                identity=user_info.identity,
                nhis_id=user_info.nhis_id,
                start_year=hc_start_year,
                end_year=hc_end_year,
            ),
        )

        return {
            "health_check_two_way": _extract_two_way(hc_resp),
            "token": token,
            "hc_start_year": hc_start_year,
            "hc_end_year": hc_end_year,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("[codef_init] 500 error")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/fetch")
async def codef_fetch(
    req: CodefFetchRequest,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """CODEF 카카오 인증 완료 후 건강검진 + 처방기록 동시 조회 (2단계)"""
    if current_user_id != req.cognito_id:
        raise HTTPException(status_code=403, detail="본인의 건강 데이터만 조회할 수 있습니다.")
    try:
        loop = asyncio.get_running_loop()
        current_year = date.today().year
        hc_start_year = req.hc_start_year or str(current_year - 4)
        hc_end_year = req.hc_end_year or str(current_year)
        presc_start = (date.today() - timedelta(days=365)).strftime("%Y%m%d")
        presc_end = date.today().strftime("%Y%m%d")

        # 건강검진 + 처방기록 동시 조회
        hc_data, presc_resp = await asyncio.gather(
            loop.run_in_executor(
                None,
                partial(
                    codef_service.fetch_health_check,
                    token=req.token,
                    user_name=req.user_info.user_name,
                    phone_no=req.user_info.phone_no,
                    identity=req.user_info.identity,
                    nhis_id=req.user_info.nhis_id,
                    start_year=hc_start_year,
                    end_year=hc_end_year,
                    two_way_info=req.health_check_two_way,
                ),
            ),
            loop.run_in_executor(
                None,
                partial(
                    codef_service.request_prescription,
                    token=req.token,
                    user_name=req.user_info.user_name,
                    phone_no=req.user_info.phone_no,
                    identity=req.user_info.identity,
                    nhis_id=req.user_info.nhis_id,
                    start_date=presc_start,
                    end_date=presc_end,
                ),
            ),
        )

        exam_items = codef_service.parse_health_check(hc_data)
        health_summary = codef_service.extract_health_summary(hc_data)
        medications = codef_service.parse_prescription(presc_resp)

        codef_bucket = settings.s3_codef_bucket_name
        s3_key = s3_service.upload_json(req.cognito_id, "codef_hc_raw.json", {"health_check": hc_data}, bucket=codef_bucket)
        if health_summary is not None:
            s3_service.upload_json(req.cognito_id, "health_summary.json", health_summary, bucket=codef_bucket)
        s3_service.upload_json(req.cognito_id, "codef_presc_raw.json", {"prescription": presc_resp})

        # DB 저장 — 건강검진 + 처방기록 단일 import 레코드
        expires = datetime.now(timezone.utc) + timedelta(days=30)
        import_record = ExternalHealthcheckImport(
            cognito_id=req.cognito_id,
            api_kind="rx_prescription",
            source_s3_url=s3_key,
            exprires_at=expires,
        )
        db.add(import_record)
        await db.flush()

        db.add(CodefApiCallLog(
            import_id=import_record.import_id,
            cognito_id=req.cognito_id,
            api_kind="rx_prescription",
            agred_dt=date.today(),
            phone_hash=hashlib.sha256(req.user_info.phone_no.encode()).hexdigest(),
            codef_request_id=req.health_check_two_way.get("jti") if isinstance(req.health_check_two_way, dict) else None,
            status=True,
            expires_at=datetime.now(timezone.utc) + timedelta(days=365 * 3),
        ))

        period_start = date(int(hc_start_year), 1, 1)
        period_end = date(int(hc_end_year), 12, 31)
        for item in exam_items:
            db.add(PrescriptionMedication(
                import_id=import_record.import_id,
                cognito_id=req.cognito_id,
                api_kind="healthcheck",
                data_type=item["name"],
                name=item["name"],
                value=item["value"],
                unit=item["unit"],
                period_start_dt=period_start,
                period_end_dt=period_end,
                expires_at=expires,
            ))

        presc_period_start = date(int(presc_start[:4]), int(presc_start[4:6]), int(presc_start[6:]))
        presc_period_end = date(int(presc_end[:4]), int(presc_end[4:6]), int(presc_end[6:]))
        for med in medications:
            db.add(PrescriptionMedication(
                import_id=import_record.import_id,
                cognito_id=req.cognito_id,
                api_kind="rx_prescription",
                data_type="drug",
                name=med["name"],
                value=med["dose"],
                period_start_dt=presc_period_start,
                period_end_dt=presc_period_end,
                expires_at=expires,
            ))

        # health_summary의 키/몸무게를 user_profile에 반영 (미설정 시에만)
        if health_summary:
            result = await db.execute(
                select(UserProfile).where(UserProfile.cognito_id == req.cognito_id)
            )
            profile = result.scalar_one_or_none()
            if profile is None:
                profile = UserProfile(cognito_id=req.cognito_id)
                db.add(profile)
            if health_summary.get("height") and not profile.height:
                profile.height = health_summary["height"]
            if health_summary.get("weight") and not profile.weight:
                profile.weight = health_summary["weight"]
            await db.flush()

        await db.commit()
        return {
            "exam_items": exam_items,
            "health_summary": health_summary,
            "medications": medications,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("[codef_fetch] 500 error")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/presc-init")
async def codef_presc_init(
    user_info: CodefUserInfo,
    current_user_id: str = Depends(get_current_user_id),
):
    """처방기록 조회 요청 (1단계) — 처방 API는 2단계 인증 없이 데이터 직접 반환"""
    try:
        loop = asyncio.get_running_loop()
        token = await loop.run_in_executor(None, codef_service.get_access_token)

        current_year = date.today().year
        presc_start = f"{current_year - 1}0101"
        presc_end = date.today().strftime("%Y%m%d")

        presc_resp = await loop.run_in_executor(
            None,
            partial(
                codef_service.request_prescription,
                token=token,
                user_name=user_info.user_name,
                phone_no=user_info.phone_no,
                identity=user_info.identity,
                nhis_id=user_info.nhis_id,
                start_date=presc_start,
                end_date=presc_end,
            ),
        )

        # 처방 API는 init 단계에서 데이터 직접 반환 — S3에 캐싱
        presc_data = presc_resp.get("data") if isinstance(presc_resp, dict) else presc_resp
        s3_service.upload_json(current_user_id, "codef_presc_init_raw.json", {"prescription": presc_data})

        two_way = _extract_two_way(presc_resp)
        return {
            "prescription_two_way": two_way,
            "token": token,
            "presc_start": presc_start,
            "presc_end": presc_end,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("[codef_presc_init] 500 error")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/presc-fetch")
async def codef_presc_fetch(
    req: CodefPrescFetchRequest,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """처방기록 카카오 인증 완료 후 데이터 조회 (처방 2단계)"""
    if current_user_id != req.cognito_id:
        raise HTTPException(status_code=403, detail="본인의 처방 데이터만 조회할 수 있습니다.")
    try:
        loop = asyncio.get_running_loop()
        current_year = date.today().year
        presc_start = req.presc_start or f"{current_year - 1}0101"
        presc_end = req.presc_end or date.today().strftime("%Y%m%d")

        jti = req.prescription_two_way.get("jti", "") if isinstance(req.prescription_two_way, dict) else ""

        if jti:
            # 2단계 인증이 있는 경우 CODEF에서 직접 조회
            presc_data = await loop.run_in_executor(
                None,
                partial(
                    codef_service.fetch_prescription,
                    token=req.token,
                    user_name=req.user_info.user_name,
                    phone_no=req.user_info.phone_no,
                    identity=req.user_info.identity,
                    nhis_id=req.user_info.nhis_id,
                    start_date=presc_start,
                    end_date=presc_end,
                    two_way_info=req.prescription_two_way,
                ),
            )
        else:
            # 처방 API는 init 단계에서 이미 데이터 반환 — S3 캐시 사용
            cached = s3_service.download_json(req.cognito_id, "codef_presc_init_raw.json")
            if cached is None:
                raise HTTPException(status_code=400, detail="처방 데이터를 먼저 요청해주세요.")
            presc_data = cached.get("prescription", cached)

        medications = codef_service.parse_prescription(presc_data)

        s3_key = s3_service.upload_json(req.cognito_id, "codef_presc_raw.json", {"prescription": presc_data})

        # DB 저장
        expires = datetime.now(timezone.utc) + timedelta(days=30)
        import_record = ExternalHealthcheckImport(
            cognito_id=req.cognito_id,
            api_kind="rx_prescription",
            source_s3_url=s3_key,
            exprires_at=expires,
        )
        db.add(import_record)
        await db.flush()  # import_id 확보

        db.add(CodefApiCallLog(
            import_id=import_record.import_id,
            cognito_id=req.cognito_id,
            api_kind="rx_prescription",
            agred_dt=date.today(),
            phone_hash=hashlib.sha256(req.user_info.phone_no.encode()).hexdigest(),
            codef_request_id=req.prescription_two_way.get("jti") if isinstance(req.prescription_two_way, dict) else None,
            status=True,
            expires_at=datetime.now(timezone.utc) + timedelta(days=365 * 3),
        ))

        period_start = date(int(presc_start[:4]), int(presc_start[4:6]), int(presc_start[6:]))
        period_end = date(int(presc_end[:4]), int(presc_end[4:6]), int(presc_end[6:]))
        for med in medications:
            db.add(PrescriptionMedication(
                import_id=import_record.import_id,
                cognito_id=req.cognito_id,
                api_kind="rx_prescription",
                data_type="drug",
                name=med["name"],
                value=med["dose"],
                period_start_dt=period_start,
                period_end_dt=period_end,
                expires_at=expires,
            ))

        await db.commit()
        return {"medications": medications}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("[codef_presc_fetch] 500 error")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health-data/{cognito_id}")
async def get_health_data(
    cognito_id: str,
    current_user_id: str = Depends(get_current_user_id),
):
    """S3에 저장된 건강 요약 데이터 조회"""
    if current_user_id != cognito_id:
        raise HTTPException(status_code=403, detail="본인의 건강 데이터만 조회할 수 있습니다.")
    summary = s3_service.download_json(cognito_id, "health_summary.json", bucket=settings.s3_codef_bucket_name)
    if summary is None:
        # health_summary.json이 없으면 raw 파일에서 추출 시도
        raw = s3_service.download_json(cognito_id, "codef_hc_raw.json", bucket=settings.s3_codef_bucket_name)
        if raw is None:
            raise HTTPException(status_code=404, detail="저장된 건강 데이터가 없습니다.")
        summary = codef_service.extract_health_summary(raw.get("health_check", raw))
    return summary


async def _build_codef_response(cognito_id: str, db: AsyncSession) -> dict:
    """
    cognito_id 기준 healthcheck / rx_prescription 각각 가장 최신 import_id의 데이터 반환.

    healthcheck와 rx_prescription이 같은 import_id로 저장된 경우에도,
    별도 import_id로 저장된 경우에도 모두 정확하게 최신 데이터를 가져옴.
    """
    from sqlalchemy import func, or_, and_

    # api_kind별로 각각 최신 import_id 서브쿼리
    latest_hc_subq = (
        select(func.max(PrescriptionMedication.import_id))
        .join(ExternalHealthcheckImport, PrescriptionMedication.import_id == ExternalHealthcheckImport.import_id)
        .where(
            ExternalHealthcheckImport.cognito_id == cognito_id,
            PrescriptionMedication.api_kind == "healthcheck",
        )
        .scalar_subquery()
    )

    latest_rx_subq = (
        select(func.max(PrescriptionMedication.import_id))
        .join(ExternalHealthcheckImport, PrescriptionMedication.import_id == ExternalHealthcheckImport.import_id)
        .where(
            ExternalHealthcheckImport.cognito_id == cognito_id,
            PrescriptionMedication.api_kind == "rx_prescription",
        )
        .scalar_subquery()
    )

    stmt = select(PrescriptionMedication).where(
        or_(
            and_(PrescriptionMedication.api_kind == "healthcheck",    PrescriptionMedication.import_id == latest_hc_subq),
            and_(PrescriptionMedication.api_kind == "rx_prescription", PrescriptionMedication.import_id == latest_rx_subq),
        )
    )
    result = await db.execute(stmt)
    rows = result.scalars().all()

    codef_health_data = {}
    medication_info = []

    for row in rows:
        if row.api_kind == "rx_prescription":
            medication_info.append({
                "name": row.name,
                "dose": row.value,
                "usage": row.unit,
            })
        elif row.api_kind == "healthcheck":
            key = row.name or row.data_type
            codef_health_data[key] = row.value

    # height, weight, exam_date 등 S3 health_summary로 보완
    summary = await asyncio.to_thread(s3_service.download_json, cognito_id, "health_summary.json") or {}
    codef_health_data.update({k: v for k, v in summary.items() if k not in codef_health_data})

    return {
        "codef_health_data": codef_health_data,
        "medication_info": medication_info,
    }


@router.get("/internal-service/{cognito_id}")
async def get_internal_service_data(
    cognito_id: str,
    db: AsyncSession = Depends(get_db),
):
    """서비스 간 내부 호출 전용 — JWT 인증 없음 (VPC 내부에서만 접근 가능)

    Analysis Backend의 /chat-calculate가 사용자 JWT 없이 CODEF 데이터를 조회할 때 사용.
    외부 인터넷에 노출되지 않도록 API Gateway / ALB에서 차단 필요.
    """
    return await _build_codef_response(cognito_id, db)


@router.get("/internal-call/{cognito_id}")
async def get_internal_call_data(
    cognito_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """내부 서비스 호출용 건강/처방 데이터 조회 (JWT 전달 방식 서비스간 호출)"""
    if current_user_id != cognito_id:
        raise HTTPException(status_code=403, detail="본인의 건강 데이터만 조회할 수 있습니다.")
    return await _build_codef_response(cognito_id, db)
