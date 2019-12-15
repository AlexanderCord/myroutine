from django.urls import path

from . import views

urlpatterns = [


    path('list/', views.TaskList.as_view()),

    path('detail/<int:task_id>/', views.TaskDetail.as_view()),

    path('detail/', views.TaskDetail.as_view())    ,
]
