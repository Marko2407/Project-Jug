from __future__ import annotations

import hashlib
import logging
import mimetypes
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO, Protocol

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload


logger = logging.getLogger(__name__)


class StorageError(RuntimeError):
    """Raised when a storage backend fails."""


class StorageBackend(Protocol):
    def upload(self, file_handle: BinaryIO, filename: str, mime_type: str | None = None) -> "StorageObject":
        ...


@dataclass(slots=True)
class StorageObject:
    provider: str
    path: str
    mime_type: str | None
    size: int | None
    checksum: str | None


_storage_instance: StorageBackend | None = None


def get_storage_backend(config: dict) -> StorageBackend:
    global _storage_instance
    if _storage_instance is not None:
        return _storage_instance

    backend_name = (config.get("MEDIA_STORAGE_BACKEND") or "gdrive").lower()
    if backend_name == "gdrive":
        _storage_instance = GoogleDriveStorage(
            service_account_path=config.get("GOOGLE_DRIVE_SERVICE_ACCOUNT"),
            upload_folder_id=config.get("GOOGLE_DRIVE_UPLOAD_FOLDER_ID"),
        )
    elif backend_name == "external":
        _storage_instance = ExternalStorage()
    else:
        _storage_instance = DatabaseStorage()
    return _storage_instance


class GoogleDriveStorage:
    """Uploads binary content to Google Drive using a service account."""

    def __init__(self, service_account_path: str | Path | None, upload_folder_id: str | None = None) -> None:
        if not service_account_path:
            raise StorageError("GOOGLE_DRIVE_SERVICE_ACCOUNT is not configured")
        path = Path(service_account_path)
        if not path.exists():
            raise StorageError(f"Google Drive service account file not found at {path}")

        scopes = ["https://www.googleapis.com/auth/drive.file"]
        creds = service_account.Credentials.from_service_account_file(str(path), scopes=scopes)
        self.drive_service = build("drive", "v3", credentials=creds)
        self.folder_id = upload_folder_id

    def upload(self, file_handle: BinaryIO, filename: str, mime_type: str | None = None) -> StorageObject:
        data = file_handle.read()
        file_handle.seek(0)
        checksum = hashlib.sha256(data).hexdigest()
        size = len(data)

        if not mime_type:
            mime_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"

        metadata = {"name": filename}
        if self.folder_id:
            metadata["parents"] = [self.folder_id]

        media = MediaIoBaseUpload(file_handle, mimetype=mime_type, resumable=False)
        file = (
            self.drive_service.files()
            .create(body=metadata, media_body=media, fields="id, name, mimeType, webContentLink, webViewLink")
            .execute()
        )

        file_id = file["id"]
        web_view_link = file.get("webViewLink") or file.get("webContentLink") or file_id

        logger.info("Uploaded file %s to Google Drive with id %s", filename, file_id)

        return StorageObject(
            provider="GDRIVE",
            path=web_view_link,
            mime_type=file.get("mimeType"),
            size=size,
            checksum=checksum,
        )


class ExternalStorage:
    """Placeholder backend that expects caller to provide externally hosted URLs."""

    def upload(self, file_handle: BinaryIO, filename: str, mime_type: str | None = None) -> StorageObject:  # pragma: no cover - simple
        raise StorageError("External storage cannot upload files. Provide a URL instead.")


class DatabaseStorage:
    """Placeholder backend for storing raw data in the database."""

    def upload(self, file_handle: BinaryIO, filename: str, mime_type: str | None = None) -> StorageObject:  # pragma: no cover - not implemented
        raise StorageError("Database storage is not implemented. Configure Google Drive instead.")
