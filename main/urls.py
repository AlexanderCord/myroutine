from django.urls import path, include

from django.conf import settings


from . import views

urlpatterns = [


    path('', views.index, name='index'),

    path('task/<int:task_id>/', views.task, name = 'task'),

    path('task/<int:task_id>/done', views.task_done, name = 'task_done'),
    
    path('task/<int:task_id>/postpone/<int:delay_shift>', views.task_postpone, name = 'task_postpone'),
    
    path('task/<int:task_id>/archive/', views.task_archive, name = 'task_archive'),

    path('task/<int:task_id>/start', views.task_start, name = 'task_start'),
    
    path('task/edit/<int:task_id>', views.task_edit, name='task_edit'),

    path('task/add', views.task_add, name = 'task_add'),
    
    path('authorize', views.authorize, name = 'authorize'),    

    path('ajax/task/done', views.ajax_task_done, name = 'ajax_task_done'),
    
    path('ajax/task/start', views.ajax_task_start, name = 'ajax_task_start'),
    
    path('ajax/task/postpone', views.ajax_task_postpone, name = 'ajax_task_postpone'),
    
    path('ajax/task/history', views.ajax_task_history, name = 'ajax_task_history'),
    
    path('ajax/task/archive', views.ajax_task_archive, name = 'ajax_task_archive'),
    
    path('ajax/task/dates_done', views.ajax_task_dates_done, name = 'ajax_task_days_done'),

    path('ajax/category/remove', views.ajax_category_remove, name = 'ajax_category_remove'),
    
    path('archive', views.archive, name='archive'),
    
    path('archive/<int:task_id>', views.archive_detail, name='archive_detail'),
    
    path('category', views.category, name = 'category'),
    
    path('category/add', views.category_add, name = 'category_add'),
    
    path('category/edit/<int:category_id>', views.category_edit, name='category_edit'), 

    path('category/remove/<int:category_id>', views.category_remove, name = 'category_remove'),
    

    path('', include('social_django.urls', namespace='social')),
    
    path('signout/', views.signout,  name='signout'),


]
