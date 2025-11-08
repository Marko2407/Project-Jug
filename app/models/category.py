from __future__ import annotations

from datetime import datetime

from sqlalchemy import ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import relationship

from app.extensions import db


class Category(db.Model):
    __tablename__ = "category"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    slug = db.Column(db.Text, nullable=False, unique=True)
    description = db.Column(db.Text)
    parent_id = db.Column(db.Integer, ForeignKey("category.id", ondelete="SET NULL"))
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    parent = relationship("Category", remote_side=[id])
    posts = relationship("BlogPost", secondary="post_category", back_populates="categories")


class PostCategory(db.Model):
    __tablename__ = "post_category"
    __table_args__ = (
        UniqueConstraint("post_id", "category_id", name="pk_post_category"),
        Index("post_category_category_idx", "category_id"),
    )

    post_id = db.Column(db.Integer, ForeignKey("blog_post.id", ondelete="CASCADE"), primary_key=True)
    category_id = db.Column(db.Integer, ForeignKey("category.id", ondelete="CASCADE"), primary_key=True)
    assigned_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, nullable=False)


from .blog import BlogPost  # noqa: E402
