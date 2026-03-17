from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import String, DateTime, Boolean, Text, Date, Numeric, Integer, BigInteger
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.database import Base


class User(Base):
    """Users 테이블 - 인증 서비스(Cognito)와 연동"""
    __tablename__ = "Users"

    cognito_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class UserProfile(Base):
    """user_profile 테이블 - 유저 프로필 정보"""
    __tablename__ = "user_profile"

    profile_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    cognito_id: Mapped[str] = mapped_column(String(36), nullable=False)
    name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    birth_dt: Mapped[date | None] = mapped_column(Date, nullable=True)
    gender: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 남:0, 여:1
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    height: Mapped[Decimal | None] = mapped_column(Numeric(5, 1), nullable=True)
    weight: Mapped[Decimal | None] = mapped_column(Numeric(5, 1), nullable=True)
    allergies: Mapped[str | None] = mapped_column(String(255), nullable=True)
    chron_diseases: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class UserConditionSnapshot(Base):
    """user_condition_snapshots 테이블"""
    __tablename__ = "user_condition_snapshots"

    snapshot_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    cognito_id: Mapped[str] = mapped_column(String(36), nullable=False)
    status: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Consent(Base):
    """consents 테이블"""
    __tablename__ = "consents"

    consent_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    cognito_id: Mapped[str] = mapped_column(String(36), nullable=False)
    type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    agree_dt: Mapped[date | None] = mapped_column(Date, nullable=True)
