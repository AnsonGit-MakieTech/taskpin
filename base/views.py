from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from datetime import datetime
from django.utils import timezone
from django.db.models import Case, When, IntegerField, Count, Q, Prefetch
from django.http import HttpResponseForbidden, JsonResponse, HttpResponse, FileResponse, Http404
from django.views.decorators.http import require_GET, require_POST
from functools import wraps

from .models import Task, ActivityLog, UserProfile, TaskAttachment
from .forms import TaskCreateForm, InviteMemberForm, RegisterForm, ProfileSettingsForm
from .permissions import is_admin, can_manage_task, can_delete_task, can_message_user
from .organizations import (
    organization_required,
    get_org_members,
    get_org_task,
    tasks_for_organization,
    activity_logs_for_organization,
    create_organization_with_admin,
    add_user_to_organization,
)
from .realtime import notify_board_update
from .filters import (
    DONE_PAGE_SIZE,
    ACTIVITY_PAGE_SIZE,
    filter_done_tasks,
    filter_activity_logs,
    filter_params,
)
from .file_uploads import validate_upload_batch
from . import task_attachments
from .calendar import (
    VIEW_WEEK,
    build_agenda_items,
    build_calendar_data,
    build_calendar_week_rows,
    build_next_7_days_agenda,
    build_week_calendar_data,
    calendar_has_visible_tasks,
    get_calendar_month_nav,
    get_calendar_week_nav,
    parse_calendar_filters,
    parse_calendar_view_params,
    weekday_labels,
)
from .scoreboard import (
    build_scoreboard_rows,
    get_scoreboard_stats,
    get_team_monthly_goal,
    level_milestone_crossed,
    member_all_time_xp,
    milestone_activity_message,
    parse_scoreboard_filters,
    rank_badge_for_level,
    xp_for_completed_task,
)


def admin_required(view_func):
    @wraps(view_func)
    @organization_required
    def wrapper(request, *args, **kwargs):
        if not is_admin(request.user):
            return HttpResponseForbidden('Admin access required.')
        return view_func(request, *args, **kwargs)
    return wrapper


PRIORITY_ORDER = Case(
    When(priority=Task.PRIORITY_URGENT, then=0),
    When(priority=Task.PRIORITY_IMPORTANT, then=1),
    When(priority=Task.PRIORITY_NORMAL, then=2),
    output_field=IntegerField(),
)


def _priority_task_groups(tasks):
    by_priority = {
        Task.PRIORITY_URGENT: [],
        Task.PRIORITY_IMPORTANT: [],
        Task.PRIORITY_NORMAL: [],
    }
    for task in tasks:
        by_priority.get(task.priority, by_priority[Task.PRIORITY_NORMAL]).append(task)
    return [
        {'label': 'Urgent', 'key': 'urgent', 'tasks': by_priority[Task.PRIORITY_URGENT]},
        {'label': 'Important', 'key': 'important', 'tasks': by_priority[Task.PRIORITY_IMPORTANT]},
        {'label': 'Normal', 'key': 'normal', 'tasks': by_priority[Task.PRIORITY_NORMAL]},
    ]


def _active_users(organization):
    return list(get_org_members(organization))


def _task_event_extra(task, previous_assigned_to_id=None):
    return {
        'assigned_to_id': task.assigned_to_id,
        'previous_assigned_to_id': previous_assigned_to_id,
        'status': task.status,
        'priority': task.priority,
    }


def _log_activity(request, action, task):
    ActivityLog.objects.create(
        organization=request.organization,
        actor=request.user,
        action=action,
        task=task,
    )


def _log_activity_for_org(organization, actor, action, task=None):
    ActivityLog.objects.create(
        organization=organization,
        actor=actor,
        action=action,
        task=task,
    )


def _maybe_log_level_milestone(request, task, assignee_old_xp: int):
    assignee = task.assigned_to
    if not assignee:
        return
    new_xp = assignee_old_xp + xp_for_completed_task(task)
    milestone = level_milestone_crossed(assignee_old_xp, new_xp)
    if milestone:
        _log_activity_for_org(
            request.organization,
            assignee,
            milestone_activity_message(assignee, milestone),
            task=task,
        )


def _scoreboard_monthly_goal_extra(organization):
    goal = get_team_monthly_goal(organization)
    return {
        'monthly_goal_current': goal.current,
        'monthly_goal_target': goal.target,
        'monthly_goal_reached': goal.reached,
    }


def _build_scoreboard_context(organization, filters, current_user):
    leaderboard, chart_max = build_scoreboard_rows(organization, filters)
    my_stats = next(
        (row for row in leaderboard if row['entry'].user.pk == current_user.pk),
        None,
    )
    total_completions = sum(row['entry'].done_count for row in leaderboard)
    return {
        'leaderboard': leaderboard,
        'podium': leaderboard[:3],
        'my_stats': my_stats,
        'filters': filters.as_template_dict(),
        'chart_max': chart_max,
        'total_completions': total_completions,
        'sort_metric': filters.sort,
        'period': filters.period,
        'monthly_goal': get_team_monthly_goal(organization),
    }


def _task_attachment_prefetch():
    return Prefetch('attachments', queryset=TaskAttachment.objects.order_by('created_at'))


def _tasks_with_attachments(queryset):
    return queryset.prefetch_related(_task_attachment_prefetch())


def _parse_id_list(post, field_name):
    ids = []
    for raw_id in post.getlist(field_name):
        if str(raw_id).isdigit():
            ids.append(int(raw_id))
    return ids


def _apply_task_attachment_changes(request, task):
    remove_ids = _parse_id_list(request.POST, 'remove_attachment_ids')
    if remove_ids:
        for attachment in task.attachments.filter(pk__in=remove_ids, uploaded_by=request.user):
            task_attachments.delete_task_attachment(attachment)

    new_ids = _parse_id_list(request.POST, 'attachment_ids')
    if new_ids:
        task_attachments.attach_existing_to_task(task, new_ids, request.user)


def _delete_task_files(task):
    for attachment in task.attachments.all():
        if attachment.file:
            attachment.file.delete(save=False)


@organization_required
def team_board(request):
    org = request.organization
    users = get_org_members(org)

    unassigned_tasks = list(
        _tasks_with_attachments(
            tasks_for_organization(org)
            .filter(status=Task.STATUS_UNASSIGNED, assigned_to__isnull=True)
            .select_related('created_by', 'created_by__profile')
        )
        .annotate(priority_order=PRIORITY_ORDER)
        .order_by('priority_order', 'due_date')
    )

    board = []
    member_stats = {
        entry.user.pk: entry
        for entry in get_scoreboard_stats(org, members=users)
    }
    for user in users:
        tasks = list(
            _tasks_with_attachments(
                tasks_for_organization(org)
                .filter(assigned_to=user, status=Task.STATUS_ASSIGNED)
                .select_related('created_by', 'created_by__profile')
            )
            .annotate(priority_order=PRIORITY_ORDER)
            .order_by('priority_order', 'due_date')
        )
        stats = member_stats.get(user.pk)
        level = stats.level if stats else 1
        board.append({
            'user': user,
            'tasks': tasks,
            'groups': _priority_task_groups(tasks),
            'level': level,
            'rank_badge': rank_badge_for_level(level),
        })

    all_users = list(users)
    return render(request, 'board/team_board.html', {
        'board': board,
        'unassigned_tasks': unassigned_tasks,
        'unassigned_groups': _priority_task_groups(unassigned_tasks),
        'all_users': all_users,
    })


@organization_required
def task_create(request):
    form = TaskCreateForm(request.POST or None, organization=request.organization)
    if request.method == 'POST' and form.is_valid():
        task = form.save(commit=False)
        task.organization = request.organization
        task.created_by = request.user
        assigned_to = form.cleaned_data.get('assign_to')
        if assigned_to:
            task.assigned_to = assigned_to
            task.status = Task.STATUS_ASSIGNED
        else:
            task.status = Task.STATUS_UNASSIGNED
        task.save()
        try:
            task_attachments.claim_task_attachments(
                request.organization,
                request.user,
                task,
                _parse_id_list(request.POST, 'attachment_ids'),
            )
        except ValueError as exc:
            form.add_error(None, str(exc))
            users = get_org_members(request.organization)
            return render(request, 'board/task_form.html', {'form': form, 'users': users})
        _log_activity(
            request,
            f'Created task "{task.title}"'
            + (f' and assigned to {assigned_to.get_full_name() or assigned_to.username}' if assigned_to else ''),
            task,
        )
        notify_board_update(
            'task.created', task.id, request.user.id,
            _task_event_extra(task),
            organization_id=request.organization.pk,
        )
        return redirect('team_board')

    users = get_org_members(request.organization)
    initial_due = request.GET.get('due', '').strip()
    if initial_due and not request.method == 'POST':
        from .filters import parse_date
        due_day = parse_date(initial_due)
        if due_day:
            due_dt = timezone.make_aware(datetime.combine(due_day, datetime.min.time().replace(hour=9)))
            form.initial['due_date'] = due_dt.strftime('%Y-%m-%dT%H:%M')
    return render(request, 'board/task_form.html', {'form': form, 'users': users})


@organization_required
def my_board(request):
    base_qs = _tasks_with_attachments(
        tasks_for_organization(request.organization)
        .filter(assigned_to=request.user, status=Task.STATUS_ASSIGNED)
        .select_related('created_by', 'created_by__profile')
        .order_by('due_date', 'created_at')
    )
    urgent = list(base_qs.filter(priority=Task.PRIORITY_URGENT))
    important = list(base_qs.filter(priority=Task.PRIORITY_IMPORTANT))
    normal = list(base_qs.filter(priority=Task.PRIORITY_NORMAL))
    all_tasks = urgent + important + normal
    groups = [
        {'label': 'Urgent', 'key': 'urgent', 'tasks': urgent},
        {'label': 'Important', 'key': 'important', 'tasks': important},
        {'label': 'Normal', 'key': 'normal', 'tasks': normal},
    ]
    all_users = list(get_org_members(request.organization))
    return render(request, 'board/my_board.html', {
        'groups': groups,
        'task_count': len(all_tasks),
        'all_users': all_users,
    })


@organization_required
def done_tasks(request):
    queryset = filter_done_tasks(
        tasks_for_organization(request.organization)
        .filter(status=Task.STATUS_DONE)
        .select_related('created_by', 'assigned_to', 'created_by__profile', 'assigned_to__profile')
        .prefetch_related(_task_attachment_prefetch())
        .order_by('-completed_at'),
        request,
    )
    paginator = Paginator(queryset, DONE_PAGE_SIZE)
    page_obj = paginator.get_page(request.GET.get('page'))
    members = get_org_members(request.organization).order_by('first_name', 'username')
    return render(request, 'board/done_tasks.html', {
        'page_obj': page_obj,
        'tasks': page_obj.object_list,
        'members': members,
        'filters': filter_params(request),
    })


@organization_required
def mark_done(request, task_id):
    task = get_org_task(request.user, task_id)
    if not can_manage_task(request.user, task):
        return HttpResponseForbidden('You cannot mark this task as done.')
    if request.method == 'POST':
        remarks = request.POST.get('completion_remarks', '').strip()[:500]
        assignee_old_xp = (
            member_all_time_xp(request.organization, task.assigned_to_id)
            if task.assigned_to_id
            else 0
        )
        task.status = Task.STATUS_DONE
        task.completed_at = timezone.now()
        task.completion_remarks = remarks
        task.save()
        action = f'Marked "{task.title}" as done'
        if remarks:
            preview = remarks if len(remarks) <= 120 else remarks[:117] + '…'
            action = f'{action} — {preview}'
        _log_activity(request, action[:300], task)
        _maybe_log_level_milestone(request, task, assignee_old_xp)
        notify_board_update(
            'task.done',
            task.id,
            request.user.id,
            {
                **_task_event_extra(task, previous_assigned_to_id=task.assigned_to_id),
                **_scoreboard_monthly_goal_extra(request.organization),
            },
            organization_id=task.organization_id,
        )
    return redirect('team_board')


@organization_required
def task_reassign(request, task_id):
    if not is_admin(request.user):
        return HttpResponseForbidden('Only admins can move tasks.')
    task = get_org_task(request.user, task_id)
    if request.method == 'POST':
        previous_assigned_to_id = task.assigned_to_id
        new_user_id = request.POST.get('assigned_to')
        if new_user_id:
            new_user = get_object_or_404(
                User,
                pk=new_user_id,
                organization_membership__organization=request.organization,
                is_active=True,
            )
            old_assignee = task.assigned_to
            task.assigned_to = new_user
            task.status = Task.STATUS_ASSIGNED
            task.save()
            old_name = old_assignee.get_full_name() or old_assignee.username if old_assignee else 'Unassigned'
            new_name = new_user.get_full_name() or new_user.username
            _log_activity(request, f'Moved "{task.title}" from {old_name} to {new_name}', task)
            notify_board_update(
                'task.moved',
                task.id,
                request.user.id,
                _task_event_extra(task, previous_assigned_to_id=previous_assigned_to_id),
                organization_id=task.organization_id,
            )
        else:
            task.assigned_to = None
            task.status = Task.STATUS_UNASSIGNED
            task.save()
            _log_activity(request, f'Unassigned "{task.title}"', task)
            notify_board_update(
                'task.moved',
                task.id,
                request.user.id,
                _task_event_extra(task, previous_assigned_to_id=previous_assigned_to_id),
                organization_id=task.organization_id,
            )
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'ok': True,
                'task_id': task.id,
                'assigned_to_id': task.assigned_to_id,
            })
    return redirect('team_board')


@organization_required
def task_edit(request, task_id):
    task = get_org_task(request.user, task_id)
    if not can_manage_task(request.user, task):
        return HttpResponseForbidden('You cannot edit this task.')
    form = TaskCreateForm(request.POST or None, instance=task, organization=request.organization)

    if request.method == 'POST' and form.is_valid():
        previous_assigned_to_id = task.assigned_to_id
        task = form.save(commit=False)
        assigned_to = form.cleaned_data.get('assign_to')
        if assigned_to:
            task.assigned_to = assigned_to
            task.status = Task.STATUS_ASSIGNED
        else:
            task.assigned_to = None
            task.status = Task.STATUS_UNASSIGNED
        task.save()
        try:
            _apply_task_attachment_changes(request, task)
        except ValueError as exc:
            form.add_error(None, str(exc))
            users = get_org_members(request.organization)
            return render(request, 'board/task_form.html', {
                'form': form,
                'users': users,
                'task': task,
                'existing_attachments': task.attachments.all(),
            })
        _log_activity(request, f'Edited task "{task.title}"', task)
        notify_board_update(
            'task.edited',
            task.id,
            request.user.id,
            _task_event_extra(task, previous_assigned_to_id=previous_assigned_to_id),
            organization_id=task.organization_id,
        )
        return redirect('team_board')

    users = get_org_members(request.organization)
    if task.assigned_to and not form.is_bound:
        form.initial['assign_to'] = task.assigned_to.pk

    return render(request, 'board/task_form.html', {
        'form': form,
        'users': users,
        'task': task,
        'existing_attachments': task.attachments.all() if task else None,
    })


@organization_required
def task_delete(request, task_id):
    task = get_org_task(request.user, task_id)
    if not can_delete_task(request.user, task):
        return HttpResponseForbidden('You cannot delete this task.')
    if request.method == 'POST':
        title = task.title
        task_id = task.id
        assigned_to_id = task.assigned_to_id
        org_id = task.organization_id
        _delete_task_files(task)
        _log_activity(request, f'Deleted task "{title}"', task)
        task.delete()
        notify_board_update('task.deleted', task_id, request.user.id, {
            'assigned_to_id': assigned_to_id,
            'previous_assigned_to_id': assigned_to_id,
            'status': 'deleted',
            'priority': None,
        }, organization_id=org_id)
    return redirect('team_board')


ACTIVITY_LOG_PAGE_SIZE = ACTIVITY_PAGE_SIZE


@organization_required
def activity_log(request):
    queryset = filter_activity_logs(
        activity_logs_for_organization(request.organization)
        .select_related('actor', 'actor__profile', 'task')
        .order_by('-timestamp'),
        request,
    )
    paginator = Paginator(queryset, ACTIVITY_LOG_PAGE_SIZE)
    page_obj = paginator.get_page(request.GET.get('page'))
    members = get_org_members(request.organization).order_by('first_name', 'username')
    return render(request, 'activity/activity_log.html', {
        'page_obj': page_obj,
        'entries': page_obj.object_list,
        'members': members,
        'filters': filter_params(request),
    })


@organization_required
def scoreboard(request):
    filters = parse_scoreboard_filters(request)
    context = _build_scoreboard_context(request.organization, filters, request.user)
    return render(request, 'scoreboard/scoreboard.html', context)


@organization_required
@require_GET
def scoreboard_fragment(request):
    filters = parse_scoreboard_filters(request)
    context = _build_scoreboard_context(request.organization, filters, request.user)
    return render(request, 'scoreboard/_scoreboard_live.html', context)


@organization_required
def calendar_view(request):
    today = timezone.localdate()
    view_params = parse_calendar_view_params(request, today=today)
    filters = parse_calendar_filters(request)

    if view_params.view == VIEW_WEEK:
        data = build_week_calendar_data(
            request.organization,
            view_params.anchor_date,
            filters,
            request.user,
            today=today,
            week_start=view_params.week_start,
        )
        period_nav = get_calendar_week_nav(view_params.anchor_date, view_params.week_start)
    else:
        data = build_calendar_data(
            request.organization,
            view_params.year,
            view_params.month,
            filters,
            request.user,
            today=today,
            week_start=view_params.week_start,
        )
        period_nav = get_calendar_month_nav(view_params.year, view_params.month)

    week_rows = build_calendar_week_rows(data.weeks, data.tasks_by_date)
    members = get_org_members(request.organization).order_by('first_name', 'username')
    next_7_days = build_next_7_days_agenda(
        request.organization,
        filters,
        request.user,
        today=today,
    )
    show_grid = view_params.view == VIEW_WEEK or calendar_has_visible_tasks(data)

    return render(request, 'calendar/calendar.html', {
        'calendar_month': data.month,
        'week_rows': week_rows,
        'weekday_labels': weekday_labels(view_params.week_start),
        'summary': data.summary,
        'unscheduled': data.unscheduled,
        'filters': filters.as_template_dict(),
        'month_nav': period_nav if view_params.view != VIEW_WEEK else get_calendar_month_nav(
            view_params.year, view_params.month,
        ),
        'week_nav': period_nav if view_params.view == VIEW_WEEK else None,
        'has_visible_tasks': calendar_has_visible_tasks(data),
        'show_grid': show_grid,
        'agenda_items': build_agenda_items(data, today=today),
        'next_7_days': next_7_days,
        'members': members,
        'year': view_params.year,
        'month': view_params.month,
        'today': today,
        'view_mode': view_params.view,
        'anchor_date': view_params.anchor_date,
        'week_start_key': view_params.week_start_key,
        'is_week_view': view_params.view == VIEW_WEEK,
    })


@organization_required
def user_settings(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    form = ProfileSettingsForm(
        request.POST or None,
        request.FILES or None,
        user=request.user,
        profile=profile,
    )

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Profile updated.')
        return redirect('user_settings')

    role_label = 'Admin' if is_admin(request.user) else profile.get_role_display()

    return render(request, 'settings/settings.html', {
        'form': form,
        'profile': profile,
        'role_label': role_label,
    })


@organization_required
def team_list(request):
    org = request.organization
    members = (
        get_org_members(org)
        .annotate(
            active_task_count=Count(
                'assigned_tasks',
                filter=Q(
                    assigned_tasks__status=Task.STATUS_ASSIGNED,
                    assigned_tasks__organization=org,
                ),
            )
        )
    )
    return render(request, 'team/team_list.html', {
        'members': members,
        'is_admin': is_admin(request.user),
    })


@admin_required
def invite_member(request):
    form = InviteMemberForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = User.objects.create_user(
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password'],
            first_name=form.cleaned_data['first_name'],
            last_name=form.cleaned_data['last_name'],
        )
        add_user_to_organization(
            request.organization,
            user,
            role=form.cleaned_data['role'],
        )
        return redirect('team_list')

    return render(request, 'team/invite_form.html', {'form': form})


def register(request):
    if request.user.is_authenticated:
        return redirect('team_board')

    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = User.objects.create_user(
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password1'],
            first_name=form.cleaned_data['first_name'],
            last_name=form.cleaned_data['last_name'],
        )
        create_organization_with_admin(form.cleaned_data['organization_name'], user)
        login(request, user)
        return redirect('team_board')

    return render(request, 'registration/register.html', {'form': form})


@organization_required
def task_card_fragment(request, task_id):
    task = get_org_task(request.user, task_id)
    if task.status != Task.STATUS_ASSIGNED and task.status != Task.STATUS_UNASSIGNED:
        return HttpResponse(status=404)
    task = (
        Task.objects
        .select_related('created_by', 'created_by__profile')
        .prefetch_related(_task_attachment_prefetch())
        .get(pk=task.pk)
    )
    card_variant = request.GET.get('variant', '').strip()
    if card_variant == 'myboard':
        card_variant = 'sticky'
    html = render(request, 'board/_task_card.html', {
        'task': task,
        'all_users': _active_users(request.organization),
        'card_variant': card_variant if card_variant == 'sticky' else '',
    }).content.decode('utf-8')
    return HttpResponse(html)


@organization_required
def task_done_row_fragment(request, task_id):
    task = get_org_task(request.user, task_id)
    if task.status != Task.STATUS_DONE:
        return HttpResponse(status=404)
    task = (
        Task.objects
        .prefetch_related(_task_attachment_prefetch())
        .select_related('created_by', 'assigned_to', 'created_by__profile', 'assigned_to__profile')
        .get(pk=task.pk)
    )
    html = render(request, 'board/_done_row.html', {'task': task}).content.decode('utf-8')
    return HttpResponse(html)


@organization_required
@require_POST
def task_upload(request):
    task_id = request.POST.get('task_id')
    task = None
    if task_id:
        task = get_org_task(request.user, task_id)
        if not can_manage_task(request.user, task):
            return HttpResponseForbidden('You cannot edit this task.')

    try:
        files = validate_upload_batch(request.FILES.getlist('files'))
    except ValueError as exc:
        return JsonResponse({'ok': False, 'error': str(exc)}, status=400)

    uploaded = []
    try:
        for uploaded_file in files:
            attachment = task_attachments.create_pending_task_attachment(
                request.organization,
                request.user,
                uploaded_file,
                task=task,
            )
            uploaded.append({
                'id': attachment.pk,
                'name': attachment.original_name,
                'size': attachment.size_bytes,
                'is_image': attachment.is_image,
                'url': f'/task/attachment/{attachment.pk}/',
            })
    except PermissionError as exc:
        return JsonResponse({'ok': False, 'error': str(exc)}, status=429)
    except ValueError as exc:
        return JsonResponse({'ok': False, 'error': str(exc)}, status=400)

    return JsonResponse({'ok': True, 'attachments': uploaded})


@organization_required
@require_GET
def task_attachment(request, attachment_id):
    attachment = get_object_or_404(
        TaskAttachment.objects.select_related('task', 'organization'),
        pk=attachment_id,
        organization=request.organization,
    )
    if not attachment.task_id and attachment.uploaded_by_id != request.user.pk:
        return HttpResponseForbidden('You cannot access this file.')

    if not attachment.file:
        raise Http404('File not found.')

    disposition = 'inline' if attachment.is_image else 'attachment'
    response = FileResponse(
        attachment.file.open('rb'),
        content_type=attachment.content_type or 'application/octet-stream',
    )
    response['Content-Disposition'] = f'{disposition}; filename="{attachment.original_name}"'
    response['Content-Length'] = attachment.size_bytes
    return response


@organization_required
@require_POST
def task_attachment_delete(request, attachment_id):
    attachment = get_object_or_404(
        TaskAttachment.objects.select_related('task'),
        pk=attachment_id,
        organization=request.organization,
    )
    if attachment.task_id:
        if not can_manage_task(request.user, attachment.task):
            return HttpResponseForbidden('You cannot delete this file.')
    elif attachment.uploaded_by_id != request.user.pk:
        return HttpResponseForbidden('You cannot delete this file.')

    task_attachments.delete_task_attachment(attachment)
    return JsonResponse({'ok': True})


DEADLINE_LABELS = {
    'overdue': 'Overdue',
    'due_today': 'Due today',
    'due_soon': 'Due within 24 hours',
}


@organization_required
def deadline_reminders(request):
    tasks = (
        tasks_for_organization(request.organization)
        .filter(assigned_to=request.user, status=Task.STATUS_ASSIGNED, due_date__isnull=False)
        .order_by('due_date')
    )
    reminders = []
    for task in tasks:
        urgency = task.deadline_urgency
        if not urgency:
            continue
        reminders.append({
            'task_id': task.id,
            'title': task.title,
            'urgency': urgency,
            'label': DEADLINE_LABELS[urgency],
            'due_date': timezone.localtime(task.due_date).strftime('%b %d, %I:%M %p'),
        })
    return JsonResponse({'reminders': reminders})
