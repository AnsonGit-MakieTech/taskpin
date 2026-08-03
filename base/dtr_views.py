"""Daily Time Record views."""

from django.contrib import messages
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.http import HttpResponseForbidden, JsonResponse, HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from .dtr import (
    DTR_PAGE_SIZE,
    daily_summary,
    entries_for_organization,
    format_hours,
    get_open_entry,
    get_org_time_entry,
    status_payload,
    today_hours,
    week_start_for_date,
    weekly_hours,
)
from .filters import (
    dtr_filter_params,
    dtr_team_filter_params,
    filter_dtr_entries,
    filter_dtr_team_entries,
)
from .models import ActivityLog, TimeEntry
from .organizations import get_org_members, organization_required
from .permissions import is_admin
from .realtime import notify_dtr_update


def _log_dtr_activity(request, action):
    ActivityLog.objects.create(
        organization=request.organization,
        actor=request.user,
        action=action[:300],
        task=None,
    )


def _parse_break_minutes(value):
    try:
        minutes = int(value or 0)
    except (TypeError, ValueError):
        return 0
    return max(0, min(minutes, 480))


def _my_dtr_member_context(org, user):
    today = timezone.localdate()
    week_start = week_start_for_date(today)
    return {
        'recent_entries': entries_for_organization(org, user=user)[:5],
        'today_hours_display': format_hours(today_hours(user, org)),
        'week_hours_display': format_hours(weekly_hours(user, org, week_start)),
    }


def _timesheet_member_context(org, user, request):
    queryset = filter_dtr_entries(
        entries_for_organization(org, user=user),
        request,
    )
    paginator = Paginator(queryset, DTR_PAGE_SIZE)
    page_obj = paginator.get_page(request.GET.get('page'))
    return {
        'page_obj': page_obj,
        'entries': page_obj.object_list,
    }


@organization_required
def dtr_my(request):
    org = request.organization
    user = request.user
    open_entry = get_open_entry(user, org)
    member_context = _my_dtr_member_context(org, user)
    return render(request, 'dtr/my_dtr.html', {
        'open_entry': open_entry,
        'today_hours': today_hours(user, org),
        'week_start': week_start_for_date(timezone.localdate()),
        'is_admin': is_admin(user),
        **member_context,
    })


@organization_required
@require_POST
def dtr_clock_in(request):
    org = request.organization
    if get_open_entry(request.user, org):
        messages.error(request, 'You are already clocked in.')
        return redirect('dtr_my')
    try:
        entry = TimeEntry.objects.create(
            organization=org,
            user=request.user,
            clock_in=timezone.now(),
            status=TimeEntry.STATUS_OPEN,
        )
    except IntegrityError:
        messages.error(request, 'You are already clocked in.')
        return redirect('dtr_my')
    _log_dtr_activity(request, f'{request.user.profile.display_name()} clocked in')
    notify_dtr_update('dtr.clock_in', entry, request.user.id)
    messages.success(request, 'Clocked in. Have a productive shift!')
    return redirect('dtr_my')


@organization_required
@require_POST
def dtr_clock_out(request):
    org = request.organization
    entry = get_open_entry(request.user, org)
    if not entry:
        messages.error(request, 'You are not clocked in.')
        return redirect('dtr_my')

    notes = request.POST.get('notes', '').strip()[:500]
    break_minutes = _parse_break_minutes(request.POST.get('break_minutes'))

    entry.clock_out = timezone.now()
    entry.break_minutes = break_minutes
    entry.notes = notes
    entry.status = TimeEntry.STATUS_PENDING
    entry.save(update_fields=['clock_out', 'break_minutes', 'notes', 'status'])

    _log_dtr_activity(
        request,
        f'{request.user.profile.display_name()} clocked out ({entry.duration_display})',
    )
    notify_dtr_update('dtr.clock_out', entry, request.user.id)
    messages.success(request, 'Clocked out. Your time entry is pending approval.')
    return redirect('dtr_my')


@organization_required
@require_GET
def dtr_status_api(request):
    return JsonResponse(status_payload(request.user, request.organization))


@organization_required
def dtr_timesheet(request):
    org = request.organization
    user = request.user
    timesheet_context = _timesheet_member_context(org, user, request)
    return render(request, 'dtr/timesheet.html', {
        **timesheet_context,
        'filters': dtr_filter_params(request),
        'status_choices': TimeEntry.STATUS_CHOICES,
        'is_admin': is_admin(user),
    })


@organization_required
def dtr_team(request):
    if not is_admin(request.user):
        return HttpResponseForbidden('Only admins can review team time records.')

    org = request.organization
    team_context = _team_dtr_context(org, request)
    members = get_org_members(org)
    return render(request, 'dtr/team_dtr.html', {
        **team_context,
        'members': members,
        'filters': dtr_team_filter_params(request),
        'status_choices': TimeEntry.STATUS_CHOICES,
    })


@organization_required
@require_POST
def dtr_approve(request, entry_id):
    if not is_admin(request.user):
        return HttpResponseForbidden('Only admins can approve time entries.')

    entry = get_org_time_entry(request.user, request.organization, entry_id)
    if entry.status not in (TimeEntry.STATUS_PENDING, TimeEntry.STATUS_REJECTED):
        messages.error(request, 'This entry cannot be approved.')
        return redirect('dtr_team')

    entry.status = TimeEntry.STATUS_APPROVED
    entry.approved_by = request.user
    entry.approved_at = timezone.now()
    entry.admin_notes = request.POST.get('admin_notes', '').strip()[:500]
    entry.save(update_fields=['status', 'approved_by', 'approved_at', 'admin_notes'])

    name = entry.user.profile.display_name()
    _log_dtr_activity(request, f'Approved time entry for {name} ({entry.duration_display})')
    notify_dtr_update('dtr.approved', entry, request.user.id)
    messages.success(request, f'Approved {name}\'s time entry.')
    return redirect('dtr_team')


@organization_required
@require_POST
def dtr_reject(request, entry_id):
    if not is_admin(request.user):
        return HttpResponseForbidden('Only admins can reject time entries.')

    admin_notes = request.POST.get('admin_notes', '').strip()[:500]
    if not admin_notes:
        messages.error(request, 'Please add a note explaining the rejection.')
        return redirect('dtr_team')

    entry = get_org_time_entry(request.user, request.organization, entry_id)
    if entry.status not in (TimeEntry.STATUS_PENDING, TimeEntry.STATUS_APPROVED):
        messages.error(request, 'This entry cannot be rejected.')
        return redirect('dtr_team')

    entry.status = TimeEntry.STATUS_REJECTED
    entry.approved_by = request.user
    entry.approved_at = timezone.now()
    entry.admin_notes = admin_notes
    entry.save(update_fields=['status', 'approved_by', 'approved_at', 'admin_notes'])

    name = entry.user.profile.display_name()
    _log_dtr_activity(request, f'Rejected time entry for {name}')
    notify_dtr_update('dtr.rejected', entry, request.user.id)
    messages.success(request, f'Rejected {name}\'s time entry.')
    return redirect('dtr_team')


def _team_dtr_context(org, request):
    today = timezone.localdate()
    queryset, entry_date = filter_dtr_team_entries(
        entries_for_organization(org),
        request,
        today,
    )
    summary = daily_summary(org, entry_date)
    return {
        'entries': queryset,
        'entry_date': entry_date,
        'summary': summary,
    }


@organization_required
@require_GET
def dtr_team_fragment(request):
    if not is_admin(request.user):
        return HttpResponseForbidden('Only admins can review team time records.')

    context = _team_dtr_context(request.organization, request)
    html = render(request, 'dtr/_team_live.html', context).content.decode('utf-8')
    return HttpResponse(html)


@organization_required
@require_GET
def dtr_my_fragment(request):
    context = _my_dtr_member_context(request.organization, request.user)
    html = render(request, 'dtr/_my_member_live.html', context).content.decode('utf-8')
    return HttpResponse(html)


@organization_required
@require_GET
def dtr_timesheet_fragment(request):
    context = _timesheet_member_context(request.organization, request.user, request)
    html = render(request, 'dtr/_timesheet_live.html', context).content.decode('utf-8')
    return HttpResponse(html)
