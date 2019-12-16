from django.urls import path

from . import views

urlpatterns = [


    path('period/list/', views.PeriodList.as_view()),
    path('category/list/', views.CategoryList.as_view()),
    path('task/list/', views.TaskList.as_view()),
    path('task/postpone/', views.TaskPostpone.as_view()),
    path('task/increment/', views.TaskIncrement.as_view()),
    path('task/changelog/', views.TaskChangelog.as_view()),
    path('task/detail/<int:task_id>/', views.TaskDetail.as_view()),

]
