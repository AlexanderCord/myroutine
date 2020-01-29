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


# @todo refactor this postpone method to a separate model method

def _postponeTask(task_id, delay_shift):
    if delay_shift is not None:
        delay_shift = int(delay_shift)
        
    if delay_shift is None:
        print("delay shift is not set")      
        raise Http404("delay shift is not set or not equal to [1,7,30]")

    elif  delay_shift not in [1,7,30]:
        print("delay shift is not ok, %d" % delay_shift)      
        raise Http404("delay shift is not set or not equal to [1,7,30]")
            
    else:
        print("delay_shift is ok, %d" % delay_shift)        
        
    if task_id is not None:
        
        try:
            qs = Schedule.objects.get(task_id=task_id)
            qs.next_date = qs.next_date + timedelta(days=delay_shift) 
            qs.save()
        except Schedule.DoesNotExist:
            raise Http404("Next task date does not exist")
            
        print(str(qs))

    else:
        raise Http404("Task_id parameter should be set")


class TaskPostpone(generics.ListAPIView):

    serializer_class = ScheduleSerializer
    
    # @todo refactor this postpone method to a separate model method
    def get_queryset(self):    
        task_id = self.request.query_params.get('task_id', None)
        delay_shift = self.request.query_params.get('delay_shift', None)

        _postponeTask(task_id, delay_shift) 
                    
        queryset = Schedule.objects.filter(task_id=task_id).all()

        print(str(queryset.query))
        return queryset



class TaskDone(generics.GenericAPIView):
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


def task_done(request, task_id):
    return HttpResponse("Task %d marked as done, <a href='javascript:history.go(-1)'>Go back</a>" % task_id)


def task_postpone(request, task_id, delay_shift):
    _postponeTask(task_id, delay_shift)
    return HttpResponse("Task %d postponed for %d days, <a href='javascript:history.go(-1)'>Go back</a>" % (task_id, delay_shift))

def task(request, task_id):

    # task_list = Task.objects.order_by('-id')[:5]
    template = loader.get_template('main/task.html')
    task_row = Task.objects.get(pk=task_id)
    context = {
        'task_id': task_id,
        'task' : task_row
    }
    return HttpResponse(template.render(context, request))




