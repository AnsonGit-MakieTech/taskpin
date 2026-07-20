"""Task file attachment helpers."""

from .file_uploads import (
    check_upload_rate_limit,
    validate_upload_file,
)
from .models import TaskAttachment

MAX_FILES_PER_TASK = 10


def task_attachment_upload_to(instance, filename):
    from .upload_paths import task_attachment_upload_to as _upload_to
    return _upload_to(instance, filename)


def claim_task_attachments(organization, user, task, attachment_ids):
    if not attachment_ids:
        return []
    if len(attachment_ids) > MAX_FILES_PER_TASK:
        raise ValueError(f'You can attach up to {MAX_FILES_PER_TASK} files per task.')

    attachments = list(
        TaskAttachment.objects.filter(
            pk__in=attachment_ids,
            organization=organization,
            uploaded_by=user,
            task__isnull=True,
        ),
    )
    if len(attachments) != len(set(attachment_ids)):
        raise ValueError('One or more attachments are invalid or already used.')

    TaskAttachment.objects.filter(pk__in=[item.pk for item in attachments]).update(task=task)
    return attachments


def attach_existing_to_task(task, attachment_ids, user):
    """Link pending uploads to an existing task (edit flow)."""
    if not attachment_ids:
        return []
    current_count = task.attachments.count()
    if current_count + len(attachment_ids) > MAX_FILES_PER_TASK:
        raise ValueError(f'You can attach up to {MAX_FILES_PER_TASK} files per task.')

    attachments = list(
        TaskAttachment.objects.filter(
            pk__in=attachment_ids,
            organization=task.organization,
            uploaded_by=user,
            task__isnull=True,
        ),
    )
    if len(attachments) != len(set(attachment_ids)):
        raise ValueError('One or more attachments are invalid or already used.')

    TaskAttachment.objects.filter(pk__in=[item.pk for item in attachments]).update(task=task)
    return attachments


def create_pending_task_attachment(organization, user, uploaded_file, task=None):
    from .file_uploads import validate_upload_file

    if not check_upload_rate_limit(user, prefix='task_upload'):
        raise PermissionError('You are uploading files too quickly. Please wait a moment.')
    validate_upload_file(uploaded_file)

    if task is not None:
        if task.attachments.count() >= MAX_FILES_PER_TASK:
            raise ValueError(f'You can attach up to {MAX_FILES_PER_TASK} files per task.')

    return TaskAttachment.objects.create(
        organization=organization,
        task=task,
        uploaded_by=user,
        file=uploaded_file,
        original_name=uploaded_file.name,
        content_type=getattr(uploaded_file, 'content_type', '') or '',
        size_bytes=uploaded_file.size,
    )


def delete_task_attachment(attachment):
    if attachment.file:
        attachment.file.delete(save=False)
    attachment.delete()
