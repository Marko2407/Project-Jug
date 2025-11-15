from __future__ import annotations

import logging
from typing import Any

from flask import Flask
from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from .extensions import db, migrate
from .routes import register_blueprints
from .services.storage import StorageError, get_storage_backend


load_dotenv()


def create_app(config: dict[str, Any] | None = None) -> Flask:
    """Application factory used by Flask."""
    app = Flask(__name__)

    default_config: dict[str, Any] = {
        "SQLALCHEMY_DATABASE_URI": "postgresql+psycopg2://postgres:postgres@localhost:5432/blog",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "JSON_SORT_KEYS": False,
        "ADMIN_JWT_SECRET": "change-me",
        "ADMIN_JWT_ALGORITHM": "HS256",
        "MEDIA_STORAGE_BACKEND": "gdrive",
        "GOOGLE_DRIVE_SERVICE_ACCOUNT": "service-account.json",
        "GOOGLE_DRIVE_UPLOAD_FOLDER_ID": None,
        "SCHEDULER_TIMEZONE": "UTC",
        "POST_FEATURED_LIMIT": 6,
        "POST_RECENT_LIMIT": 12,
    }

    app.config.from_mapping(default_config)

    if config:
        app.config.update(config)

    init_extensions(app)
    register_blueprints(app)
    configure_logging(app)

    with app.app_context():
        _ensure_chapter_title_column(app)

        # Ensure storage backend is initialized early to fail fast on misconfiguration.
        try:
            get_storage_backend(app.config)
        except StorageError as exc:
            app.logger.warning("Storage backend initialization failed: %s", exc)

    return app


def init_extensions(app: Flask) -> None:
    db.init_app(app)
    migrate.init_app(app, db)


def configure_logging(app: Flask) -> None:
    if app.debug or app.testing:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    logging.getLogger("googleapiclient.discovery_cache").setLevel(logging.ERROR)


__all__ = ["create_app"]


def _ensure_chapter_title_column(app: Flask) -> None:
    try:
        db.session.execute(text("ALTER TABLE IF EXISTS chapter ADD COLUMN IF NOT EXISTS title TEXT"))
        db.session.commit()
    except SQLAlchemyError as exc:
        app.logger.warning("Failed to ensure chapter.title column exists: %s", exc)
        db.session.rollback()
