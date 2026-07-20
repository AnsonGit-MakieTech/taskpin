"""Shared file upload validation helpers."""

import os

from django.core.cache import cache

MAX_FILE_SIZE = 10 * 1024 * 1024
MAX_FILES_PER_BATCH = 10
MAX_TOTAL_UPLOAD_SIZE = 25 * 1024 * 1024
UPLOAD_RATE_LIMIT = 20
UPLOAD_RATE_WINDOW = 60

MAX_PROFILE_IMAGE_SIZE = 2 * 1024 * 1024
PROFILE_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}

ALLOWED_EXTENSIONS = {
    '.jpg', '.jpeg', '.png', '.gif', '.webp',
    '.pdf', '.txt', '.csv',
    '.doc', '.docx', '.xls', '.xlsx',
}

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}


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
    if len(files) > MAX_FILES_PER_BATCH:
        raise ValueError(f'You can upload up to {MAX_FILES_PER_BATCH} files at a time.')
    total_size = 0
    validated = []
    for uploaded_file in files:
        validate_upload_file(uploaded_file)
        total_size += uploaded_file.size
        validated.append(uploaded_file)
    if total_size > MAX_TOTAL_UPLOAD_SIZE:
        raise ValueError(f'Total upload size cannot exceed {MAX_TOTAL_UPLOAD_SIZE // (1024 * 1024)} MB.')
    return validated


def validate_profile_image(uploaded_file):
    if not uploaded_file:
        raise ValueError('No image provided.')
    if uploaded_file.size > MAX_PROFILE_IMAGE_SIZE:
        raise ValueError(f'Profile photo must be {MAX_PROFILE_IMAGE_SIZE // (1024 * 1024)} MB or smaller.')
    ext = file_extension(uploaded_file.name)
    if ext not in PROFILE_IMAGE_EXTENSIONS:
        raise ValueError('Use JPG, PNG, or WebP for your profile photo.')
    return uploaded_file


def check_upload_rate_limit(user, prefix='upload'):
    key = f'taskpin:{prefix}_rate:{user.pk}'
    count = cache.get(key, 0)
    if count >= UPLOAD_RATE_LIMIT:
        return False
    cache.set(key, count + 1, UPLOAD_RATE_WINDOW)
    return True
