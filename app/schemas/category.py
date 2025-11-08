from __future__ import annotations

from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from app.extensions import db
from app.models import Category


class CategorySchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Category
        sqla_session = db.session
        include_fk = True
        load_instance = True

    parent_id = fields.Integer(load_default=None)
