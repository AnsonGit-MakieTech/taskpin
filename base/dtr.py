"""Daily Time Record queries and hour calculations."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Optional

from django.contrib.auth.models import User
from django.db.models import Count, Q, QuerySet
from django.utils import timezone

from .models import Organization, TimeEntry


DTR_PAGE_SIZE = 25

COUNTABLE_STATUSES = (
    TimeEntry.STATUS_OPEN,
    TimeEntry.STATUS_PENDING,
    TimeEntry.STATUS_APPROVED,
)


def entries_for_organization(
    organization: Organization,
    *,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    user: Optional[User] = None,
    status: Optional[str] = None,
) -> QuerySet:
    qs = (
        TimeEntry.objects
        .filter(organization=organization)
        .select_related('user', 'user__profile', 'approved_by', 'approved_by__profile')
    )
    if user is not None:
        qs = qs.filter(user=user)
    if status:
        qs = qs.filter(status=status)
    if date_from:
        start = timezone.make_aware(datetime.combine(date_from, datetime.min.time()))
        qs = qs.filter(clock_in__gte=start)
    if date_to:
        end = timezone.make_aware(datetime.combine(date_to, datetime.max.time()))
        qs = qs.filter(clock_in__lte=end)
    return qs.order_by('-clock_in')


def get_open_entry(user: User, organization: Organization) -> Optional[TimeEntry]:
    return (
        TimeEntry.objects
        .filter(
            organization=organization,
            user=user,
            status=TimeEntry.STATUS_OPEN,
        )
        .select_related('user', 'user__profile')
        .first()
    )


def get_org_time_entry(user: User, organization: Organization, entry_id: int) -> TimeEntry:
    from django.shortcuts import get_object_or_404
    return get_object_or_404(
        TimeEntry,
        pk=entry_id,
        organization=organization,
    )


def week_start_for_date(value: date) -> date:
    """Monday as the first day of the week."""
    return value - timedelta(days=value.weekday())


def entry_duration_hours(entry: TimeEntry, *, now: Optional[datetime] = None) -> float:
    if not entry.clock_in:
        return 0.0
    end = entry.clock_out or now or timezone.now()
    if end < entry.clock_in:
        return 0.0
    total_minutes = (end - entry.clock_in).total_seconds() / 60
    total_minutes = max(0, total_minutes - entry.break_minutes)
    return round(total_minutes / 60, 2)


def format_hours(hours: float) -> str:
    if hours <= 0:
        return '0h'
    whole_hours = int(hours)
    minutes = int(round((hours - whole_hours) * 60))
    if minutes == 60:
        whole_hours += 1
        minutes = 0
    if minutes:
        return f'{whole_hours}h {minutes}m'
    return f'{whole_hours}h'


def _countable_entries_qs(
    organization: Organization,
    user: User,
    date_from: date,
    date_to: date,
) -> QuerySet:
    start = timezone.make_aware(datetime.combine(date_from, datetime.min.time()))
    end = timezone.make_aware(datetime.combine(date_to, datetime.max.time()))
    return entries_for_organization(
        organization,
        date_from=date_from,
        date_to=date_to,
        user=user,
    ).filter(status__in=COUNTABLE_STATUSES, clock_in__gte=start, clock_in__lte=end)


def weekly_hours(
    user: User,
    organization: Organization,
    week_start: Optional[date] = None,
    *,
    now: Optional[datetime] = None,
) -> float:
    if week_start is None:
        week_start = week_start_for_date(timezone.localdate())
    week_end = week_start + timedelta(days=6)
    total = 0.0
    for entry in _countable_entries_qs(organization, user, week_start, week_end):
        total += entry_duration_hours(entry, now=now)
    return round(total, 2)


def today_hours(
    user: User,
    organization: Organization,
    *,
    now: Optional[datetime] = None,
) -> float:
    today = timezone.localdate()
    total = 0.0
    for entry in _countable_entries_qs(organization, user, today, today):
        total += entry_duration_hours(entry, now=now)
    return round(total, 2)


@dataclass(frozen=True)
class DailySummary:
    date: date
    clocked_in_count: int
    pending_count: int
    approved_count: int
    total_entries: int


def daily_summary(organization: Organization, summary_date: date) -> DailySummary:
    start = timezone.make_aware(datetime.combine(summary_date, datetime.min.time()))
    end = timezone.make_aware(datetime.combine(summary_date, datetime.max.time()))
    qs = TimeEntry.objects.filter(organization=organization, clock_in__gte=start, clock_in__lte=end)
    counts = qs.aggregate(
        clocked_in_count=Count('id', filter=Q(status=TimeEntry.STATUS_OPEN)),
        pending_count=Count('id', filter=Q(status=TimeEntry.STATUS_PENDING)),
        approved_count=Count('id', filter=Q(status=TimeEntry.STATUS_APPROVED)),
        total_entries=Count('id'),
    )
    return DailySummary(date=summary_date, **counts)


def elapsed_seconds(entry: TimeEntry, *, now: Optional[datetime] = None) -> int:
    current = now or timezone.now()
    return max(0, int((current - entry.clock_in).total_seconds()))


def status_payload(user: User, organization: Organization) -> dict:
    open_entry = get_open_entry(user, organization)
    today = timezone.localdate()
    week_start = week_start_for_date(today)
    payload = {
        'clocked_in': open_entry is not None,
        'today_hours': today_hours(user, organization),
        'today_hours_display': format_hours(today_hours(user, organization)),
        'week_hours': weekly_hours(user, organization, week_start),
        'week_hours_display': format_hours(weekly_hours(user, organization, week_start)),
    }
    if open_entry:
        payload.update({
            'entry_id': open_entry.pk,
            'clock_in': open_entry.clock_in.isoformat(),
            'clock_in_display': timezone.localtime(open_entry.clock_in).strftime('%I:%M %p'),
            'elapsed_seconds': elapsed_seconds(open_entry),
        })
    return payload
