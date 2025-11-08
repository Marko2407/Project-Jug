from __future__ import annotations

from datetime import datetime

from sqlalchemy import ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db


class Category(db.Model):
    __tablename__ = "category"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.Text, nullable=False)
    slug: Mapped[str] = mapped_column(db.Text, nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(db.Text)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("category.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(db.DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        db.DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    parent: Mapped["Category" | None] = relationship("Category", remote_side=[id])
    posts: Mapped[list["BlogPost"]] = relationship("BlogPost", secondary="post_category", back_populates="categories")


class PostCategory(db.Model):
    __tablename__ = "post_category"
    __table_args__ = (
        UniqueConstraint("post_id", "category_id", name="pk_post_category"),
        Index("post_category_category_idx", "category_id"),
    )

    post_id: Mapped[int] = mapped_column(ForeignKey("blog_post.id", ondelete="CASCADE"), primary_key=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("category.id", ondelete="CASCADE"), primary_key=True)
    assigned_at: Mapped[datetime] = mapped_column(
        db.DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )


from .blog import BlogPost  # noqa: E402
