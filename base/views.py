from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Case, When, IntegerField

from .models import Task, ActivityLog


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

    return render(request, 'board/team_board.html', {
        'board': board,
        'unassigned_tasks': unassigned_tasks,
    })


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
    return redirect('team_board')
