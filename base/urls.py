from django.urls import path
from . import views

urlpatterns = [
    path('', views.team_board, name='team_board'),
    path('my/', views.my_board, name='my_board'),
    path('done/', views.done_tasks, name='done_tasks'),
    path('task/create/', views.task_create, name='task_create'),
    path('task/<int:task_id>/done/', views.mark_done, name='mark_done'),
    path('task/<int:task_id>/reassign/', views.task_reassign, name='task_reassign'),
    path('task/<int:task_id>/edit/', views.task_edit, name='task_edit'),
    path('task/<int:task_id>/delete/', views.task_delete, name='task_delete'),
]
