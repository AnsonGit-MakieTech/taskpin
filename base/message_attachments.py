"""Validation and helpers for message file attachments."""

import os
import uuid

from django.utils.text import get_valid_filename

from .file_uploads import (
    ALLOWED_EXTENSIONS,
    IMAGE_EXTENSIONS,
    MAX_FILE_SIZE,
    MAX_FILES_PER_BATCH,
    MAX_TOTAL_UPLOAD_SIZE,
    UPLOAD_RATE_LIMIT,
    UPLOAD_RATE_WINDOW,
    check_upload_rate_limit,
    file_extension,
    is_image_filename,
    validate_upload_batch,
    validate_upload_file,
)

MAX_FILES_PER_MESSAGE = 10
MAX_UPLOAD_BATCH = MAX_FILES_PER_BATCH

__all__ = [
    'ALLOWED_EXTENSIONS',
    'IMAGE_EXTENSIONS',
    'MAX_FILE_SIZE',
    'MAX_FILES_PER_MESSAGE',
    'MAX_FILES_PER_BATCH',
    'MAX_TOTAL_UPLOAD_SIZE',
    'MAX_UPLOAD_BATCH',
    'UPLOAD_RATE_LIMIT',
    'UPLOAD_RATE_WINDOW',
    'attachment_upload_to',
    'check_upload_rate_limit',
    'file_extension',
    'format_file_size',
    'is_image_filename',
    'validate_upload_batch',
    'validate_upload_file',
]


def format_file_size(size_bytes):
    if size_bytes < 1024:
        return f'{size_bytes} B'
    if size_bytes < 1024 * 1024:
        return f'{size_bytes / 1024:.1f} KB'
    return f'{size_bytes / (1024 * 1024):.1f} MB'


def attachment_upload_to(instance, filename):
    from .upload_paths import message_attachment_upload_to
    return message_attachment_upload_to(instance, filename)
