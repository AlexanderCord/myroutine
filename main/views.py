from django.http import HttpResponse,Http404
from django.template import loader
from rest_framework import generics
from .serializers import *
from .models import *
from datetime import datetime  
from datetime import timedelta

"""
Backend API methods
"""


class TaskPostpone(generics.ListAPIView):

    serializer_class = ScheduleSerializer
    def get_queryset(self):    
        task_id = self.request.query_params.get('task_id', None)
        if task_id is not None:
            try:
                qs = Schedule.objects.get(task_id=task_id)
                qs.next_date = qs.next_date + timedelta(days=7) 
                qs.save()
            except Schedule.DoesNotExist:
                raise Http404("Next task date does not exist")
            
            print(str(qs))

        else:
            raise Http404("Task_id parameter should be set")
        queryset = Schedule.objects.filter(task_id=task_id).all()

        print(str(queryset.query))
        return queryset



class TaskIncrement(generics.GenericAPIView):
    def get_object(self):
        raise Http404

class TaskChangelog(generics.GenericAPIView):
    def get_object(self):
        raise Http404


class PeriodList(generics.ListAPIView):
    queryset = Period.objects.all()
    serializer_class = PeriodSerializer


class CategoryList(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class TaskList(generics.ListAPIView):
    serializer_class = TaskSerializer
    def get_queryset(self):    
        queryset = Task.objects.select_related('period', 'category_id', 'user_id').filter(active=True)
        category = self.request.query_params.get('category', None)
        if category is not None:
            queryset = queryset.filter(category_id = category)
        queryset = queryset.all()
        print(str(queryset.query))
        return queryset
    

class TaskDetail(generics.RetrieveAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer


"""
Regular UI
"""

def index(request):
    task_list = Task.objects.filter(active=True).order_by('-id')[:5]
    template = loader.get_template('main/index.html')
    context = {
        'task_list': task_list,
    }
    return HttpResponse(template.render(context, request))


def task(request, task_id):
    # task_list = Task.objects.order_by('-id')[:5]
    template = loader.get_template('main/task.html')
    context = {
        'task_id': task_id,
    }
    return HttpResponse(template.render(context, request))




