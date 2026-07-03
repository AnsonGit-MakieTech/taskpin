from datetime import timedelta

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


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


class ActivityLog(models.Model):
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
