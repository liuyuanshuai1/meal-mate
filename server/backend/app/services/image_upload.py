import asyncio
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.core.config import get_settings
from app.core.response import AppException

ALLOWED_IMAGE_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}
MAX_IMAGE_SIZE = 5 * 1024 * 1024


async def save_upload_image(file: UploadFile) -> str:
    suffix = ALLOWED_IMAGE_TYPES.get(file.content_type or "")
    if suffix is None:
        raise AppException(40001, "只允许上传 jpg、png 或 webp 图片")

    content = await file.read(MAX_IMAGE_SIZE + 1)
    if len(content) > MAX_IMAGE_SIZE:
        raise AppException(40001, "图片不能超过 5MB")

    settings = get_settings()
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid4().hex}{suffix}"
    target = upload_dir / filename
    await asyncio.to_thread(target.write_bytes, content)
    return f"{settings.public_static_url.rstrip('/')}/{filename}"
