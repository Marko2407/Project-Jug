from __future__ import annotations

from datetime import datetime

from sqlalchemy import Enum, ForeignKey
from sqlalchemy.orm import relationship

from app.extensions import db


class MediaAsset(db.Model):
    __tablename__ = "media_asset"

    id = db.Column(db.Integer, primary_key=True)
    uploader_id = db.Column(db.Integer, ForeignKey("user.id", ondelete="SET NULL"))
    kind = db.Column(Enum("IMAGE", "VIDEO", "FILE", name="media_kind"), nullable=False)
    storage_provider = db.Column(Enum("DB", "GDRIVE", "EXTERNAL", name="storage_provider"), nullable=False)
    storage_path = db.Column(db.Text, nullable=False)
    mime_type = db.Column(db.String(255))
    bytes = db.Column(db.Integer)
    checksum = db.Column(db.String(255))
    width = db.Column(db.Integer)
    height = db.Column(db.Integer)
    duration_seconds = db.Column(db.Integer)
    thumbnail_media_id = db.Column(db.Integer, ForeignKey("media_asset.id"))
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    uploader = relationship("User", backref="uploaded_media", foreign_keys=[uploader_id])
    thumbnail = relationship("MediaAsset", remote_side=[id])


from .user import User  # noqa: E402
