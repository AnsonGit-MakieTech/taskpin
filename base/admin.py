from django.contrib import admin
from .models import UserProfile, Task, ActivityLog


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')
    list_filter = ('role',)
    search_fields = ('user__username', 'user__first_name', 'user__last_name')


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'priority', 'assigned_to', 'created_by', 'due_date', 'created_at')
    list_filter = ('status', 'priority')
    search_fields = ('title', 'description')
    date_hierarchy = 'created_at'
    raw_id_fields = ('created_by', 'assigned_to')


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('actor', 'action', 'task', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('action', 'actor__username', 'task__title')
    readonly_fields = ('actor', 'action', 'task', 'timestamp')
