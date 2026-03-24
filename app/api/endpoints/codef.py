from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, join

from app.core.security import get_current_user_id
from app.db.database import get_db
from app.models.codef import ExternalHealthcheckImport, PrescriptionMedication
from app.schemas.codef import CodefUserInfo, CodefInitResponse, CodefFetchRequest
from app.services import codef_service, s3_service

router = APIRouter(prefix="/users/codef", tags=["CODEF"])


@router.post("/init", response_model=CodefInitResponse)
def codef_init(
    user_info: CodefUserInfo,
    _: str = Depends(get_current_user_id),
):
    """CODEF 카카오 인증 요청 (1단계) — 건강검진 + 처방기록 동시 요청"""
    try:
        token = codef_service.get_access_token()

        # 연도 범위 자동 계산 — 최근 5년
        current_year = date.today().year
        hc_start_year = str(current_year - 4)
        hc_end_year = str(current_year)
        presc_start = f"{current_year - 1}0101"
        presc_end = f"{current_year}1231"

        hc_resp = codef_service.request_health_check(
            token=token,
            user_name=user_info.user_name,
            phone_no=user_info.phone_no,
            identity=user_info.identity,
            nhis_id=user_info.nhis_id,
            start_year=hc_start_year,
            end_year=hc_end_year,
        )

        def extract_two_way(resp: dict) -> dict:
            data = resp.get("data") or {}
            return {
                "jobIndex": data.get("jobIndex", 0),
                "threadIndex": data.get("threadIndex", 0),
                "jti": data.get("jti", ""),
                "twoWayTimestamp": data.get("twoWayTimestamp", 0),
            }

        hc_two_way = extract_two_way(hc_resp)

        try:
            presc_resp = codef_service.request_prescription(
                token=token,
                user_name=user_info.user_name,
                phone_no=user_info.phone_no,
                identity=user_info.identity,
                nhis_id=user_info.nhis_id,
                start_date=presc_start,
                end_date=presc_end,
            )
            presc_two_way = extract_two_way(presc_resp)
        except Exception:
            presc_two_way = {"jobIndex": 0, "threadIndex": 0, "jti": "", "twoWayTimestamp": 0}

        return {
            "health_check_two_way": hc_two_way,
            "prescription_two_way": presc_two_way,
            "token": token,
            "hc_start_year": hc_start_year,
            "hc_end_year": hc_end_year,
            "presc_start": presc_start,
            "presc_end": presc_end,
        }
    except HTTPException as e:
        print(e)
        raise
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/fetch")
def codef_fetch(
    req: CodefFetchRequest,
    current_user_id: str = Depends(get_current_user_id),
):
    """CODEF 카카오 인증 완료 후 데이터 조회 (2단계)"""
    if current_user_id != req.cognito_id:
        raise HTTPException(status_code=403, detail="본인의 건강 데이터만 조회할 수 있습니다.")
    try:
        current_year = date.today().year
        hc_start_year = req.hc_start_year or str(current_year - 4)
        hc_end_year = req.hc_end_year or str(current_year)
        presc_start = req.presc_start or f"{current_year - 1}0101"
        presc_end = req.presc_end or f"{current_year}1231"

        hc_data = codef_service.fetch_health_check(
            token=req.token,
            user_name=req.user_info.user_name,
            phone_no=req.user_info.phone_no,
            identity=req.user_info.identity,
            nhis_id=req.user_info.nhis_id,
            start_year=hc_start_year,
            end_year=hc_end_year,
            two_way_info=req.health_check_two_way,
        )
        presc_data = codef_service.fetch_prescription(
            token=req.token,
            user_name=req.user_info.user_name,
            phone_no=req.user_info.phone_no,
            identity=req.user_info.identity,
            nhis_id=req.user_info.nhis_id,
            start_date=presc_start,
            end_date=presc_end,
            two_way_info=req.prescription_two_way,
        )

        exam_items = codef_service.parse_health_check(hc_data)
        medications = codef_service.parse_prescription(presc_data)
        health_summary = codef_service.extract_health_summary(hc_data)

        s3_service.upload_json(req.cognito_id, "codef_raw.json", {
            "health_check": hc_data,
            "prescription": presc_data,
        })
        if health_summary:
<<<<<<< Updated upstream
            s3_service.upload_json(req.cognito_id, "health_summary.json", health_summary)
=======
            s3_service.upload_json(req.cognito_id, "health_summary.json", health_summary, bucket=codef_bucket)

        # DB 저장
        expires = datetime.now(timezone.utc) + timedelta(days=30)
        import_record = ExternalHealthcheckImport(
            cognito_id=req.cognito_id,
            api_kind="healthcheck",
            source_s3_url=s3_key,
            exprires_at=expires,
        )
        db.add(import_record)
        await db.flush()  # import_id 확보

        db.add(CodefApiCallLog(
            import_id=import_record.import_id,
            api_kind="healthcheck",
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
                api_kind="healthcheck",
                data_type=item["name"],
                name=item["name"],
                value=item["value"],
                unit=item["unit"],
                period_start_dt=period_start,
                period_end_dt=period_end,
                expires_at=expires,
            ))
>>>>>>> Stashed changes

        return {
            "exam_items": exam_items,
            "medications": medications,
            "health_summary": health_summary,
        }
<<<<<<< Updated upstream
=======
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/presc-init", response_model=CodefPrescInitResponse)
async def codef_presc_init(
    user_info: CodefUserInfo,
    _: str = Depends(get_current_user_id),
):
    """처방기록 카카오 인증 요청 (처방 1단계)"""
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

        return {
            "prescription_two_way": _extract_two_way(presc_resp),
            "token": token,
            "presc_start": presc_start,
            "presc_end": presc_end,
        }
    except HTTPException:
        raise
    except Exception as e:
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

        medications = codef_service.parse_prescription(presc_data)

        s3_key = s3_service.upload_json(req.cognito_id, "codef_presc_raw.json", {"prescription": presc_data}, bucket=settings.s3_codef_bucket_name)

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
                api_kind="rx_prescription",
                data_type="drug",
                name=med["name"],
                value=med["dose"],
                period_start_dt=period_start,
                period_end_dt=period_end,
                expires_at=expires,
            ))

        return {"medications": medications, "success": True}
    except HTTPException:
        raise
>>>>>>> Stashed changes
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health-data/{cognito_id}")
def get_health_data(
    cognito_id: str,
    current_user_id: str = Depends(get_current_user_id),
):
    """S3에 저장된 건강 요약 데이터 조회"""
    if current_user_id != cognito_id:
        raise HTTPException(status_code=403, detail="본인의 건강 데이터만 조회할 수 있습니다.")
    summary = s3_service.download_json(cognito_id, "health_summary.json")
    if summary is None:
        raise HTTPException(status_code=404, detail="저장된 건강 데이터가 없습니다.")
    return summary


@router.get("/internal-call/{cognito_id}")
async def get_internal_call_data(
    cognito_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """내부 서비스 호출용 건강/처방 데이터 조회 (JWT 전달 방식 서비스간 호출)

    prescription_medications 테이블에서 api_kind로 구분하여 조회:
    - codef_health_data: 건강검진 수치 (api_kind == 'healthcheck')
    - medication_info: 처방 의약품 (api_kind == 'rx_prescription')
    """
    if current_user_id != cognito_id:
        raise HTTPException(status_code=403, detail="본인의 건강 데이터만 조회할 수 있습니다.")

    # external_healthcheck_import JOIN prescription_medications
    stmt = (
        select(PrescriptionMedication)
        .join(
            ExternalHealthcheckImport,
            PrescriptionMedication.import_id == ExternalHealthcheckImport.import_id,
        )
        .where(ExternalHealthcheckImport.cognito_id == cognito_id)
        .order_by(PrescriptionMedication.created_at.desc())
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
                "unit": row.unit,
            })
        elif row.api_kind == "healthcheck":
            # 혈압, 혈당, 콜레스테롤 등 검진 수치
            key = row.name or row.data_type
            codef_health_data[key] = row.value

    # height, weight, exam_date는 S3 health_summary에서 보완
    summary = s3_service.download_json(cognito_id, "health_summary.json") or {}
    codef_health_data.update({k: v for k, v in summary.items() if k not in codef_health_data})

    return {
        "codef_health_data": codef_health_data,
        "medication_info": medication_info,
    }
