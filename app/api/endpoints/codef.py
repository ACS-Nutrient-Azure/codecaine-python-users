import asyncio
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from functools import partial

from app.core.security import get_current_user_id
from app.schemas.codef import CodefUserInfo, CodefInitResponse, CodefFetchRequest
from app.services import codef_service, s3_service

router = APIRouter(prefix="/users/codef", tags=["CODEF"])


@router.post("/init", response_model=CodefInitResponse)
async def codef_init(
    user_info: CodefUserInfo,
    _: str = Depends(get_current_user_id),
):
    """CODEF 카카오 인증 요청 (1단계) — 건강검진 + 처방기록 동시 요청"""
    try:
        loop = asyncio.get_running_loop()
        token = await loop.run_in_executor(None, codef_service.get_access_token)

        # 연도 범위 자동 계산 — 최근 5년
        current_year = date.today().year
        hc_start_year = str(current_year - 4)
        hc_end_year = str(current_year)
        presc_start = f"{current_year - 1}0101"
        presc_end = f"{current_year}1231"

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
async def codef_fetch(
    req: CodefFetchRequest,
    current_user_id: str = Depends(get_current_user_id),
):
    """CODEF 카카오 인증 완료 후 데이터 조회 (2단계)"""
    if current_user_id != req.cognito_id:
        raise HTTPException(status_code=403, detail="본인의 건강 데이터만 조회할 수 있습니다.")
    try:
        loop = asyncio.get_running_loop()
        current_year = date.today().year
        hc_start_year = req.hc_start_year or str(current_year - 4)
        hc_end_year = req.hc_end_year or str(current_year)
        presc_start = req.presc_start or f"{current_year - 1}0101"
        presc_end = req.presc_end or f"{current_year}1231"

        hc_data = await loop.run_in_executor(
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
        )
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

        exam_items = codef_service.parse_health_check(hc_data)
        medications = codef_service.parse_prescription(presc_data)
        health_summary = codef_service.extract_health_summary(hc_data)

        s3_service.upload_json(req.cognito_id, "codef_raw.json", {
            "health_check": hc_data,
            "prescription": presc_data,
        })
        if health_summary:
            s3_service.upload_json(req.cognito_id, "health_summary.json", health_summary)

        return {
            "exam_items": exam_items,
            "medications": medications,
            "health_summary": health_summary,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health-data/{cognito_id}")
async def get_health_data(
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
