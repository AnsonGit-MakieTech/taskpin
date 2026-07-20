"""Upload path callables for FileField/ImageField (no model imports)."""

import os
import uuid

from django.utils.text import get_valid_filename


def profile_avatar_upload_to(instance, filename):
    ext = os.path.splitext(filename or '')[1].lower() or '.jpg'
    if ext not in {'.jpg', '.jpeg', '.png', '.webp'}:
        ext = '.jpg'
    return f'profiles/user_{instance.user_id}/avatar{ext}'


def task_attachment_upload_to(instance, filename):
    org_id = instance.organization_id
    task_part = instance.task_id if instance.task_id else 'pending'
    safe_name = get_valid_filename(os.path.basename(filename)) or 'file'
    return f'tasks/org_{org_id}/task_{task_part}/{uuid.uuid4().hex}_{safe_name}'


def message_attachment_upload_to(instance, filename):
    org_id = instance.conversation.organization_id
    conv_id = instance.conversation_id
    safe_name = get_valid_filename(os.path.basename(filename)) or 'file'
    return f'messages/org_{org_id}/conv_{conv_id}/{uuid.uuid4().hex}_{safe_name}'
