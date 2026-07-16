from django.contrib import admin
from .models import (
    UserProfile, Task, ActivityLog, Conversation, ConversationParticipant, Message,
    Organization, OrganizationMembership,
)


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_by', 'created_at')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(OrganizationMembership)
class OrganizationMembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'organization', 'role', 'joined_at')
    list_filter = ('role', 'organization')
    search_fields = ('user__username', 'organization__name')
    raw_id_fields = ('user', 'organization')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')
    list_filter = ('role',)
    search_fields = ('user__username', 'user__first_name', 'user__last_name')


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'organization', 'status', 'priority', 'assigned_to', 'created_by', 'due_date', 'created_at')
    list_filter = ('status', 'priority', 'organization')
    search_fields = ('title', 'description')
    date_hierarchy = 'created_at'
    raw_id_fields = ('created_by', 'assigned_to')


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('actor', 'organization', 'action', 'task', 'timestamp')
    list_filter = ('timestamp', 'organization')
    search_fields = ('action', 'actor__username', 'task__title')
    readonly_fields = ('actor', 'action', 'task', 'timestamp')


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'organization', 'conversation_type', 'user_a', 'user_b', 'updated_at')
    list_filter = ('conversation_type', 'organization')


@admin.register(ConversationParticipant)
class ConversationParticipantAdmin(admin.ModelAdmin):
    list_display = ('conversation', 'user', 'last_read_at')
    raw_id_fields = ('conversation', 'user')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('conversation', 'sender', 'preview_body', 'created_at')
    search_fields = ('body', 'sender__username')
    raw_id_fields = ('conversation', 'sender')

    @admin.display(description='Body')
    def preview_body(self, obj):
        return obj.preview
