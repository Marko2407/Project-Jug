from __future__ import annotations

from marshmallow import fields, validate
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from app.extensions import db
from app.models import MediaAsset


class MediaAssetSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = MediaAsset
        sqla_session = db.session
        include_fk = True
        load_instance = True

    kind = fields.String(validate=validate.OneOf(["IMAGE", "VIDEO", "FILE"]))
    storage_provider = fields.String(validate=validate.OneOf(["DB", "GDRIVE", "EXTERNAL"]))
