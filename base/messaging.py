"""Conversation helpers, unread counts, and message sending."""

from django.contrib.auth.models import User
from django.core.cache import cache
from django.utils import timezone

from .models import Conversation, ConversationParticipant, Message, MessageAttachment
from .message_attachments import MAX_FILES_PER_MESSAGE
from .organizations import get_org_members, get_user_organization, users_share_organization
from .realtime import notify_board_update

MESSAGE_RATE_LIMIT = 30
MESSAGE_RATE_WINDOW = 60


def _ordered_users(user_one, user_two):
    if user_one.pk <= user_two.pk:
        return user_one, user_two
    return user_two, user_one


def ensure_participant(conversation, user):
    participant, _ = ConversationParticipant.objects.get_or_create(
        conversation=conversation,
        user=user,
    )
    return participant


def get_team_conversation(organization):
    conversation, _ = Conversation.objects.get_or_create(
        conversation_type=Conversation.TYPE_TEAM,
        organization=organization,
    )
    for user in get_org_members(organization):
        ensure_participant(conversation, user)
    return conversation


def sync_team_participants(user):
    """Add any organization members missing from the team conversation."""
    organization = get_user_organization(user)
    if organization is None:
        return None
    conversation = get_team_conversation(organization)
    member_ids = set(get_org_members(organization).values_list('pk', flat=True))
    existing_ids = set(conversation.participants.values_list('user_id', flat=True))
    for user_id in member_ids - existing_ids:
        ensure_participant(conversation, User.objects.get(pk=user_id))
    return conversation


def get_or_create_direct_conversation(user, other_user):
    if user.pk == other_user.pk:
        raise ValueError('Cannot create a direct chat with yourself.')
    if not users_share_organization(user, other_user):
        raise PermissionError('You can only message members of your organization.')
    organization = get_user_organization(user)
    user_a, user_b = _ordered_users(user, other_user)
    conversation, created = Conversation.objects.get_or_create(
        conversation_type=Conversation.TYPE_DIRECT,
        user_a=user_a,
        user_b=user_b,
        defaults={'organization': organization},
    )
    if conversation.organization_id != organization.pk:
        raise PermissionError('You cannot access this conversation.')
    ensure_participant(conversation, user_a)
    ensure_participant(conversation, user_b)
    return conversation


def user_display_name(user):
    if hasattr(user, 'profile') and user.profile:
        return user.profile.display_name()
    full = user.get_full_name()
    return full if full else user.username


def conversation_title(conversation, viewer):
    if conversation.conversation_type == Conversation.TYPE_TEAM:
        return 'Team'
    other = conversation.user_b if conversation.user_a_id == viewer.pk else conversation.user_a
    if other:
        return user_display_name(other)
    return 'Direct message'


def conversation_avatar_context(conversation, viewer):
    if conversation.conversation_type == Conversation.TYPE_TEAM:
        return {
            'is_team': True,
            'initials': 'TM',
            'color': '#FFB74D',
        }
    other = conversation.user_b if conversation.user_a_id == viewer.pk else conversation.user_a
    profile = getattr(other, 'profile', None)
    return {
        'is_team': False,
        'initials': profile.initials() if profile else other.username[:2].upper(),
        'color': profile.avatar_color() if profile else '#64B5F6',
    }


def other_user_in_direct(conversation, viewer):
    if conversation.conversation_type != Conversation.TYPE_DIRECT:
        return None
    if conversation.user_a_id == viewer.pk:
        return conversation.user_b
    return conversation.user_a


def is_participant(conversation, user):
    organization = get_user_organization(user)
    if organization is None or conversation.organization_id != organization.pk:
        return False
    return conversation.participants.filter(user=user).exists()


def unread_count_for_user(user):
    organization = get_user_organization(user)
    if organization is None:
        return 0
    participants = (
        ConversationParticipant.objects
        .filter(user=user, conversation__organization=organization)
        .select_related('conversation')
    )
    total = 0
    for participant in participants:
        qs = Message.objects.filter(conversation=participant.conversation).exclude(sender=user)
        if participant.last_read_at:
            qs = qs.filter(created_at__gt=participant.last_read_at)
        total += qs.count()
    return total


def unread_count_for_conversation(conversation, user):
    participant = conversation.participants.filter(user=user).first()
    if not participant:
        return 0
    qs = Message.objects.filter(conversation=conversation).exclude(sender=user)
    if participant.last_read_at:
        qs = qs.filter(created_at__gt=participant.last_read_at)
    return qs.count()


def read_receipt_label(message, viewer):
    """Return Messenger-style read receipt text for the sender's own messages."""
    if message.sender_id != viewer.pk:
        return ''

    conversation = message.conversation
    msg_time = message.created_at

    if conversation.conversation_type == Conversation.TYPE_DIRECT:
        other = other_user_in_direct(conversation, viewer)
        if not other:
            return ''
        participant = conversation.participants.filter(user=other).first()
        if participant and participant.last_read_at and participant.last_read_at >= msg_time:
            return 'Seen'
        return ''

    others = list(conversation.participants.exclude(user=viewer).select_related('user', 'user__profile'))
    total_others = len(others)
    if total_others == 0:
        return ''

    readers = [p for p in others if p.last_read_at and p.last_read_at >= msg_time]
    count = len(readers)
    if count == 0:
        return ''
    if count >= total_others:
        return 'Seen'
    if count == 1:
        return f'Seen by {user_display_name(readers[0].user)}'
    return f'Seen by {count}'


def read_receipt_context(message, viewer):
    """Template context for read receipt markup."""
    if message.sender_id != viewer.pk:
        return {'show': False}

    label = read_receipt_label(message, viewer)
    conversation = message.conversation
    is_team = conversation.conversation_type == Conversation.TYPE_TEAM
    team_others = 0
    read_count = 0

    if is_team:
        others = list(conversation.participants.exclude(user=viewer))
        team_others = len(others)
        read_count = sum(
            1 for p in others
            if p.last_read_at and p.last_read_at >= message.created_at
        )
    elif label:
        read_count = 1

    return {
        'show': True,
        'label': label,
        'is_team': is_team,
        'team_others': team_others,
        'read_count': read_count,
    }


def mark_conversation_read(conversation, user):
    participant = ensure_participant(conversation, user)
    previous_read = participant.last_read_at
    now = timezone.now()

    unread_qs = Message.objects.filter(conversation=conversation).exclude(sender=user)
    if previous_read:
        unread_qs = unread_qs.filter(created_at__gt=previous_read)
    had_unread = unread_qs.exists()

    participant.last_read_at = now
    participant.save(update_fields=['last_read_at'])

    if not had_unread and previous_read is not None:
        return

    notify_board_update('conversation.read', None, user.id, {
        'conversation_id': conversation.id,
        'reader_id': user.id,
        'reader_name': user_display_name(user),
        'read_at': participant.last_read_at.isoformat(),
        'conversation_type': conversation.conversation_type,
    }, organization_id=conversation.organization_id)


def check_message_rate_limit(user):
    key = f'taskpin:msg_rate:{user.pk}'
    count = cache.get(key, 0)
    if count >= MESSAGE_RATE_LIMIT:
        return False
    cache.set(key, count + 1, MESSAGE_RATE_WINDOW)
    return True


def get_inbox_entries(user):
    organization = get_user_organization(user)
    if organization is None:
        return []
    sync_team_participants(user)
    participants = (
        ConversationParticipant.objects
        .filter(user=user, conversation__organization=organization)
        .select_related('conversation', 'conversation__user_a', 'conversation__user_b')
        .prefetch_related('conversation__user_a__profile', 'conversation__user_b__profile')
    )
    entries = []
    for participant in participants:
        conversation = participant.conversation
        last_message = (
            conversation.messages
            .select_related('sender', 'sender__profile')
            .order_by('-created_at')
            .first()
        )
        entries.append({
            'conversation': conversation,
            'participant': participant,
            'title': conversation_title(conversation, user),
            'avatar': conversation_avatar_context(conversation, user),
            'last_message': last_message,
            'unread_count': unread_count_for_conversation(conversation, user),
            'is_team': conversation.conversation_type == Conversation.TYPE_TEAM,
        })

    def sort_key(entry):
        if entry['is_team']:
            return (0, entry['conversation'].updated_at)
        if entry['last_message']:
            return (1, entry['last_message'].created_at)
        return (2, entry['conversation'].created_at)

    entries.sort(key=sort_key, reverse=True)
    team_entries = [e for e in entries if e['is_team']]
    direct_entries = [e for e in entries if not e['is_team']]
    direct_entries.sort(
        key=lambda e: e['last_message'].created_at if e['last_message'] else e['conversation'].created_at,
        reverse=True,
    )
    return team_entries + direct_entries


def latest_unread_team_message(user):
    """Latest team chat message the user has not read (excludes own messages)."""
    organization = get_user_organization(user)
    if organization is None:
        return None, None
    sync_team_participants(user)
    conversation = Conversation.objects.filter(
        conversation_type=Conversation.TYPE_TEAM,
        organization=organization,
    ).first()
    if not conversation:
        return None, None
    participant = conversation.participants.filter(user=user).first()
    if not participant:
        return None, conversation
    qs = (
        Message.objects
        .filter(conversation=conversation)
        .exclude(sender=user)
        .select_related('sender', 'sender__profile')
        .order_by('-created_at')
    )
    if participant.last_read_at:
        qs = qs.filter(created_at__gt=participant.last_read_at)
    message = qs.first()
    return message, conversation


def serialize_attachments(message):
    return [
        {
            'id': attachment.pk,
            'name': attachment.original_name,
            'size': attachment.size_bytes,
            'is_image': attachment.is_image,
            'url': f'/messages/attachment/{attachment.pk}/',
        }
        for attachment in message.attachments.all()
    ]


def _claim_attachments(conversation, sender, attachment_ids):
    if not attachment_ids:
        return []
    if len(attachment_ids) > MAX_FILES_PER_MESSAGE:
        raise ValueError(f'You can attach up to {MAX_FILES_PER_MESSAGE} files per message.')
    attachments = list(
        MessageAttachment.objects.filter(
            pk__in=attachment_ids,
            conversation=conversation,
            uploaded_by=sender,
            message__isnull=True,
        )
    )
    if len(attachments) != len(set(attachment_ids)):
        raise ValueError('One or more attachments are invalid or already used.')
    return attachments


def send_message(conversation, sender, body, attachment_ids=None):
    body = (body or '').strip()
    attachment_ids = attachment_ids or []
    attachments = _claim_attachments(conversation, sender, attachment_ids)

    if not body and not attachments:
        raise ValueError('Enter a message or attach at least one file.')
    if body and len(body) > Message.MAX_BODY_LENGTH:
        raise ValueError(f'Message cannot exceed {Message.MAX_BODY_LENGTH} characters.')
    if not is_participant(conversation, sender):
        raise PermissionError('You are not a participant in this conversation.')
    if not check_message_rate_limit(sender):
        raise PermissionError('You are sending messages too quickly. Please wait a moment.')

    message = Message.objects.create(
        conversation=conversation,
        sender=sender,
        body=body,
    )
    if attachments:
        MessageAttachment.objects.filter(pk__in=[item.pk for item in attachments]).update(message=message)

    Conversation.objects.filter(pk=conversation.pk).update(updated_at=timezone.now())
    mark_conversation_read(conversation, sender)

    message = (
        Message.objects
        .prefetch_related('attachments')
        .get(pk=message.pk)
    )

    other_user_id = None
    if conversation.conversation_type == Conversation.TYPE_DIRECT:
        other = other_user_in_direct(conversation, sender)
        other_user_id = other.pk if other else None

    notify_board_update('message.new', None, sender.id, {
        'conversation_id': conversation.id,
        'message_id': message.id,
        'conversation_type': conversation.conversation_type,
        'sender_name': user_display_name(sender),
        'preview': message.preview,
        'recipient_user_id': other_user_id,
        'attachments': serialize_attachments(message),
    }, organization_id=conversation.organization_id)
    return message


def create_pending_attachment(conversation, sender, uploaded_file):
    from .message_attachments import check_upload_rate_limit, validate_upload_file

    if not is_participant(conversation, sender):
        raise PermissionError('You are not a participant in this conversation.')
    if not check_upload_rate_limit(sender):
        raise PermissionError('You are uploading files too quickly. Please wait a moment.')
    validate_upload_file(uploaded_file)

    return MessageAttachment.objects.create(
        conversation=conversation,
        uploaded_by=sender,
        file=uploaded_file,
        original_name=uploaded_file.name,
        content_type=getattr(uploaded_file, 'content_type', '') or '',
        size_bytes=uploaded_file.size,
    )
