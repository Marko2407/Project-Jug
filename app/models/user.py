from __future__ import annotations

from datetime import datetime

from sqlalchemy import Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db


class User(db.Model):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(db.Text, unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(db.Text, nullable=False)
    display_name: Mapped[str] = mapped_column(db.Text, nullable=False)
    role: Mapped[str] = mapped_column(Enum("ADMIN", name="user_role"), default="ADMIN", nullable=False)
    status: Mapped[str] = mapped_column(Enum("ACTIVE", "DISABLED", name="user_status"), default="ACTIVE", nullable=False)
    created_at: Mapped[datetime] = mapped_column(db.DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(db.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    profile: Mapped["Profile"] = relationship(back_populates="user", uselist=False, cascade="all, delete")
    posts: Mapped[list["BlogPost"]] = relationship("BlogPost", back_populates="author")


class Profile(db.Model):
    __tablename__ = "profile"

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), primary_key=True)
    title: Mapped[str | None]
    bio: Mapped[str | None]
    avatar_media_id: Mapped[int | None] = mapped_column(ForeignKey("media_asset.id"))
    website_url: Mapped[str | None]
    instagram: Mapped[str | None]
    facebook: Mapped[str | None]
    youtube: Mapped[str | None]
    phone: Mapped[str | None]
    location: Mapped[str | None]
    created_at: Mapped[datetime] = mapped_column(db.DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(db.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user: Mapped[User] = relationship(back_populates="profile")
    avatar: Mapped["MediaAsset" | None] = relationship("MediaAsset", foreign_keys=[avatar_media_id])


from .blog import BlogPost  # noqa: E402  circular import guard
from .media import MediaAsset  # noqa: E402
