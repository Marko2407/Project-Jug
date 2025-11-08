from __future__ import annotations

from datetime import datetime

from sqlalchemy import Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db


class MediaAsset(db.Model):
    __tablename__ = "media_asset"

    id: Mapped[int] = mapped_column(primary_key=True)
    uploader_id: Mapped[int | None] = mapped_column(ForeignKey("user.id", ondelete="SET NULL"))
    kind: Mapped[str] = mapped_column(Enum("IMAGE", "VIDEO", "FILE", name="media_kind"), nullable=False)
    storage_provider: Mapped[str] = mapped_column(Enum("DB", "GDRIVE", "EXTERNAL", name="storage_provider"), nullable=False)
    storage_path: Mapped[str] = mapped_column(db.Text, nullable=False)
    mime_type: Mapped[str | None]
    bytes: Mapped[int | None]
    checksum: Mapped[str | None]
    width: Mapped[int | None]
    height: Mapped[int | None]
    duration_seconds: Mapped[int | None]
    thumbnail_media_id: Mapped[int | None] = mapped_column(ForeignKey("media_asset.id"))
    created_at: Mapped[datetime] = mapped_column(db.DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(db.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    uploader: Mapped["User" | None] = relationship("User", backref="uploaded_media", foreign_keys=[uploader_id])
    thumbnail: Mapped["MediaAsset" | None] = relationship(remote_side=[id])


from .user import User  # noqa: E402
