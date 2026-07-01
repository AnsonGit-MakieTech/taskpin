from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Case, When, IntegerField, Count, Q
from django.http import HttpResponseForbidden
from functools import wraps

from .models import Task, ActivityLog, UserProfile
from .forms import TaskCreateForm, InviteMemberForm, RegisterForm
from .realtime import notify_board_update


def is_admin(user):
    if user.is_superuser:
        return True
    profile = getattr(user, 'profile', None)
    return profile is not None and profile.role == 'admin'


def admin_required(view_func):
    @wraps(view_func)
    @login_required
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


@login_required
def team_board(request):
    users = (
        User.objects
        .filter(is_active=True)
        .select_related('profile')
        .order_by('first_name', 'username')
    )

    unassigned_tasks = list(
        Task.objects
        .filter(status=Task.STATUS_UNASSIGNED, assigned_to__isnull=True)
        .annotate(priority_order=PRIORITY_ORDER)
        .order_by('priority_order', 'due_date')
    )

    board = []
    for user in users:
        tasks = list(
            Task.objects
            .filter(assigned_to=user, status=Task.STATUS_ASSIGNED)
            .annotate(priority_order=PRIORITY_ORDER)
            .order_by('priority_order', 'due_date')
        )
        board.append({'user': user, 'tasks': tasks})

    all_users = list(users)
    return render(request, 'board/team_board.html', {
        'board': board,
        'unassigned_tasks': unassigned_tasks,
        'all_users': all_users,
    })


@login_required
def task_create(request):
    form = TaskCreateForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        task = form.save(commit=False)
        task.created_by = request.user
        assigned_to = form.cleaned_data.get('assign_to')
        if assigned_to:
            task.assigned_to = assigned_to
            task.status = Task.STATUS_ASSIGNED
        else:
            task.status = Task.STATUS_UNASSIGNED
        task.save()
        ActivityLog.objects.create(
            actor=request.user,
            action=f'Created task "{task.title}"'
            + (f' and assigned to {assigned_to.get_full_name() or assigned_to.username}' if assigned_to else ''),
            task=task,
        )
        notify_board_update('task.created', task.id, request.user.id, {
            'assigned_to_id': task.assigned_to_id,
        })
        return redirect('team_board')

    users = (
        User.objects
        .filter(is_active=True)
        .select_related('profile')
        .order_by('first_name', 'username')
    )
    return render(request, 'board/task_form.html', {'form': form, 'users': users})


@login_required
def my_board(request):
    base_qs = (
        Task.objects
        .filter(assigned_to=request.user, status=Task.STATUS_ASSIGNED)
        .order_by('due_date', 'created_at')
    )
    urgent    = list(base_qs.filter(priority=Task.PRIORITY_URGENT))
    important = list(base_qs.filter(priority=Task.PRIORITY_IMPORTANT))
    normal    = list(base_qs.filter(priority=Task.PRIORITY_NORMAL))
    all_tasks = urgent + important + normal
    groups = [
        {'label': 'Urgent',    'key': 'urgent',    'tasks': urgent},
        {'label': 'Important', 'key': 'important', 'tasks': important},
        {'label': 'Normal',    'key': 'normal',    'tasks': normal},
    ]
    all_users = list(
        User.objects.filter(is_active=True).select_related('profile').order_by('first_name', 'username')
    )
    return render(request, 'board/my_board.html', {
        'groups': groups,
        'task_count': len(all_tasks),
        'all_users': all_users,
    })


@login_required
def done_tasks(request):
    tasks = list(
        Task.objects
        .filter(status=Task.STATUS_DONE)
        .select_related('created_by', 'assigned_to', 'created_by__profile', 'assigned_to__profile')
        .order_by('-completed_at')
    )
    return render(request, 'board/done_tasks.html', {'tasks': tasks})


@login_required
def mark_done(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    if request.method == 'POST':
        task.status = Task.STATUS_DONE
        task.completed_at = timezone.now()
        task.save()
        ActivityLog.objects.create(
            actor=request.user,
            action=f'Marked "{task.title}" as done',
            task=task,
        )
        notify_board_update('task.done', task.id, request.user.id, {
            'assigned_to_id': task.assigned_to_id,
        })
    return redirect('team_board')


@login_required
def task_reassign(request, task_id):
    if not is_admin(request.user):
        return HttpResponseForbidden('Only admins can move tasks.')
    task = get_object_or_404(Task, pk=task_id)
    if request.method == 'POST':
        new_user_id = request.POST.get('assigned_to')
        if new_user_id:
            new_user = get_object_or_404(User, pk=new_user_id)
            old_assignee = task.assigned_to
            task.assigned_to = new_user
            task.status = Task.STATUS_ASSIGNED
            task.save()
            old_name = old_assignee.get_full_name() or old_assignee.username if old_assignee else 'Unassigned'
            new_name = new_user.get_full_name() or new_user.username
            ActivityLog.objects.create(
                actor=request.user,
                action=f'Moved "{task.title}" from {old_name} to {new_name}',
                task=task,
            )
            notify_board_update('task.moved', task.id, request.user.id, {
                'assigned_to_id': task.assigned_to_id,
            })
        else:
            task.assigned_to = None
            task.status = Task.STATUS_UNASSIGNED
            task.save()
            ActivityLog.objects.create(
                actor=request.user,
                action=f'Unassigned "{task.title}"',
                task=task,
            )
            notify_board_update('task.moved', task.id, request.user.id, {
                'assigned_to_id': None,
            })
    return redirect('team_board')


@login_required
def task_edit(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    form = TaskCreateForm(request.POST or None, instance=task)

    if request.method == 'POST' and form.is_valid():
        task = form.save(commit=False)
        assigned_to = form.cleaned_data.get('assign_to')
        if assigned_to:
            task.assigned_to = assigned_to
            task.status = Task.STATUS_ASSIGNED
        else:
            task.assigned_to = None
            task.status = Task.STATUS_UNASSIGNED
        task.save()
        ActivityLog.objects.create(
            actor=request.user,
            action=f'Edited task "{task.title}"',
            task=task,
        )
        notify_board_update('task.edited', task.id, request.user.id, {
            'assigned_to_id': task.assigned_to_id,
        })
        return redirect('team_board')

    users = (
        User.objects
        .filter(is_active=True)
        .select_related('profile')
        .order_by('first_name', 'username')
    )
    # Pre-select the current assignee in the form
    if task.assigned_to and not form.is_bound:
        form.initial['assign_to'] = task.assigned_to.pk

    return render(request, 'board/task_form.html', {
        'form': form,
        'users': users,
        'task': task,
    })


@login_required
def task_delete(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    if request.method == 'POST':
        title = task.title
        task_id = task.id
        assigned_to_id = task.assigned_to_id
        ActivityLog.objects.create(
            actor=request.user,
            action=f'Deleted task "{title}"',
            task=task,
        )
        task.delete()
        notify_board_update('task.deleted', task_id, request.user.id, {
            'assigned_to_id': assigned_to_id,
        })
    return redirect('team_board')


ACTIVITY_LOG_LIMIT = 50


@login_required
def activity_log(request):
    entries = (
        ActivityLog.objects
        .select_related('actor', 'actor__profile', 'task')
        .order_by('-timestamp')[:ACTIVITY_LOG_LIMIT]
    )
    return render(request, 'activity/activity_log.html', {
        'entries': entries,
        'entry_count': len(entries),
    })


@login_required
def team_list(request):
    members = (
        User.objects
        .filter(is_active=True)
        .select_related('profile')
        .annotate(
            active_task_count=Count(
                'assigned_tasks',
                filter=Q(assigned_tasks__status=Task.STATUS_ASSIGNED),
            )
        )
        .order_by('first_name', 'username')
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
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.role = form.cleaned_data['role']
        profile.save()
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
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.role = 'admin'
        profile.save()
        login(request, user)
        return redirect('team_board')

    return render(request, 'registration/register.html', {'form': form})
