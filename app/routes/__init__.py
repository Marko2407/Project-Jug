from __future__ import annotations

from flask import Blueprint, Flask

from .admin import admin_bp
from .public import public_bp


def register_blueprints(app: Flask) -> None:
    app.register_blueprint(public_bp, url_prefix="/api")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")


__all__ = ["register_blueprints"]
