# Blog "Svijet Zdravlja" backend

Flask backend for a health & nutrition blog with support for Google Drive media storage, scheduled publishing and dynamic post chapters.

## Features

- PostgreSQL schema that mirrors the provided SQL design using SQLAlchemy models.
- REST API with public endpoints for listing, filtering and reading posts, featured content and categories.
- Admin endpoints protected by a JWT bearer token for CRUD operations on posts, chapters, categories and media uploads.
- Google Drive storage backend capable of uploading images, videos or other media through a service account.
- Daily metrics and visit tracking for popularity rankings.

## Getting started

1. Create and activate a virtual environment.

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Configure environment variables. Copy `.env.example` to `.env` (or set variables another way) and adjust as needed.

3. Prepare a PostgreSQL database and apply migrations.

   ```bash
   flask --app wsgi db init  # first run only
   flask --app wsgi db migrate -m "Initial schema"
   flask --app wsgi db upgrade
   ```

4. Provide Google Drive credentials: download a service account JSON file and point `GOOGLE_DRIVE_SERVICE_ACCOUNT` to it. Optionally specify `GOOGLE_DRIVE_UPLOAD_FOLDER_ID` for uploads.

5. Run the development server.

   ```bash
   flask --app wsgi run --debug
   ```

## Configuration

| Variable | Description | Default |
| --- | --- | --- |
| `SQLALCHEMY_DATABASE_URI` | PostgreSQL connection string | `postgresql+psycopg2://postgres:postgres@localhost:5432/blog` |
| `ADMIN_JWT_SECRET` | Secret used to sign/verify admin JWTs | `change-me` |
| `ADMIN_JWT_ALGORITHM` | JWT signing algorithm | `HS256` |
| `MEDIA_STORAGE_BACKEND` | `gdrive`, `db`, or `external` | `gdrive` |
| `GOOGLE_DRIVE_SERVICE_ACCOUNT` | Path to service account JSON | `service-account.json` |
| `GOOGLE_DRIVE_UPLOAD_FOLDER_ID` | Optional Drive folder for uploads | `None` |

## API overview

### Public endpoints

- `GET /api/posts` – list published posts with optional filters (`category`, `search`, `published_before`, `published_after`).
- `GET /api/posts/<slug>` – fetch a single published post and register a visit.
- `GET /api/posts/featured` – featured posts.
- `GET /api/posts/recent` – latest posts.
- `GET /api/posts/popular` – most viewed posts based on metrics.
- `GET /api/categories` – list all categories.

### Admin endpoints

Include an `Authorization: Bearer <JWT>` header where the token encodes `{"role": "admin"}`.

Generate a short-lived admin token using PyJWT:

```bash
python - <<'PY'
import datetime as dt
import jwt

payload = {
    "sub": "admin",
    "role": "admin",
    "exp": dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=1),
}
secret = "change-me"  # match ADMIN_JWT_SECRET
print(jwt.encode(payload, secret, algorithm="HS256"))
PY
```

- `POST /api/admin/posts` – create a post with chapters.
- `PUT /api/admin/posts/<id>` – update post metadata, chapters, categories.
- `DELETE /api/admin/posts/<id>` – delete post.
- `GET /api/admin/posts` – list all posts.
- `POST /api/admin/categories` – create category.
- `PUT /api/admin/categories/<id>` – update category.
- `DELETE /api/admin/categories/<id>` – delete category.
- `GET /api/admin/categories` – list categories.
- `POST /api/admin/media` – upload media file to Google Drive and persist metadata.

## Testing the API quickly

Use HTTP clients such as `curl` or Postman.

```bash
curl -X POST http://localhost:5000/api/admin/posts \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{
    "slug": "prvi-post",
    "title": "Prvi blog post",
    "summary": "Uvod u zdravu prehranu",
    "status": "PUBLISHED",
    "chapters": [
      {"type": "TEXT", "position": 0, "text_content": "Sadržaj poglavlja."}
    ]
  }'
```

## Next steps

- Implementåç authentication for multiple admin users.
- Add background scheduler to automatically publish scheduled posts.
- Expand metrics tracking for likes and shares.
- Integrate with front-end for rendering dynamic chapters.
