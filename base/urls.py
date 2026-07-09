from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.team_board, name='team_board'),
    path('my/', views.my_board, name='my_board'),
    path('done/', views.done_tasks, name='done_tasks'),
    path('activity/', views.activity_log, name='activity_log'),
    path('settings/', views.user_settings, name='user_settings'),
    path(
        'settings/password/',
        auth_views.PasswordChangeView.as_view(
            template_name='settings/password_change.html',
            success_url=reverse_lazy('password_change_done'),
        ),
        name='password_change',
    ),
    path(
        'settings/password/done/',
        auth_views.PasswordChangeDoneView.as_view(
            template_name='settings/password_change_done.html',
        ),
        name='password_change_done',
    ),
    path('task/create/', views.task_create, name='task_create'),
    path('task/<int:task_id>/done/', views.mark_done, name='mark_done'),
    path('task/<int:task_id>/reassign/', views.task_reassign, name='task_reassign'),
    path('task/<int:task_id>/edit/', views.task_edit, name='task_edit'),
    path('task/<int:task_id>/delete/', views.task_delete, name='task_delete'),
    path('task/<int:task_id>/card/', views.task_card_fragment, name='task_card_fragment'),
    path('task/<int:task_id>/done-row/', views.task_done_row_fragment, name='task_done_row_fragment'),
    path('api/my/deadline-reminders/', views.deadline_reminders, name='deadline_reminders'),
    path('team/', views.team_list, name='team_list'),
    path('team/invite/', views.invite_member, name='invite_member'),
]
