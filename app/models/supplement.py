from datetime import datetime, date
from sqlalchemy import String, DateTime, Boolean, Integer, BigInteger, Date
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.database import Base


class CurrentSupplement(Base):
    """1-7. 복용중인 영양제 테이블"""
    __tablename__ = "1-7. 복용중인 영양제"

    current_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    cognito_id: Mapped[str] = mapped_column(String(36), nullable=False)
    product_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    serving_amount: Mapped[int | None] = mapped_column(Integer, nullable=True)
    serving_per_day: Mapped[int | None] = mapped_column(Integer, nullable=True)
    daily_total_amount: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_quantity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    ingredients: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    purchased_dt: Mapped[date | None] = mapped_column(Date, nullable=True)
    estimated_end_dt: Mapped[date | None] = mapped_column(Date, nullable=True)
    start_dt: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_dt: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class IntakeSupplement(Base):
    """intake_supplements 테이블"""
    __tablename__ = "intake_supplements"

    cognito_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    itk_product_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    itk_serving_amount: Mapped[int | None] = mapped_column(Integer, nullable=True)
    itk_serving_per_day: Mapped[int | None] = mapped_column(Integer, nullable=True)
    itk_daily_total_amount: Mapped[int | None] = mapped_column(Integer, nullable=True)
    itk_total_quantity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    itk_purchased_dt: Mapped[date | None] = mapped_column(Date, nullable=True)
    itk_estimated_end_dt: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
