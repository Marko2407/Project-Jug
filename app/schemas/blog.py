from __future__ import annotations

from marshmallow import fields, validate
from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field

from app.extensions import db
from app.models import BlogPost, Chapter
from .category import CategorySchema


class ChapterSchema(SQLAlchemySchema):
    class Meta:
        model = Chapter
        sqla_session = db.session
        load_instance = True

    id = auto_field(dump_only=True)
    post_id = auto_field(dump_only=True)
    position = auto_field()
    type = auto_field(validate=validate.OneOf(["TEXT", "IMAGE", "VIDEO"]))
    title = auto_field(load_default=None)
    text_content = auto_field(load_default=None)
    media_id = auto_field(load_default=None)
    external_video_url = auto_field(load_default=None)
    caption = auto_field(load_default=None)
    alt_text = auto_field(load_default=None)
    created_at = auto_field(dump_only=True)
    updated_at = auto_field(dump_only=True)


class BlogPostSchema(SQLAlchemySchema):
    class Meta:
        model = BlogPost
        sqla_session = db.session
        load_instance = True

    id = auto_field(dump_only=True)
    author_id = fields.Integer(required=False, allow_none=True)
    slug = auto_field()
    title = auto_field()
    summary = auto_field(load_default=None)
    status = auto_field(validate=validate.OneOf(["DRAFT", "SCHEDULED", "PUBLISHED", "HIDDEN", "ARCHIVED"]))
    is_featured = fields.Boolean(load_default=False)
    scheduled_for = fields.AwareDateTime(load_default=None)
    published_at = fields.AwareDateTime(load_default=None)
    hero_media_id = auto_field(load_default=None)
    meta_title = auto_field(load_default=None)
    meta_description = auto_field(load_default=None)
    reading_time_minutes = auto_field(load_default=None)
    lang = auto_field()
    created_at = auto_field(dump_only=True)
    updated_at = auto_field(dump_only=True)
    chapters = fields.List(fields.Nested(ChapterSchema), load_default=list)
    category_ids = fields.List(fields.Integer(), load_default=list, load_only=True)
    categories = fields.List(fields.Pluck(CategorySchema, "slug"), dump_only=True)
