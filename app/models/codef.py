from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import String, DateTime, Boolean, Date, Numeric, BigInteger
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.database import Base


class ExternalHealthcheckImport(Base):
    """external_healthcheck_import 테이블"""
    __tablename__ = "external_healthcheck_import"

    import_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    cognito_id: Mapped[str] = mapped_column(String(36), nullable=False)
    api_kind: Mapped[str | None] = mapped_column(String(50), nullable=True)       # healthcheck/rx_prescription
    source_s3_url: Mapped[str | None] = mapped_column(String, nullable=True)      # s3 경로
    exprires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)  # 오타 그대로 유지, 1개월 후 삭제
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())


class CodefApiCallLog(Base):
    """codef_api_call_log 테이블"""
    __tablename__ = "codef_api_call_log"

    log_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    import_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    api_kind: Mapped[str | None] = mapped_column(String(50), nullable=True)       # healthcheck/rx_prescription
    agred_dt: Mapped[date | None] = mapped_column(Date, nullable=True)            # 오타 그대로 유지, YYYY-MM-DD
    phone_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)     # 해시암호화
    codef_request_id: Mapped[str | None] = mapped_column(String(255), nullable=True)  # requestID(transactionID)
    status: Mapped[bool | None] = mapped_column(Boolean, nullable=True)           # TRUE=성공
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)  # 3년 보관 후 삭제
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class PrescriptionMedication(Base):
    """prescription_medications 테이블"""
    __tablename__ = "prescription_medications"

    med_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    import_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    api_kind: Mapped[str | None] = mapped_column(String(50), nullable=True)       # healthcheck/rx_prescription
    data_type: Mapped[str | None] = mapped_column(String(50), nullable=True)      # drug, blood_pressure, cholesterol, glucose 등
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)          # 약품명/혈압/혈당 등
    value: Mapped[str | None] = mapped_column(String(255), nullable=True)         # 100mg 1T / 140 / 220 등
    unit: Mapped[str | None] = mapped_column(String(20), nullable=True)           # mg / mmHg / mg/dL
    period_start_dt: Mapped[date | None] = mapped_column(Date, nullable=True)
    period_end_dt: Mapped[date | None] = mapped_column(Date, nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)  # 1개월 후 삭제
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class UnitConvertor(Base):
    """unit_convertor 테이블"""
    __tablename__ = "unit_convertor"

    vitamin_name: Mapped[str] = mapped_column(String(255), primary_key=True)
    convert_unit: Mapped[Decimal | None] = mapped_column(Numeric(12, 8), nullable=True)  # e.g. 0.0005
