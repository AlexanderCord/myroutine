from django.urls import path

from . import views

urlpatterns = [


    path('', views.index, name='index'),

    path('task/<int:task_id>/', views.task, name = 'task'),

    path('task/<int:task_id>/done', views.task_done, name = 'task_done'),
    
    path('task/<int:task_id>/postpone/<int:delay_shift>', views.task_postpone, name = 'task_postpone'),

    path('task/<int:task_id>/start', views.task_start, name = 'task_start'),
    
    path('authorize', views.authorize, name = 'authorize'),    
]
