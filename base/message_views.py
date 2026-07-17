from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.http import FileResponse, Http404, HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

from .models import Conversation, Message, MessageAttachment
from . import messaging
from .message_attachments import validate_upload_batch
from .organizations import get_org_members, get_user_organization, organization_required
from .permissions import can_message_user

MESSAGES_PAGE_SIZE = 50
MESSAGE_PREFETCH = ('attachments',)


def _render_message_bubble(request, message, show_sender):
    return render(request, 'messages/_message_bubble.html', {
        'message': message,
        'show_sender': show_sender,
    }).content.decode('utf-8')


def _messages_queryset(conversation):
    return (
        conversation.messages
        .select_related('sender', 'sender__profile')
        .prefetch_related(*MESSAGE_PREFETCH)
        .order_by('-created_at')
    )


def _conversation_or_403(conversation_id, user):
    organization = get_user_organization(user)
    conversation = get_object_or_404(
        Conversation.objects.select_related('user_a', 'user_b', 'user_a__profile', 'user_b__profile'),
        pk=conversation_id,
        organization=organization,
    )
    if not messaging.is_participant(conversation, user):
        return None, HttpResponseForbidden('You cannot access this conversation.')
    return conversation, None


@organization_required
def messages_inbox(request, conversation_id=None):
    messaging.sync_team_participants(request.user)
    inbox_entries = messaging.get_inbox_entries(request.user)
    active_conversation = None
    thread_messages = []
    page_obj = None

    if conversation_id:
        active_conversation, denied = _conversation_or_403(conversation_id, request.user)
        if denied:
            return denied

    if active_conversation:
        messaging.mark_conversation_read(active_conversation, request.user)
        queryset = _messages_queryset(active_conversation)
        paginator = Paginator(queryset, MESSAGES_PAGE_SIZE)
        page_obj = paginator.get_page(request.GET.get('page'))
        thread_messages = list(reversed(page_obj.object_list))

    teammates = (
        get_org_members(request.organization)
        .exclude(pk=request.user.pk)
    )

    team_others_count = 0
    if active_conversation and active_conversation.conversation_type == Conversation.TYPE_TEAM:
        team_others_count = active_conversation.participants.exclude(user=request.user).count()

    return render(request, 'messages/inbox.html', {
        'inbox_entries': inbox_entries,
        'active_conversation': active_conversation,
        'active_title': messaging.conversation_title(active_conversation, request.user) if active_conversation else '',
        'active_avatar': messaging.conversation_avatar_context(active_conversation, request.user) if active_conversation else None,
        'is_team_chat': active_conversation.conversation_type == Conversation.TYPE_TEAM if active_conversation else False,
        'thread_messages': thread_messages,
        'page_obj': page_obj,
        'teammates': teammates,
        'team_others_count': team_others_count,
        'unread_message_count': messaging.unread_count_for_user(request.user),
    })


@organization_required
def message_start_direct(request, user_id):
    other_user = get_object_or_404(
        User,
        pk=user_id,
        is_active=True,
        organization_membership__organization=request.organization,
    )
    if other_user.pk == request.user.pk:
        return redirect('messages_inbox')
    if not can_message_user(request.user, other_user):
        return HttpResponseForbidden('You can only message members of your organization.')
    conversation = messaging.get_or_create_direct_conversation(request.user, other_user)
    return redirect('messages_conversation', conversation_id=conversation.pk)


@organization_required
@require_POST
def message_upload(request):
    conversation_id = request.POST.get('conversation_id')
    conversation, denied = _conversation_or_403(conversation_id, request.user)
    if denied:
        return denied

    try:
        files = validate_upload_batch(request.FILES.getlist('files'))
    except ValueError as exc:
        return JsonResponse({'ok': False, 'error': str(exc)}, status=400)

    uploaded = []
    try:
        for uploaded_file in files:
            attachment = messaging.create_pending_attachment(
                conversation, request.user, uploaded_file,
            )
            uploaded.append({
                'id': attachment.pk,
                'name': attachment.original_name,
                'size': attachment.size_bytes,
                'is_image': attachment.is_image,
                'url': f'/messages/attachment/{attachment.pk}/',
            })
    except PermissionError as exc:
        return JsonResponse({'ok': False, 'error': str(exc)}, status=429)
    except ValueError as exc:
        return JsonResponse({'ok': False, 'error': str(exc)}, status=400)

    return JsonResponse({'ok': True, 'attachments': uploaded})


@organization_required
@require_POST
def message_send(request):
    conversation_id = request.POST.get('conversation_id')
    conversation, denied = _conversation_or_403(conversation_id, request.user)
    if denied:
        return denied

    attachment_ids = []
    for raw_id in request.POST.getlist('attachment_ids'):
        if str(raw_id).isdigit():
            attachment_ids.append(int(raw_id))

    try:
        body = request.POST.get('body', '')
        message = messaging.send_message(
            conversation, request.user, body, attachment_ids=attachment_ids,
        )
    except ValueError as exc:
        return JsonResponse({'ok': False, 'error': str(exc)}, status=400)
    except PermissionError as exc:
        return JsonResponse({'ok': False, 'error': str(exc)}, status=429)

    html = _render_message_bubble(
        request, message, conversation.conversation_type == Conversation.TYPE_TEAM,
    )

    return JsonResponse({
        'ok': True,
        'message_id': message.id,
        'html': html,
        'created_at': message.created_at.isoformat(),
        'preview': message.preview,
        'attachments': messaging.serialize_attachments(message),
    })


@organization_required
@require_POST
def message_mark_read(request):
    conversation_id = request.POST.get('conversation_id')
    conversation, denied = _conversation_or_403(conversation_id, request.user)
    if denied:
        return denied
    messaging.mark_conversation_read(conversation, request.user)
    return JsonResponse({
        'ok': True,
        'unread_message_count': messaging.unread_count_for_user(request.user),
    })


@organization_required
def message_history(request, conversation_id):
    conversation, denied = _conversation_or_403(conversation_id, request.user)
    if denied:
        return denied

    before_id = request.GET.get('before')
    qs = _messages_queryset(conversation)
    if before_id:
        qs = qs.filter(pk__lt=before_id)

    messages = list(reversed(list(qs[:MESSAGES_PAGE_SIZE])))
    html_parts = []
    show_sender = conversation.conversation_type == Conversation.TYPE_TEAM
    for message in messages:
        html_parts.append(_render_message_bubble(request, message, show_sender))

    return JsonResponse({
        'ok': True,
        'html': ''.join(html_parts),
        'has_more': qs.count() > MESSAGES_PAGE_SIZE,
        'oldest_id': messages[0].pk if messages else None,
    })


@organization_required
def message_bubble_fragment(request, message_id):
    organization = get_user_organization(request.user)
    message = get_object_or_404(
        Message.objects.select_related('sender', 'sender__profile', 'conversation').prefetch_related(*MESSAGE_PREFETCH),
        pk=message_id,
        conversation__organization=organization,
    )
    conversation = message.conversation
    if not messaging.is_participant(conversation, request.user):
        return HttpResponseForbidden('You cannot access this message.')
    html = _render_message_bubble(
        request, message, conversation.conversation_type == Conversation.TYPE_TEAM,
    )
    return HttpResponse(html)


@organization_required
@require_GET
def message_attachment(request, attachment_id):
    organization = get_user_organization(request.user)
    attachment = get_object_or_404(
        MessageAttachment.objects.select_related('conversation', 'message'),
        pk=attachment_id,
        conversation__organization=organization,
    )
    if not messaging.is_participant(attachment.conversation, request.user):
        return HttpResponseForbidden('You cannot access this file.')
    if not attachment.file:
        raise Http404('File not found.')

    disposition = 'inline' if attachment.is_image else 'attachment'
    response = FileResponse(attachment.file.open('rb'), content_type=attachment.content_type or 'application/octet-stream')
    response['Content-Disposition'] = f'{disposition}; filename="{attachment.original_name}"'
    response['Content-Length'] = attachment.size_bytes
    return response


@organization_required
def unread_count_api(request):
    return JsonResponse({
        'unread_message_count': messaging.unread_count_for_user(request.user),
    })
