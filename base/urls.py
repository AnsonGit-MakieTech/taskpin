from django.urls import path
from . import views

urlpatterns = [
    path('', views.team_board, name='team_board'),
    path('task/<int:task_id>/done/', views.mark_done, name='mark_done'),
]
