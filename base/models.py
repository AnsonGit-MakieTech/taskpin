from datetime import timedelta

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.text import slugify

from .upload_paths import (
    message_attachment_upload_to as attachment_upload_to,
    profile_avatar_upload_to,
    task_attachment_upload_to,
)


class Organization(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_organizations',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    @staticmethod
    def unique_slug(name):
        base = slugify(name)[:200] or 'organization'
        slug = base
        counter = 1
        while Organization.objects.filter(slug=slug).exists():
            slug = f'{base}-{counter}'
            counter += 1
        return slug


class OrganizationMembership(models.Model):
    ROLE_ADMIN = 'admin'
    ROLE_MEMBER = 'member'
    ROLE_CHOICES = [
        (ROLE_ADMIN, 'Admin'),
        (ROLE_MEMBER, 'Member'),
    ]

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='organization_membership',
    )
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name='memberships',
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=ROLE_MEMBER)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['joined_at']

    def __str__(self):
        return f'{self.user_id} in {self.organization_id} ({self.role})'


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('member', 'Member'),
        ('admin', 'Admin'),
    ]

    AVATAR_COLORS = ['#FFB74D', '#64B5F6', '#81C784', '#CE93D8', '#80CBC4', '#F48FB1']

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='member')
    avatar_initials = models.CharField(
        max_length=2,
        blank=True,
        help_text='Optional override for avatar initials (max 2 characters).',
    )
    avatar_image = models.ImageField(
        upload_to=profile_avatar_upload_to,
        blank=True,
        null=True,
    )

    def initials(self):
        if self.avatar_initials:
            return self.avatar_initials[:2].upper()
        first = self.user.first_name[:1].upper() if self.user.first_name else ''
        last = self.user.last_name[:1].upper() if self.user.last_name else ''
        if first or last:
            return f'{first}{last}'
        return self.user.username[:2].upper()

    def display_name(self):
        full = f'{self.user.first_name} {self.user.last_name}'.strip()
        return full if full else self.user.username

    def avatar_color(self):
        index = sum(ord(c) for c in self.user.username) % len(self.AVATAR_COLORS)
        return self.AVATAR_COLORS[index]

    @property
    def avatar_photo_url(self):
        if self.avatar_image:
            return self.avatar_image.url
        return None

    def __str__(self):
        return f'{self.display_name()} ({self.role})'


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)


class Task(models.Model):
    STATUS_UNASSIGNED = 'unassigned'
    STATUS_ASSIGNED = 'assigned'
    STATUS_DONE = 'done'
    STATUS_CHOICES = [
        (STATUS_UNASSIGNED, 'Unassigned'),
        (STATUS_ASSIGNED, 'Assigned'),
        (STATUS_DONE, 'Done'),
    ]

    PRIORITY_NORMAL = 'normal'
    PRIORITY_IMPORTANT = 'important'
    PRIORITY_URGENT = 'urgent'
    PRIORITY_CHOICES = [
        (PRIORITY_NORMAL, 'Normal'),
        (PRIORITY_IMPORTANT, 'Important'),
        (PRIORITY_URGENT, 'Urgent'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name='tasks',
    )
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default=STATUS_UNASSIGNED)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default=PRIORITY_NORMAL)
    due_date = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='created_tasks'
    )
    assigned_to = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    completion_remarks = models.TextField(
        blank=True,
        help_text='Optional notes added when the task was marked done.',
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def is_done(self):
        return self.status == self.STATUS_DONE

    @property
    def is_overdue(self):
        if self.due_date and not self.is_done:
            return self.due_date < timezone.now()
        return False

    @property
    def deadline_urgency(self):
        """CSS modifier: overdue, due_soon (within 24h), or due_today."""
        if not self.due_date or self.is_done:
            return ''
        now = timezone.now()
        if self.due_date < now:
            return 'overdue'
        if timezone.localtime(self.due_date).date() == timezone.localtime(now).date():
            return 'due_today'
        if self.due_date <= now + timedelta(hours=24):
            return 'due_soon'
        return ''


class TaskAttachment(models.Model):
    task = models.ForeignKey(
        Task, on_delete=models.CASCADE, null=True, blank=True, related_name='attachments',
    )
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name='task_attachments',
    )
    uploaded_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='task_uploads',
    )
    file = models.FileField(upload_to=task_attachment_upload_to)
    original_name = models.CharField(max_length=255)
    content_type = models.CharField(max_length=127, blank=True)
    size_bytes = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return self.original_name

    @property
    def is_image(self):
        from .file_uploads import is_image_filename
        return is_image_filename(self.original_name)

    def save(self, *args, **kwargs):
        if self.file and not self.size_bytes:
            self.size_bytes = self.file.size
        if self.file and hasattr(self.file, 'content_type') and self.file.content_type:
            self.content_type = self.file.content_type
        super().save(*args, **kwargs)


class ActivityLog(models.Model):
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name='activity_logs',
    )
    actor = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='activity_logs'
    )
    action = models.CharField(max_length=300)
    task = models.ForeignKey(
        Task, on_delete=models.SET_NULL, null=True, blank=True, related_name='logs'
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f'{self.actor} — {self.action} ({self.timestamp:%Y-%m-%d %H:%M})'


class Conversation(models.Model):
    TYPE_TEAM = 'team'
    TYPE_DIRECT = 'direct'
    TYPE_CHOICES = [
        (TYPE_TEAM, 'Team'),
        (TYPE_DIRECT, 'Direct'),
    ]

    conversation_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name='conversations',
    )
    user_a = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True, related_name='+',
    )
    user_b = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True, related_name='+',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['organization', 'conversation_type'],
                condition=models.Q(conversation_type='team'),
                name='unique_team_conversation_per_org',
            ),
            models.UniqueConstraint(
                fields=['user_a', 'user_b'],
                condition=models.Q(conversation_type='direct'),
                name='unique_direct_conversation',
            ),
        ]
        ordering = ['-updated_at']

    def __str__(self):
        if self.conversation_type == self.TYPE_TEAM:
            return 'Team chat'
        return f'Direct ({self.user_a_id}, {self.user_b_id})'


class ConversationParticipant(models.Model):
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name='participants',
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversation_participants')
    last_read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = [['conversation', 'user']]

    def __str__(self):
        return f'{self.user_id} in {self.conversation_id}'


class Message(models.Model):
    MAX_BODY_LENGTH = 2000

    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name='messages',
    )
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    body = models.TextField(max_length=MAX_BODY_LENGTH, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        preview = self.preview
        return f'{self.sender_id}: {preview[:40]}'

    @property
    def preview(self):
        body = self.body.replace('\n', ' ').strip()
        attachments = list(self.attachments.all())

        if body:
            if len(body) > 80:
                body = body[:77] + '…'
            if attachments:
                count = len(attachments)
                suffix = f' (+ {count} file{"s" if count != 1 else ""})'
                combined = body + suffix
                return combined[:80] + ('…' if len(combined) > 80 else '')
            return body

        if not attachments:
            return ''

        if len(attachments) == 1:
            name = attachments[0].original_name
            label = f'📎 {name}'
            return label[:80] + ('…' if len(label) > 80 else '')
        return f'📎 {len(attachments)} files'

    @property
    def has_content(self):
        return bool(self.body.strip()) or self.attachments.exists()


class MessageAttachment(models.Model):
    message = models.ForeignKey(
        Message, on_delete=models.CASCADE, null=True, blank=True, related_name='attachments',
    )
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name='pending_attachments',
    )
    uploaded_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='message_uploads',
    )
    file = models.FileField(upload_to=attachment_upload_to)
    original_name = models.CharField(max_length=255)
    content_type = models.CharField(max_length=127, blank=True)
    size_bytes = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return self.original_name

    @property
    def is_image(self):
        from .message_attachments import is_image_filename
        return is_image_filename(self.original_name)

    def save(self, *args, **kwargs):
        if self.file and not self.size_bytes:
            self.size_bytes = self.file.size
        if self.file and hasattr(self.file, 'content_type') and self.file.content_type:
            self.content_type = self.file.content_type
        super().save(*args, **kwargs)
