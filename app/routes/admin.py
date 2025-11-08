from __future__ import annotations

from datetime import datetime

import jwt
from flask import Blueprint, current_app, g, jsonify, request
from jwt import InvalidTokenError
from sqlalchemy import select

from app.extensions import db
from app.models import BlogPost, Category, Chapter, MediaAsset, User
from app.schemas import BlogPostSchema, CategorySchema, MediaAssetSchema
from app.services.storage import StorageError, get_storage_backend

admin_bp = Blueprint("admin", __name__)


blog_post_schema = BlogPostSchema()
blog_post_list_schema = BlogPostSchema(many=True)
category_schema = CategorySchema()
category_list_schema = CategorySchema(many=True)
media_schema = MediaAssetSchema()


def require_admin_jwt() -> dict:
    from flask import abort

    auth_header = request.headers.get("Authorization", "")
    if not auth_header.lower().startswith("bearer "):
        abort(401, description="Missing bearer token")

    token = auth_header.split(" ", 1)[1].strip()
    if not token:
        abort(401, description="Missing bearer token")

    secret = current_app.config.get("ADMIN_JWT_SECRET")
    if not secret:
        current_app.logger.error("ADMIN_JWT_SECRET is not configured")
        abort(500, description="Admin authentication misconfigured")

    algorithms = current_app.config.get("ADMIN_JWT_ALGORITHM", "HS256")
    if isinstance(algorithms, str):
        algorithms = [algorithms]

    try:
        claims = jwt.decode(token, secret, algorithms=algorithms)
    except InvalidTokenError as exc:
        current_app.logger.warning("Invalid admin JWT: %s", exc)
        abort(401, description="Invalid admin token")

    if claims.get("role") != "admin":
        abort(403, description="Admin privileges required")

    return claims


@admin_bp.before_request
def _authenticate_admin() -> None:
    g.admin_claims = require_admin_jwt()


@admin_bp.post("/posts")
def create_post():
    payload = request.get_json() or {}
    post = blog_post_schema.load(payload)
    post.author_id = payload.get("author_id") or _ensure_default_admin_user().id

    chapters_payload = payload.get("chapters", [])
    if chapters_payload and not isinstance(chapters_payload, list):
        return jsonify({"message": "chapters must be a list"}), 400
    post.chapters = []
    for idx, chapter_data in enumerate(chapters_payload):
        if not isinstance(chapter_data, dict):
            return jsonify({"message": "chapters must contain objects"}), 400
        post.chapters.append(_build_chapter(chapter_data, idx))

    category_ids = payload.get("category_ids", [])
    if category_ids and not isinstance(category_ids, list):
        return jsonify({"message": "category_ids must be a list"}), 400

    try:
        _apply_post_status(post)
    except ValueError as exc:
        db.session.rollback()
        return jsonify({"message": str(exc)}), 400

    db.session.add(post)
    _apply_categories(post, category_ids)
    db.session.commit()

    return jsonify(blog_post_schema.dump(post)), 201


@admin_bp.put("/posts/<int:post_id>")
def update_post(post_id: int):
    post = db.session.get(BlogPost, post_id)
    if not post:
        return jsonify({"message": "Not found"}), 404

    payload = request.get_json() or {}
    post = blog_post_schema.load(payload, instance=post, partial=True)

    if "chapters" in payload:
        chapters_payload = payload["chapters"]
        if chapters_payload and not isinstance(chapters_payload, list):
            return jsonify({"message": "chapters must be a list"}), 400
        post.chapters.clear()
        for idx, chapter_data in enumerate(chapters_payload):
            if not isinstance(chapter_data, dict):
                return jsonify({"message": "chapters must contain objects"}), 400
            post.chapters.append(_build_chapter(chapter_data, idx))

    if "category_ids" in payload:
        category_ids = payload["category_ids"]
        if category_ids and not isinstance(category_ids, list):
            return jsonify({"message": "category_ids must be a list"}), 400
        _apply_categories(post, category_ids)

    try:
        _apply_post_status(post)
    except ValueError as exc:
        db.session.rollback()
        return jsonify({"message": str(exc)}), 400

    db.session.commit()
    return jsonify(blog_post_schema.dump(post))


@admin_bp.delete("/posts/<int:post_id>")
def delete_post(post_id: int):
    post = db.session.get(BlogPost, post_id)
    if not post:
        return jsonify({"message": "Not found"}), 404

    db.session.delete(post)
    db.session.commit()
    return "", 204


@admin_bp.get("/posts")
def list_posts():
    posts = db.session.scalars(select(BlogPost).order_by(BlogPost.created_at.desc())).all()
    return jsonify(blog_post_list_schema.dump(posts))


@admin_bp.post("/categories")
def create_category():
    payload = request.get_json() or {}
    category = category_schema.load(payload)
    db.session.add(category)
    db.session.commit()
    return jsonify(category_schema.dump(category)), 201


@admin_bp.put("/categories/<int:category_id>")
def update_category(category_id: int):
    category = db.session.get(Category, category_id)
    if not category:
        return jsonify({"message": "Not found"}), 404

    payload = request.get_json() or {}
    category = category_schema.load(payload, instance=category, partial=True)
    db.session.commit()
    return jsonify(category_schema.dump(category))


@admin_bp.delete("/categories/<int:category_id>")
def delete_category(category_id: int):
    category = db.session.get(Category, category_id)
    if not category:
        return jsonify({"message": "Not found"}), 404

    db.session.delete(category)
    db.session.commit()
    return "", 204


@admin_bp.get("/categories")
def list_categories():
    categories = db.session.scalars(select(Category).order_by(Category.name)).all()
    return jsonify(category_list_schema.dump(categories))


@admin_bp.post("/media")
def upload_media():
    if "file" not in request.files:
        return jsonify({"message": "Missing file"}), 400

    file = request.files["file"]
    filename = file.filename or "upload"
    kind = request.form.get("kind", "IMAGE").upper()
    if kind not in {"IMAGE", "VIDEO", "FILE"}:
        return jsonify({"message": "Invalid media kind"}), 400

    storage = get_storage_backend(current_app.config)
    try:
        storage_obj = storage.upload(file.stream, filename, file.mimetype)
    except StorageError as exc:  # pragma: no cover - requires external service
        return jsonify({"message": str(exc)}), 500

    uploader_id = request.form.get("uploader_id")
    if uploader_id:
        try:
            uploader_id = int(uploader_id)
        except ValueError:
            return jsonify({"message": "uploader_id must be an integer"}), 400

    media = MediaAsset(
        uploader_id=uploader_id,
        kind=kind,
        storage_provider=storage_obj.provider,
        storage_path=storage_obj.path,
        mime_type=storage_obj.mime_type,
        bytes=storage_obj.size,
        checksum=storage_obj.checksum,
    )

    db.session.add(media)
    db.session.commit()

    return jsonify(media_schema.dump(media)), 201


def _apply_categories(post: BlogPost, category_ids: list[int]) -> None:
    if not category_ids:
        post.categories.clear()
        return

    categories = db.session.scalars(select(Category).where(Category.id.in_(category_ids))).all()
    post.categories = categories


def _ensure_default_admin_user() -> User:
    admin = db.session.scalar(select(User).limit(1))
    if admin:
        return admin

    admin = User(
        email="admin@example.com",
        password_hash="",
        display_name="Admin",
    )
    db.session.add(admin)
    db.session.commit()
    return admin


def _apply_post_status(post: BlogPost) -> None:
    if post.status == "PUBLISHED" and not post.published_at:
        post.published_at = datetime.utcnow()
    if post.status == "SCHEDULED" and not post.scheduled_for:
        raise ValueError("Scheduled posts must include 'scheduled_for'")


def _build_chapter(chapter_data: dict, fallback_position: int) -> Chapter:
    data = dict(chapter_data)
    data.pop("id", None)
    position = data.pop("position", fallback_position)
    chapter = Chapter(**data)
    chapter.position = position
    return chapter
