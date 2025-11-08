from __future__ import annotations

from datetime import datetime, date

from sqlalchemy import CheckConstraint, Enum, ForeignKey, Index
from sqlalchemy.orm import relationship

from app.extensions import db


class BlogPost(db.Model):
    __tablename__ = "blog_post"
    __table_args__ = (
        CheckConstraint("(status <> 'SCHEDULED') OR (scheduled_for IS NOT NULL)", name="ck_blog_post_scheduled"),
        Index("blog_post_status_idx", "status"),
        Index("blog_post_published_at_idx", "published_at"),
        Index("blog_post_author_idx", "author_id"),
    )

    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, ForeignKey("user.id", ondelete="RESTRICT"), nullable=False)
    slug = db.Column(db.Text, nullable=False, unique=True)
    title = db.Column(db.Text, nullable=False)
    summary = db.Column(db.Text)
    status = db.Column(Enum("DRAFT", "SCHEDULED", "PUBLISHED", "HIDDEN", "ARCHIVED", name="post_status"), default="DRAFT", nullable=False)
    is_featured = db.Column(db.Boolean, default=False, nullable=False)
    scheduled_for = db.Column(db.DateTime(timezone=True))
    published_at = db.Column(db.DateTime(timezone=True))
    hero_media_id = db.Column(db.Integer, ForeignKey("media_asset.id"))
    meta_title = db.Column(db.Text)
    meta_description = db.Column(db.Text)
    reading_time_minutes = db.Column(db.Integer)
    lang = db.Column(db.String(10), default="hr")
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    author = relationship("User", back_populates="posts")
    hero_media = relationship("MediaAsset", foreign_keys=[hero_media_id])
    chapters = relationship("Chapter", order_by="Chapter.position", cascade="all, delete-orphan", back_populates="post")
    categories = relationship("Category", secondary="post_category", back_populates="posts")
    metrics_daily = relationship("PostMetricsDaily", cascade="all, delete-orphan", back_populates="post")
    visits = relationship("Visit", cascade="all, delete-orphan", back_populates="post")


class Chapter(db.Model):
    __tablename__ = "chapter"
    __table_args__ = (
        CheckConstraint("(type <> 'TEXT') OR (text_content IS NOT NULL)", name="ck_chapter_text_content"),
        Index("chapter_post_position_idx", "post_id", "position"),
    )

    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, ForeignKey("blog_post.id", ondelete="CASCADE"), nullable=False)
    position = db.Column(db.Integer, nullable=False)
    type = db.Column(Enum("TEXT", "IMAGE", "VIDEO", name="chapter_type"), nullable=False)
    text_content = db.Column(db.Text)
    media_id = db.Column(db.Integer, ForeignKey("media_asset.id"))
    external_video_url = db.Column(db.Text)
    caption = db.Column(db.Text)
    alt_text = db.Column(db.Text)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    post = relationship("BlogPost", back_populates="chapters")
    media = relationship("MediaAsset", foreign_keys=[media_id])


class Visit(db.Model):
    __tablename__ = "visit"
    __table_args__ = (Index("visit_post_time_idx", "post_id", "visited_at"),)

    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, ForeignKey("blog_post.id", ondelete="CASCADE"), nullable=False)
    visited_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    session_id = db.Column(db.String(255))
    ip_hash = db.Column(db.String(255))
    user_agent = db.Column(db.Text)
    referrer = db.Column(db.Text)

    post = relationship("BlogPost", back_populates="visits")


class PostMetricsDaily(db.Model):
    __tablename__ = "post_metrics_daily"

    post_id = db.Column(db.Integer, ForeignKey("blog_post.id", ondelete="CASCADE"), primary_key=True)
    date = db.Column(db.Date, primary_key=True)
    views = db.Column(db.Integer, default=0, nullable=False)
    unique_sessions = db.Column(db.Integer, default=0, nullable=False)
    likes = db.Column(db.Integer, default=0, nullable=False)
    shares = db.Column(db.Integer, default=0, nullable=False)

    post = relationship("BlogPost", back_populates="metrics_daily")


from .media import MediaAsset  # noqa: E402
from .user import User  # noqa: E402
