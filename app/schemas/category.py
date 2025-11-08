from __future__ import annotations

from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field

from app.extensions import db
from app.models import Category


class CategorySchema(SQLAlchemySchema):
    class Meta:
        model = Category
        sqla_session = db.session
        load_instance = True

    id = auto_field(dump_only=True)
    name = auto_field()
    slug = auto_field()
    description = auto_field(load_default=None)
    parent_id = auto_field(load_default=None)
    created_at = auto_field(dump_only=True)
    updated_at = auto_field(dump_only=True)
