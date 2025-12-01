from typing import Any

from sqlalchemy import String, Boolean, Integer, ForeignKey, DateTime
from datetime import datetime, timezone
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models import Base


class UserAuth(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(100), nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_read_only: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return (f"User(id={self.username!r}, full_name={self.full_name!r}, "
                f"email={self.email!r}, hashed_password={self.hashed_password!r}, "
                f"id={self.id!r}, status={self.status!r})")


    def to_dict(self) -> dict[str, Any]:
        return {
            "uuid": self.id,
            "username": self.username,
            "full_name": self.full_name,
            "email": self.email,
            "status": self.status,
        }

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    token_hash: Mapped[str] = mapped_column(String(256), nullable=False, unique=True)  # store hash (sha256)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    plain: Mapped[str] = mapped_column(String, nullable=False)
    
    user = relationship("UserAuth", back_populates="refresh_tokens")