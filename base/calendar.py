"""Calendar view helpers — month grid and task grouping by due date."""

from __future__ import annotations

from calendar import monthrange
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Optional

from django.contrib.auth.models import User
from django.db.models import Q, QuerySet
from django.utils import timezone

from .models import Organization, Task
from .organizations import tasks_for_organization

# Python weekday(): Monday=0 … Sunday=6
WEEK_START_SUNDAY = 6
WEEK_START_MONDAY = 0
DEFAULT_WEEK_START = WEEK_START_SUNDAY

VIEW_MONTH = 'month'
VIEW_WEEK = 'week'
VIEW_CHOICES = (VIEW_MONTH, VIEW_WEEK)

SCOPE_MY = 'my'
SCOPE_TEAM = 'team'
SCOPE_CHOICES = (SCOPE_MY, SCOPE_TEAM)

PRIORITY_FILTER_ALL = 'all'
PRIORITY_FILTER_URGENT = 'urgent'
PRIORITY_FILTER_IMPORTANT = 'important'
PRIORITY_FILTER_NORMAL = 'normal'
PRIORITY_FILTER_CHOICES = (
    PRIORITY_FILTER_ALL,
    PRIORITY_FILTER_URGENT,
    PRIORITY_FILTER_IMPORTANT,
    PRIORITY_FILTER_NORMAL,
)


@dataclass(frozen=True)
class CalendarViewParams:
    view: str
    week_start: int
    anchor_date: date
    year: int
    month: int

    @property
    def week_start_key(self) -> str:
        return 'mon' if self.week_start == WEEK_START_MONDAY else 'sun'


@dataclass(frozen=True)
class CalendarWeekNav:
    prev_date: date
    next_date: date
    label: str


@dataclass(frozen=True)
class CalendarMonth:
    year: int
    month: int
    month_start: date
    month_end: date
    grid_start: date
    grid_end: date


@dataclass(frozen=True)
class CalendarDay:
    day: date
    in_current_month: bool
    is_today: bool


@dataclass(frozen=True)
class CalendarDayCell:
    day: CalendarDay
    tasks: list[CalendarTaskItem]


@dataclass(frozen=True)
class CalendarTaskItem:
    task: Task
    calendar_date: date
    date_source: str
    priority: str
    urgency: str
    is_done: bool


@dataclass(frozen=True)
class CalendarFilters:
    scope: str = SCOPE_TEAM
    assignee_id: Optional[int] = None
    priority: str = PRIORITY_FILTER_ALL
    include_done: bool = False
    show_completed_on: bool = False

    def as_template_dict(self) -> dict[str, str]:
        return {
            'scope': self.scope,
            'assignee': str(self.assignee_id) if self.assignee_id else '',
            'priority': self.priority,
            'include_done': '1' if self.include_done else '',
            'show_completed_on': '1' if self.show_completed_on else '',
        }


@dataclass(frozen=True)
class CalendarSummary:
    due_today: int
    overdue: int
    due_this_week: int
    unscheduled: int


@dataclass
class CalendarData:
    month: CalendarMonth
    weeks: list[list[CalendarDay]]
    tasks_by_date: dict[date, list[CalendarTaskItem]]
    unscheduled: list[Task]
    summary: CalendarSummary


def parse_week_start(value: str, *, default: Optional[int] = None) -> int:
    default = DEFAULT_WEEK_START if default is None else default
    if value == 'mon':
        return WEEK_START_MONDAY
    if value == 'sun':
        return WEEK_START_SUNDAY
    return default


def locale_default_week_start() -> int:
    """Match Python locale calendar first weekday (0=Mon, 6=Sun)."""
    import calendar as cal_module
    first = cal_module.firstweekday()
    return WEEK_START_MONDAY if first == cal_module.MONDAY else WEEK_START_SUNDAY


def weekday_labels(week_start: int) -> tuple[str, ...]:
    mon_first = ('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun')
    if week_start == WEEK_START_SUNDAY:
        return ('Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat')
    return mon_first


def parse_calendar_view_params(request, *, today: Optional[date] = None) -> CalendarViewParams:
    today = today or timezone.localdate()
    view = request.GET.get('view', VIEW_MONTH).strip() or VIEW_MONTH
    if view not in VIEW_CHOICES:
        view = VIEW_MONTH

    week_start_raw = request.GET.get('week_start', '').strip()
    week_start = (
        parse_week_start(week_start_raw)
        if week_start_raw
        else locale_default_week_start()
    )

    from .filters import parse_date as parse_filter_date
    date_raw = request.GET.get('date', '').strip()
    anchor = parse_filter_date(date_raw) or today

    year_raw = request.GET.get('year', '').strip()
    month_raw = request.GET.get('month', '').strip()
    year = int(year_raw) if year_raw.isdigit() else today.year
    month = int(month_raw) if month_raw.isdigit() else today.month

    if view == VIEW_WEEK:
        year = anchor.year
        month = anchor.month

    return CalendarViewParams(
        view=view,
        week_start=week_start,
        anchor_date=anchor,
        year=year,
        month=month,
    )


def clamp_month(year: int, month: int) -> tuple[int, int]:
    if month < 1:
        return year - 1, 12
    if month > 12:
        return year + 1, 1
    return year, month


def parse_calendar_month(
    year: Optional[int],
    month: Optional[int],
    *,
    today: Optional[date] = None,
    week_start: int = DEFAULT_WEEK_START,
) -> CalendarMonth:
    today = today or timezone.localdate()
    year = year if year is not None else today.year
    month = month if month is not None else today.month
    year = max(1970, min(2100, int(year)))
    month = max(1, min(12, int(month)))
    return get_calendar_month(year, month, today=today, week_start=week_start)


def get_calendar_month(
    year: int,
    month: int,
    *,
    today: Optional[date] = None,
    week_start: int = DEFAULT_WEEK_START,
) -> CalendarMonth:
    today = today or timezone.localdate()
    month_start = date(year, month, 1)
    month_end = date(year, month, monthrange(year, month)[1])
    grid_start = month_start - timedelta(days=_days_since_week_start(month_start, week_start))
    grid_end = month_end + timedelta(days=_days_until_week_end(month_end, week_start))
    return CalendarMonth(
        year=year,
        month=month,
        month_start=month_start,
        month_end=month_end,
        grid_start=grid_start,
        grid_end=grid_end,
    )


def get_calendar_week(
    anchor: date,
    *,
    today: Optional[date] = None,
    week_start: int = DEFAULT_WEEK_START,
) -> tuple[date, date]:
    """Return (week_start_date, week_end_date) for the week containing anchor."""
    today = today or timezone.localdate()
    week_start_date = anchor - timedelta(days=_days_since_week_start(anchor, week_start))
    week_end_date = week_start_date + timedelta(days=6)
    return week_start_date, week_end_date


def _days_since_week_start(day: date, week_start: int = DEFAULT_WEEK_START) -> int:
    return (day.weekday() - week_start) % 7


def _days_until_week_end(day: date, week_start: int = DEFAULT_WEEK_START) -> int:
    return (week_start - day.weekday()) % 7


def local_day_start(day: date) -> datetime:
    return timezone.make_aware(datetime.combine(day, datetime.min.time()))


def local_day_end(day: date) -> datetime:
    return timezone.make_aware(datetime.combine(day, datetime.max.time()))


def build_month_grid(
    calendar_month: CalendarMonth,
    *,
    today: Optional[date] = None,
    week_start: int = DEFAULT_WEEK_START,
) -> list[list[CalendarDay]]:
    today = today or timezone.localdate()
    weeks: list[list[CalendarDay]] = []
    cursor = calendar_month.grid_start
    while cursor <= calendar_month.grid_end:
        week: list[CalendarDay] = []
        for _ in range(7):
            week.append(
                CalendarDay(
                    day=cursor,
                    in_current_month=(
                        cursor.month == calendar_month.month
                        and cursor.year == calendar_month.year
                    ),
                    is_today=cursor == today,
                ),
            )
            cursor += timedelta(days=1)
        weeks.append(week)
    return weeks


def build_week_grid(
    anchor: date,
    *,
    today: Optional[date] = None,
    week_start: int = DEFAULT_WEEK_START,
) -> list[list[CalendarDay]]:
    """Single-week grid row for week view."""
    today = today or timezone.localdate()
    week_start_date, _ = get_calendar_week(anchor, today=today, week_start=week_start)
    week: list[CalendarDay] = []
    cursor = week_start_date
    for _ in range(7):
        week.append(
            CalendarDay(
                day=cursor,
                in_current_month=True,
                is_today=cursor == today,
            ),
        )
        cursor += timedelta(days=1)
    return [week]


def priority_filter_q(priority_filter: str) -> Q:
    if priority_filter == PRIORITY_FILTER_URGENT:
        return Q(priority=Task.PRIORITY_URGENT)
    if priority_filter == PRIORITY_FILTER_IMPORTANT:
        return Q(priority=Task.PRIORITY_IMPORTANT)
    if priority_filter == PRIORITY_FILTER_NORMAL:
        return Q(priority=Task.PRIORITY_NORMAL)
    return Q()


def parse_calendar_filters(request) -> CalendarFilters:
    scope = request.GET.get('scope', SCOPE_TEAM).strip() or SCOPE_TEAM
    if scope not in SCOPE_CHOICES:
        scope = SCOPE_TEAM

    assignee_raw = request.GET.get('assignee', '').strip()
    assignee_id = int(assignee_raw) if assignee_raw.isdigit() else None

    priority = request.GET.get('priority', PRIORITY_FILTER_ALL).strip() or PRIORITY_FILTER_ALL
    if priority not in PRIORITY_FILTER_CHOICES:
        priority = PRIORITY_FILTER_ALL

    return CalendarFilters(
        scope=scope,
        assignee_id=assignee_id,
        priority=priority,
        include_done=request.GET.get('include_done') == '1',
        show_completed_on=request.GET.get('show_completed_on') == '1',
    )


def _scoped_tasks(
    organization: Organization,
    filters: CalendarFilters,
    user: User,
) -> QuerySet:
    qs = tasks_for_organization(organization).select_related(
        'assigned_to',
        'assigned_to__profile',
        'created_by',
    )
    if filters.scope == SCOPE_MY:
        qs = qs.filter(assigned_to=user)
    elif filters.assignee_id:
        qs = qs.filter(assigned_to_id=filters.assignee_id)
    return qs.filter(priority_filter_q(filters.priority))


def _active_status_q() -> Q:
    return Q(status__in=[Task.STATUS_UNASSIGNED, Task.STATUS_ASSIGNED])


def _calendar_task_item(task: Task, calendar_date: date, date_source: str) -> CalendarTaskItem:
    return CalendarTaskItem(
        task=task,
        calendar_date=calendar_date,
        date_source=date_source,
        priority=task.priority,
        urgency=task.deadline_urgency,
        is_done=task.is_done,
    )


def _group_due_date_tasks(
    tasks: list[Task],
    *,
    include_done: bool,
) -> dict[date, list[CalendarTaskItem]]:
    grouped: dict[date, list[CalendarTaskItem]] = defaultdict(list)
    for task in tasks:
        if not task.due_date:
            continue
        if task.is_done and not include_done:
            continue
        if not task.is_done and task.status == Task.STATUS_DONE:
            continue
        day = timezone.localtime(task.due_date).date()
        grouped[day].append(_calendar_task_item(task, day, 'due_date'))
    return grouped


def _group_completed_tasks(
    tasks: list[Task],
) -> dict[date, list[CalendarTaskItem]]:
    grouped: dict[date, list[CalendarTaskItem]] = defaultdict(list)
    for task in tasks:
        if not task.is_done or not task.completed_at:
            continue
        day = timezone.localtime(task.completed_at).date()
        grouped[day].append(_calendar_task_item(task, day, 'completed_at'))
    return grouped


def _merge_task_groups(
    primary: dict[date, list[CalendarTaskItem]],
    secondary: dict[date, list[CalendarTaskItem]],
) -> dict[date, list[CalendarTaskItem]]:
    merged: dict[date, list[CalendarTaskItem]] = defaultdict(list)
    seen: dict[date, set[int]] = defaultdict(set)

    for day, items in primary.items():
        for item in items:
            merged[day].append(item)
            seen[day].add(item.task.pk)

    for day, items in secondary.items():
        for item in items:
            if item.task.pk in seen[day]:
                continue
            merged[day].append(item)
            seen[day].add(item.task.pk)

    for day in merged:
        merged[day].sort(
            key=lambda item: (
                item.is_done,
                item.task.due_date or item.task.completed_at or timezone.now(),
            ),
        )
    return dict(merged)


def fetch_unscheduled_tasks(
    organization: Organization,
    filters: CalendarFilters,
    user: User,
) -> list[Task]:
    qs = (
        _scoped_tasks(organization, filters, user)
        .filter(due_date__isnull=True)
        .filter(_active_status_q())
        .order_by('-priority', 'created_at')
    )
    return list(qs)


def fetch_calendar_tasks_for_range(
    organization: Organization,
    range_start: date,
    range_end: date,
    filters: CalendarFilters,
    user: User,
) -> tuple[dict[date, list[CalendarTaskItem]], list[Task]]:
    base_qs = _scoped_tasks(organization, filters, user)
    range_filter = Q(
        due_date__gte=local_day_start(range_start),
        due_date__lte=local_day_end(range_end),
        due_date__isnull=False,
    )

    due_qs = base_qs.filter(range_filter)
    if filters.include_done:
        due_qs = due_qs.filter(Q(_active_status_q()) | Q(status=Task.STATUS_DONE))
    else:
        due_qs = due_qs.filter(_active_status_q())

    tasks_by_date = _group_due_date_tasks(list(due_qs), include_done=filters.include_done)

    if filters.show_completed_on:
        completed_qs = base_qs.filter(
            status=Task.STATUS_DONE,
            completed_at__gte=local_day_start(range_start),
            completed_at__lte=local_day_end(range_end),
        )
        tasks_by_date = _merge_task_groups(tasks_by_date, _group_completed_tasks(list(completed_qs)))

    unscheduled = fetch_unscheduled_tasks(organization, filters, user)
    return tasks_by_date, unscheduled


def build_calendar_summary(
    organization: Organization,
    filters: CalendarFilters,
    user: User,
    *,
    today: Optional[date] = None,
    unscheduled_count: Optional[int] = None,
    week_start: int = DEFAULT_WEEK_START,
) -> CalendarSummary:
    today = today or timezone.localdate()
    week_start_date, week_end_date = get_calendar_week(today, today=today, week_start=week_start)
    now = timezone.now()

    qs = _scoped_tasks(organization, filters, user).filter(_active_status_q(), due_date__isnull=False)

    due_today = qs.filter(
        due_date__gte=local_day_start(today),
        due_date__lte=local_day_end(today),
    ).count()

    overdue = qs.filter(due_date__lt=now).count()

    due_this_week = qs.filter(
        due_date__gte=local_day_start(week_start_date),
        due_date__lte=local_day_end(week_end_date),
    ).count()

    if unscheduled_count is None:
        unscheduled_count = len(fetch_unscheduled_tasks(organization, filters, user))

    return CalendarSummary(
        due_today=due_today,
        overdue=overdue,
        due_this_week=due_this_week,
        unscheduled=unscheduled_count,
    )


def build_calendar_data(
    organization: Organization,
    year: int,
    month: int,
    filters: CalendarFilters,
    user: User,
    *,
    today: Optional[date] = None,
    week_start: int = DEFAULT_WEEK_START,
) -> CalendarData:
    today = today or timezone.localdate()
    calendar_month = get_calendar_month(year, month, today=today, week_start=week_start)
    weeks = build_month_grid(calendar_month, today=today, week_start=week_start)
    tasks_by_date, unscheduled = fetch_calendar_tasks_for_range(
        organization,
        calendar_month.grid_start,
        calendar_month.grid_end,
        filters,
        user,
    )
    summary = build_calendar_summary(
        organization,
        filters,
        user,
        today=today,
        unscheduled_count=len(unscheduled),
        week_start=week_start,
    )
    return CalendarData(
        month=calendar_month,
        weeks=weeks,
        tasks_by_date=tasks_by_date,
        unscheduled=unscheduled,
        summary=summary,
    )


def build_week_calendar_data(
    organization: Organization,
    anchor: date,
    filters: CalendarFilters,
    user: User,
    *,
    today: Optional[date] = None,
    week_start: int = DEFAULT_WEEK_START,
) -> CalendarData:
    today = today or timezone.localdate()
    week_start_date, week_end_date = get_calendar_week(anchor, today=today, week_start=week_start)
    calendar_month = get_calendar_month(anchor.year, anchor.month, today=today, week_start=week_start)
    weeks = build_week_grid(anchor, today=today, week_start=week_start)
    tasks_by_date, unscheduled = fetch_calendar_tasks_for_range(
        organization,
        week_start_date,
        week_end_date,
        filters,
        user,
    )
    summary = build_calendar_summary(
        organization,
        filters,
        user,
        today=today,
        unscheduled_count=len(unscheduled),
        week_start=week_start,
    )
    return CalendarData(
        month=calendar_month,
        weeks=weeks,
        tasks_by_date=tasks_by_date,
        unscheduled=unscheduled,
        summary=summary,
    )


@dataclass(frozen=True)
class CalendarMonthNav:
    prev_year: int
    prev_month: int
    next_year: int
    next_month: int
    label: str


def get_calendar_week_nav(anchor: date, week_start: int = DEFAULT_WEEK_START) -> CalendarWeekNav:
    week_start_date, week_end_date = get_calendar_week(anchor, week_start=week_start)
    prev_date = week_start_date - timedelta(days=7)
    next_date = week_start_date + timedelta(days=7)
    if week_start_date.year == week_end_date.year:
        label = f"{week_start_date.strftime('%b %d')} – {week_end_date.strftime('%b %d, %Y')}"
    else:
        label = (
            f"{week_start_date.strftime('%b %d, %Y')} – {week_end_date.strftime('%b %d, %Y')}"
        )
    return CalendarWeekNav(prev_date=prev_date, next_date=next_date, label=label)


def get_calendar_month_nav(year: int, month: int) -> CalendarMonthNav:
    prev_year, prev_month = clamp_month(year, month - 1)
    next_year, next_month = clamp_month(year, month + 1)
    label = date(year, month, 1).strftime('%B %Y')
    return CalendarMonthNav(
        prev_year=prev_year,
        prev_month=prev_month,
        next_year=next_year,
        next_month=next_month,
        label=label,
    )


def build_calendar_week_rows(
    weeks: list[list[CalendarDay]],
    tasks_by_date: dict[date, list[CalendarTaskItem]],
) -> list[list[CalendarDayCell]]:
    return [
        [
            CalendarDayCell(day=day, tasks=tasks_by_date.get(day.day, []))
            for day in week
        ]
        for week in weeks
    ]


def calendar_has_visible_tasks(data: CalendarData) -> bool:
    if data.unscheduled:
        return True
    month = data.month
    for day, items in data.tasks_by_date.items():
        if month.month_start <= day <= month.month_end and items:
            return True
    return False


def build_next_7_days_agenda(
    organization: Organization,
    filters: CalendarFilters,
    user: User,
    *,
    today: Optional[date] = None,
) -> list[tuple[date, list[CalendarTaskItem]]]:
    """Tasks grouped by day for today through the next six days."""
    today = today or timezone.localdate()
    end = today + timedelta(days=6)
    tasks_by_date, _ = fetch_calendar_tasks_for_range(
        organization,
        today,
        end,
        filters,
        user,
    )
    return [
        (today + timedelta(days=offset), tasks_by_date.get(today + timedelta(days=offset), []))
        for offset in range(7)
    ]


def build_agenda_items(
    data: CalendarData,
    *,
    today: Optional[date] = None,
) -> list[tuple[date, list[CalendarTaskItem]]]:
    """Flat sorted list of (date, tasks) for mobile agenda view."""
    today = today or timezone.localdate()
    month = data.month
    items = [
        (day, tasks)
        for day, tasks in data.tasks_by_date.items()
        if month.month_start <= day <= month.month_end and tasks
    ]
    items.sort(key=lambda entry: entry[0])
    return items
