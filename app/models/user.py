from __future__ import annotations

from datetime import datetime

from sqlalchemy import Enum, ForeignKey
from sqlalchemy.orm import relationship

from app.extensions import db


class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Text, unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    display_name = db.Column(db.Text, nullable=False)
    role = db.Column(Enum("ADMIN", name="user_role"), default="ADMIN", nullable=False)
    status = db.Column(Enum("ACTIVE", "DISABLED", name="user_status"), default="ACTIVE", nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    profile = relationship("Profile", back_populates="user", uselist=False, cascade="all, delete")
    posts = relationship("BlogPost", back_populates="author")


class Profile(db.Model):
    __tablename__ = "profile"

    user_id = db.Column(db.Integer, ForeignKey("user.id", ondelete="CASCADE"), primary_key=True)
    title = db.Column(db.Text)
    bio = db.Column(db.Text)
    avatar_media_id = db.Column(db.Integer, ForeignKey("media_asset.id"))
    website_url = db.Column(db.Text)
    instagram = db.Column(db.Text)
    facebook = db.Column(db.Text)
    youtube = db.Column(db.Text)
    phone = db.Column(db.Text)
    location = db.Column(db.Text)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="profile")
    avatar = relationship("MediaAsset", foreign_keys=[avatar_media_id])


from .blog import BlogPost  # noqa: E402  circular import guard
from .media import MediaAsset  # noqa: E402
