from __future__ import annotations

from marshmallow import fields, validate
from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field

from app.extensions import db
from app.models import MediaAsset


class MediaAssetSchema(SQLAlchemySchema):
    class Meta:
        model = MediaAsset
        sqla_session = db.session
        load_instance = True

    id = auto_field(dump_only=True)
    uploader_id = auto_field(load_default=None)
    kind = fields.String(validate=validate.OneOf(["IMAGE", "VIDEO", "FILE"]))
    storage_provider = fields.String(validate=validate.OneOf(["DB", "GDRIVE", "EXTERNAL"]))
    storage_path = auto_field()
    mime_type = auto_field(load_default=None)
    bytes = auto_field(load_default=None)
    checksum = auto_field(load_default=None)
    width = auto_field(load_default=None)
    height = auto_field(load_default=None)
    duration_seconds = auto_field(load_default=None)
    thumbnail_media_id = auto_field(load_default=None)
    created_at = auto_field(dump_only=True)
    updated_at = auto_field(dump_only=True)
