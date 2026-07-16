"""Validation and helpers for message file attachments."""

import os
import uuid

from django.core.cache import cache
from django.utils.text import get_valid_filename

MAX_FILE_SIZE = 10 * 1024 * 1024
MAX_FILES_PER_MESSAGE = 10
MAX_TOTAL_UPLOAD_SIZE = 25 * 1024 * 1024
MAX_UPLOAD_BATCH = 10
UPLOAD_RATE_LIMIT = 20
UPLOAD_RATE_WINDOW = 60

ALLOWED_EXTENSIONS = {
    '.jpg', '.jpeg', '.png', '.gif', '.webp',
    '.pdf', '.txt', '.csv',
    '.doc', '.docx', '.xls', '.xlsx',
}

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}


def attachment_upload_to(instance, filename):
    org_id = instance.conversation.organization_id
    conv_id = instance.conversation_id
    safe_name = get_valid_filename(os.path.basename(filename)) or 'file'
    return f'messages/org_{org_id}/conv_{conv_id}/{uuid.uuid4().hex}_{safe_name}'


def file_extension(filename):
    return os.path.splitext(filename or '')[1].lower()


def is_image_filename(filename):
    return file_extension(filename) in IMAGE_EXTENSIONS


def validate_upload_file(uploaded_file):
    if not uploaded_file:
        raise ValueError('No file provided.')
    if uploaded_file.size > MAX_FILE_SIZE:
        raise ValueError(f'Each file must be {MAX_FILE_SIZE // (1024 * 1024)} MB or smaller.')
    ext = file_extension(uploaded_file.name)
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f'File type not allowed: {ext or "unknown"}')
    return uploaded_file


def validate_upload_batch(files):
    if not files:
        raise ValueError('No files selected.')
    if len(files) > MAX_UPLOAD_BATCH:
        raise ValueError(f'You can upload up to {MAX_UPLOAD_BATCH} files at a time.')
    total_size = 0
    validated = []
    for uploaded_file in files:
        validate_upload_file(uploaded_file)
        total_size += uploaded_file.size
        validated.append(uploaded_file)
    if total_size > MAX_TOTAL_UPLOAD_SIZE:
        raise ValueError(f'Total upload size cannot exceed {MAX_TOTAL_UPLOAD_SIZE // (1024 * 1024)} MB.')
    return validated


def check_upload_rate_limit(user):
    key = f'taskpin:msg_upload_rate:{user.pk}'
    count = cache.get(key, 0)
    if count >= UPLOAD_RATE_LIMIT:
        return False
    cache.set(key, count + 1, UPLOAD_RATE_WINDOW)
    return True


def format_file_size(size_bytes):
    if size_bytes < 1024:
        return f'{size_bytes} B'
    if size_bytes < 1024 * 1024:
        return f'{size_bytes / 1024:.1f} KB'
    return f'{size_bytes / (1024 * 1024):.1f} MB'
