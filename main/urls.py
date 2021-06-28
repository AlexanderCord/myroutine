from django.urls import path, include

from django.conf import settings


from . import views, views_ajax, views_task, views_category

urlpatterns = [


    path('', views.index, name='index'),

    path('task/<int:task_id>/', views_task.task, name = 'task'),

    path('task/<int:task_id>/done', views_task.task_done, name = 'task_done'),
    
    path('task/<int:task_id>/postpone/<int:delay_shift>', views_task.task_postpone, name = 'task_postpone'),
    
    path('task/<int:task_id>/assign/<int:delay_shift>', views_task.task_assign, name = 'task_assign'),
    
    path('task/<int:task_id>/archive/', views_task.task_archive, name = 'task_archive'),

    path('task/<int:task_id>/start', views_task.task_start, name = 'task_start'),
    
    path('task/edit/<int:task_id>', views_task.task_edit, name='task_edit'),

    path('task/add', views_task.task_add, name = 'task_add'),
    
    path('authorize', views.authorize, name = 'authorize'),    

    path('ajax/task/done', views_ajax.ajax_task_done, name = 'ajax_task_done'),
    
    path('ajax/task/start', views_ajax.ajax_task_start, name = 'ajax_task_start'),
    
    path('ajax/task/postpone', views_ajax.ajax_task_postpone, name = 'ajax_task_postpone'),

    path('ajax/task/assign', views_ajax.ajax_task_assign, name = 'ajax_task_assign'),
    
    path('ajax/task/history', views_ajax.ajax_task_history, name = 'ajax_task_history'),
    
    path('ajax/task/archive', views_ajax.ajax_task_archive, name = 'ajax_task_archive'),
    
    path('ajax/task/dates_done', views_ajax.ajax_task_dates_done, name = 'ajax_task_days_done'),
    
    path('ajax/task/stats', views_ajax.ajax_task_stats, name = 'ajax_task_stats'),

    path('ajax/category/remove', views_ajax.ajax_category_remove, name = 'ajax_category_remove'),
    
    path('archive', views.archive, name='archive'),
    
    path('archive/<int:task_id>', views.archive_detail, name='archive_detail'),
    
    path('category', views_category.category, name = 'category'),
    
    path('category/add', views_category.category_add, name = 'category_add'),
    
    path('category/edit/<int:category_id>', views_category.category_edit, name='category_edit'), 

    path('category/remove/<int:category_id>', views_category.category_remove, name = 'category_remove'),
    
    path('notifications', views.notifications, name = 'notifications'), 

    path('stats', views.stats, name = 'stats'), 

    path('progress_log', views.progress_log, name = 'progress_log'), 
    

    path('', include('social_django.urls', namespace='social')),
    
    path('signout/', views.signout,  name='signout'),


]
