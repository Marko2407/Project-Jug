from __future__ import annotations

from marshmallow import fields, validate
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field

from app.extensions import db
from app.models import BlogPost, Chapter
from .category import CategorySchema


class ChapterSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Chapter
        sqla_session = db.session
        include_fk = True
        load_instance = True

    type = auto_field(validate=validate.OneOf(["TEXT", "IMAGE", "VIDEO"]))
    media_id = fields.Integer(load_default=None)


class BlogPostSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = BlogPost
        sqla_session = db.session
        include_relationships = True
        include_fk = True
        load_instance = True

    status = auto_field(validate=validate.OneOf(["DRAFT", "SCHEDULED", "PUBLISHED", "HIDDEN", "ARCHIVED"]))
    is_featured = fields.Boolean(load_default=False)
    chapters = fields.List(fields.Nested(ChapterSchema), load_default=list)
    category_ids = fields.List(fields.Integer(), load_default=list, load_only=True)
    categories = fields.List(fields.Pluck(CategorySchema, "slug"), dump_only=True)
    hero_media_id = fields.Integer(load_default=None)

    published_at = fields.AwareDateTime(load_default=None)
    scheduled_for = fields.AwareDateTime(load_default=None)
