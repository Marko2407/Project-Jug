from __future__ import annotations

from datetime import datetime

from flask import Blueprint, current_app, jsonify, request
from sqlalchemy import func, select

from app.extensions import db
from app.models import BlogPost, Category, PostMetricsDaily, Visit
from app.schemas import BlogPostSchema, CategorySchema

public_bp = Blueprint("public", __name__)

blog_post_schema = BlogPostSchema()
blog_post_list_schema = BlogPostSchema(many=True)
category_list_schema = CategorySchema(many=True)


@public_bp.get("/posts")
def list_posts():
    query = select(BlogPost).where(BlogPost.status == "PUBLISHED")

    category_slug = request.args.get("category")
    if category_slug:
        query = query.join(BlogPost.categories).where(Category.slug == category_slug)

    search = request.args.get("search")
    if search:
        ilike = f"%{search.lower()}%"
        summary_expr = func.coalesce(BlogPost.summary, "")
        query = query.where(
            func.lower(BlogPost.title).like(ilike) | func.lower(summary_expr).like(ilike)
        )

    published_before = request.args.get("published_before")
    if published_before:
        try:
            dt = datetime.fromisoformat(published_before)
            query = query.where(BlogPost.published_at <= dt)
        except ValueError:
            return jsonify({"message": "Invalid published_before"}), 400

    published_after = request.args.get("published_after")
    if published_after:
        try:
            dt = datetime.fromisoformat(published_after)
            query = query.where(BlogPost.published_at >= dt)
        except ValueError:
            return jsonify({"message": "Invalid published_after"}), 400

    query = query.order_by(BlogPost.published_at.desc().nullslast())

    posts = db.session.scalars(query).all()
    return jsonify(blog_post_list_schema.dump(posts))


@public_bp.get("/posts/<slug>")
def get_post(slug: str):
    post = db.session.scalar(select(BlogPost).where(BlogPost.slug == slug, BlogPost.status == "PUBLISHED"))
    if not post:
        return jsonify({"message": "Not found"}), 404

    _register_visit(post)
    return jsonify(blog_post_schema.dump(post))


@public_bp.get("/posts/featured")
def get_featured_posts():
    limit = current_app.config.get("POST_FEATURED_LIMIT", 6)
    posts = db.session.scalars(
        select(BlogPost)
        .where(BlogPost.status == "PUBLISHED", BlogPost.is_featured.is_(True))
        .order_by(BlogPost.published_at.desc().nullslast())
        .limit(limit)
    ).all()
    return jsonify(blog_post_list_schema.dump(posts))


@public_bp.get("/posts/recent")
def get_recent_posts():
    limit = current_app.config.get("POST_RECENT_LIMIT", 12)
    posts = db.session.scalars(
        select(BlogPost)
        .where(BlogPost.status == "PUBLISHED")
        .order_by(BlogPost.published_at.desc().nullslast())
        .limit(limit)
    ).all()
    return jsonify(blog_post_list_schema.dump(posts))


@public_bp.get("/posts/popular")
def get_popular_posts():
    subquery = (
        select(
            PostMetricsDaily.post_id,
            func.sum(PostMetricsDaily.views).label("total_views"),
        )
        .group_by(PostMetricsDaily.post_id)
        .subquery()
    )

    posts = db.session.scalars(
        select(BlogPost)
        .join(subquery, BlogPost.id == subquery.c.post_id)
        .where(BlogPost.status == "PUBLISHED")
        .order_by(subquery.c.total_views.desc())
        .limit(current_app.config.get("POST_FEATURED_LIMIT", 6))
    ).all()

    return jsonify(blog_post_list_schema.dump(posts))


@public_bp.get("/categories")
def list_categories():
    categories = db.session.scalars(select(Category).order_by(Category.name)).all()
    return jsonify(category_list_schema.dump(categories))


def _register_visit(post: BlogPost) -> None:
    session_id = request.headers.get("X-Session-ID")
    ip_hash = request.headers.get("X-Forwarded-For") or request.remote_addr
    user_agent = request.headers.get("User-Agent")
    today = datetime.utcnow().date()

    already_counted = False
    if session_id:
        already_counted = (
            db.session.scalar(
                select(func.count())
                .select_from(Visit)
                .where(
                    Visit.post_id == post.id,
                    Visit.session_id == session_id,
                    func.date(Visit.visited_at) == today,
                )
            )
            > 0
        )

    visit = Visit(
        post_id=post.id,
        session_id=session_id,
        ip_hash=ip_hash,
        user_agent=user_agent,
        visited_at=datetime.utcnow(),
    )
    db.session.add(visit)
    db.session.commit()

    metrics_key = (post.id, today)
    metrics = db.session.get(PostMetricsDaily, metrics_key)
    if not metrics:
        metrics = PostMetricsDaily(post_id=metrics_key[0], date=metrics_key[1])
        db.session.add(metrics)

    metrics.views += 1
    if session_id and not already_counted:
        metrics.unique_sessions += 1
    db.session.commit()
