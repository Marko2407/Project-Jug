from __future__ import annotations

from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from app.extensions import db
from app.models import Profile


class ProfileSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Profile
        sqla_session = db.session
        include_fk = True
        load_instance = True
