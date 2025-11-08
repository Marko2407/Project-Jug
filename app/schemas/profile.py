from __future__ import annotations

from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field

from app.extensions import db
from app.models import Profile


class ProfileSchema(SQLAlchemySchema):
    class Meta:
        model = Profile
        sqla_session = db.session
        load_instance = True

    user_id = auto_field()
    title = auto_field(load_default=None)
    bio = auto_field(load_default=None)
    avatar_media_id = auto_field(load_default=None)
    website_url = auto_field(load_default=None)
    instagram = auto_field(load_default=None)
    facebook = auto_field(load_default=None)
    youtube = auto_field(load_default=None)
    phone = auto_field(load_default=None)
    location = auto_field(load_default=None)
    created_at = auto_field(dump_only=True)
    updated_at = auto_field(dump_only=True)
