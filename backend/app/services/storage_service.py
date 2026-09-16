import os
import uuid
import logging
from typing import Optional
from fastapi import UploadFile
from app.config import settings

logger = logging.getLogger(__name__)

# Try optional cloudinary import
try:
    import cloudinary
    import cloudinary.uploader
    if settings.CLOUDINARY_CLOUD_NAME and settings.CLOUDINARY_API_KEY and settings.CLOUDINARY_API_SECRET:
        cloudinary.config(
            cloud_name=settings.CLOUDINARY_CLOUD_NAME,
            api_key=settings.CLOUDINARY_API_KEY,
            api_secret=settings.CLOUDINARY_API_SECRET,
            secure=True
        )
        has_cloudinary = True
    else:
        has_cloudinary = False
except Exception:
    has_cloudinary = False


class StorageService:
    def __init__(self):
        self.upload_dir = settings.UPLOAD_DIR
        os.makedirs(self.upload_dir, exist_ok=True)

    async def save_file(
        self,
        file: UploadFile,
        folder: str = "media",
        resource_type: str = "auto",
    ) -> str:
        """Upload a file to Cloudinary if configured, or save locally and return URL."""
        if has_cloudinary:
            try:
                contents = await file.read()
                result = cloudinary.uploader.upload(
                    contents,
                    folder=f"coursedrive/{folder}",
                    resource_type=resource_type,
                )
                return result.get("secure_url") or result.get("url")
            except Exception as e:
                logger.error(f"Cloudinary upload failed: {e}. Falling back to local storage.")

        # Local storage fallback
        sub_dir = os.path.join(self.upload_dir, folder)
        os.makedirs(sub_dir, exist_ok=True)

        ext = os.path.splitext(file.filename or "")[1]
        unique_filename = f"{uuid.uuid4().hex}{ext}"
        file_path = os.path.join(sub_dir, unique_filename)

        await file.seek(0)
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)

        # Build accessible URL
        return f"{settings.BACKEND_URL}/uploads/{folder}/{unique_filename}"

    def save_bytes(
        self,
        data: bytes,
        filename: str,
        folder: str = "certificates",
    ) -> str:
        """Save raw bytes (e.g. generated PDF) locally or to cloud."""
        if has_cloudinary:
            try:
                import io
                result = cloudinary.uploader.upload(
                    io.BytesIO(data),
                    folder=f"coursedrive/{folder}",
                    resource_type="raw",
                    public_id=filename
                )
                return result.get("secure_url") or result.get("url")
            except Exception as e:
                logger.error(f"Cloudinary upload failed for bytes: {e}. Falling back to local storage.")

        sub_dir = os.path.join(self.upload_dir, folder)
        os.makedirs(sub_dir, exist_ok=True)

        file_path = os.path.join(sub_dir, filename)
        with open(file_path, "wb") as f:
            f.write(data)

        # Use an environment variable or fallback to NEXT_PUBLIC_API_URL domain logic?
        # Actually just use BACKEND_URL, but we can't reliably know frontend URL here.
        return f"{settings.BACKEND_URL}/uploads/{folder}/{filename}"

storage_service = StorageService()
