from datetime import datetime
from sqlalchemy import String, DateTime, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.database import Base


class User(Base):
    """
    마이페이지 서비스가 관리하는 유저 프로필 테이블.
    
    MSA 구조이므로 인증(Auth 서비스)과 분리되어 있음.
    user_id는 Auth 서비스의 ID를 그대로 사용 (UUID).
    """
    __tablename__ = "users"

    # Auth 서비스에서 발급한 UUID를 PK로 사용
    id: Mapped[str] = mapped_column(String(36), primary_key=True)

    # 프로필 정보
    nickname: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    profile_image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    bio: Mapped[str | None] = mapped_column(String(200), nullable=True)

    # 건강 정보 (영양제 추천 서비스와 연관)
    age: Mapped[int | None] = mapped_column(nullable=True)
    gender: Mapped[str | None] = mapped_column(String(10), nullable=True)  # male | female | other
    health_goals: Mapped[str | None] = mapped_column(Text, nullable=True)   # JSON 문자열로 저장

    # 알림 설정
    push_notification: Mapped[bool] = mapped_column(Boolean, default=True)
    email_notification: Mapped[bool] = mapped_column(Boolean, default=True)

    # 계정 상태
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # 타임스탬프
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
