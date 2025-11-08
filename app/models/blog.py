from __future__ import annotations

from datetime import datetime, date

from sqlalchemy import CheckConstraint, Enum, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db


class BlogPost(db.Model):
    __tablename__ = "blog_post"
    __table_args__ = (
        CheckConstraint("(status <> 'SCHEDULED') OR (scheduled_for IS NOT NULL)", name="ck_blog_post_scheduled"),
        Index("blog_post_status_idx", "status"),
        Index("blog_post_published_at_idx", "published_at"),
        Index("blog_post_author_idx", "author_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="RESTRICT"), nullable=False)
    slug: Mapped[str] = mapped_column(db.Text, nullable=False, unique=True)
    title: Mapped[str] = mapped_column(db.Text, nullable=False)
    summary: Mapped[str | None] = mapped_column(db.Text)
    status: Mapped[str] = mapped_column(
        Enum("DRAFT", "SCHEDULED", "PUBLISHED", "HIDDEN", "ARCHIVED", name="post_status"),
        default="DRAFT",
        nullable=False,
    )
    is_featured: Mapped[bool] = mapped_column(default=False, nullable=False)
    scheduled_for: Mapped[datetime | None] = mapped_column(db.DateTime(timezone=True))
    published_at: Mapped[datetime | None] = mapped_column(db.DateTime(timezone=True))
    hero_media_id: Mapped[int | None] = mapped_column(ForeignKey("media_asset.id"))
    meta_title: Mapped[str | None] = mapped_column(db.Text)
    meta_description: Mapped[str | None] = mapped_column(db.Text)
    reading_time_minutes: Mapped[int | None] = mapped_column(db.Integer)
    lang: Mapped[str | None] = mapped_column(db.String(10), default="hr")
    created_at: Mapped[datetime] = mapped_column(db.DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        db.DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    author: Mapped["User"] = relationship("User", back_populates="posts")
    hero_media: Mapped["MediaAsset" | None] = relationship("MediaAsset", foreign_keys=[hero_media_id])
    chapters: Mapped[list["Chapter"]] = relationship(
        "Chapter", order_by="Chapter.position", cascade="all, delete-orphan", back_populates="post"
    )
    categories: Mapped[list["Category"]] = relationship(
        "Category", secondary="post_category", back_populates="posts"
    )
    metrics_daily: Mapped[list["PostMetricsDaily"]] = relationship(
        "PostMetricsDaily", cascade="all, delete-orphan", back_populates="post"
    )
    visits: Mapped[list["Visit"]] = relationship("Visit", cascade="all, delete-orphan", back_populates="post")


class Chapter(db.Model):
    __tablename__ = "chapter"
    __table_args__ = (
        CheckConstraint("(type <> 'TEXT') OR (text_content IS NOT NULL)", name="ck_chapter_text_content"),
        Index("chapter_post_position_idx", "post_id", "position"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("blog_post.id", ondelete="CASCADE"), nullable=False)
    position: Mapped[int] = mapped_column(nullable=False)
    type: Mapped[str] = mapped_column(Enum("TEXT", "IMAGE", "VIDEO", name="chapter_type"), nullable=False)
    text_content: Mapped[str | None] = mapped_column(db.Text)
    media_id: Mapped[int | None] = mapped_column(ForeignKey("media_asset.id"))
    external_video_url: Mapped[str | None] = mapped_column(db.Text)
    caption: Mapped[str | None] = mapped_column(db.Text)
    alt_text: Mapped[str | None] = mapped_column(db.Text)
    created_at: Mapped[datetime] = mapped_column(db.DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        db.DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    post: Mapped["BlogPost"] = relationship("BlogPost", back_populates="chapters")
    media: Mapped["MediaAsset" | None] = relationship("MediaAsset", foreign_keys=[media_id])


class Visit(db.Model):
    __tablename__ = "visit"
    __table_args__ = (Index("visit_post_time_idx", "post_id", "visited_at"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("blog_post.id", ondelete="CASCADE"), nullable=False)
    visited_at: Mapped[datetime] = mapped_column(db.DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    session_id: Mapped[str | None] = mapped_column(db.String(255))
    ip_hash: Mapped[str | None] = mapped_column(db.String(255))
    user_agent: Mapped[str | None] = mapped_column(db.Text)
    referrer: Mapped[str | None] = mapped_column(db.Text)

    post: Mapped["BlogPost"] = relationship("BlogPost", back_populates="visits")


class PostMetricsDaily(db.Model):
    __tablename__ = "post_metrics_daily"

    post_id: Mapped[int] = mapped_column(ForeignKey("blog_post.id", ondelete="CASCADE"), primary_key=True)
    date: Mapped[date] = mapped_column(primary_key=True)
    views: Mapped[int] = mapped_column(default=0, nullable=False)
    unique_sessions: Mapped[int] = mapped_column(default=0, nullable=False)
    likes: Mapped[int] = mapped_column(default=0, nullable=False)
    shares: Mapped[int] = mapped_column(default=0, nullable=False)

    post: Mapped["BlogPost"] = relationship("BlogPost", back_populates="metrics_daily")


from .media import MediaAsset  # noqa: E402
from .user import User  # noqa: E402
