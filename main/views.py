from django.http import HttpResponse,Http404, JsonResponse
from django.shortcuts import HttpResponseRedirect

from django.template import loader
from rest_framework import generics
from .serializers import *
from .models import *
from datetime import datetime  
from datetime import timedelta

from django.contrib.auth import logout

from .static import *

"""
Google OAuth logout
"""
def signout(request):
    logout(request)
    return HttpResponseRedirect('/')


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
            task = Task.objects.get(pk = task_id)

            print("saving changelog".encode('utf-8'))
            qs2 = Changelog.objects.create(task_id = task, action = TASK_LOG_POSTPONE)
            qs2.save()

        except Schedule.DoesNotExist:
            raise Http404("Next task date does not exist")

        except DatabaseError as e:
            print(str(e))
            
            raise Http404("Error during save")
            
        print(str(qs).encode("utf-8"))
        print(str(qs2).encode("utf-8"))

    else:
        raise Http404("Task_id parameter should be set")



# @todo delay_shift should be loaded from Task properties
def _completeTask(task_id):

    delay_shift = 7

    if task_id is not None:
        
        try:
            qs = Schedule.objects.get(task_id=task_id)
            qs.next_date = qs.next_date + timedelta(days=delay_shift) 
            qs.save()
            task = Task.objects.get(pk = task_id)

            print("saving changelog".encode('utf-8'))
            qs2 = Changelog.objects.create(task_id = task, action = TASK_LOG_DONE)
            qs2.save()

        except Schedule.DoesNotExist:
            raise Http404("Next task date does not exist")

        except DatabaseError as e:
            print(str(e))
            
            raise Http404("Error during save")
            
        print(str(qs).encode("utf-8"))
        print(str(qs2).encode("utf-8"))

    else:
        raise Http404("Task_id parameter should be set")



def _startTask(task_id, start_date):
        
    if start_date is None:
        print("start_date is not set")      
        raise Http404("start_date is not set ")

    else:
        print("start_date is ok, %s" % start_date)        
        
    if task_id is not None:
        
        try:
            task = Task.objects.get(pk = task_id)
            
            qs = Schedule.objects.create(task_id = task, next_date = start_date)
            
            qs.save()
            
            
            qs2 = Changelog.objects.create(task_id = task, action = TASK_LOG_START)
            qs2.save()
        except DatabaseError as e:
            print(str(e).encode("utf-8"))
            
            raise Http404("Error during save")
            
        print(str(qs).encode("utf-8"))

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
    task_list = Task.objects.filter(active=True).order_by('-id')
    template = loader.get_template('main/index.html')
    context = {
        'task_list': task_list,
    }
    return HttpResponse(template.render(context, request))


def task_start(request, task_id):
    start_date = request.POST.get('start_date', None)
    
    _startTask(task_id, start_date)
        
    return HttpResponse("Task %d now has start date %s, <a href='javascript:history.go(-1)'>Go back</a>" % (task_id, start_date))

def task_done(request, task_id):
    _completeTask(task_id)
    return HttpResponse("Task %d marked as done, <a href='javascript:history.go(-1)'>Go back</a>" % task_id)

"""
UI AJAX Methods 
"""

def ajax_task_done(request):
    task_id = int(request.GET.get('task_id', None))
    _completeTask(task_id)

    data = {
        'result': ("Task %d marked as done" % task_id)
    }

    return JsonResponse(data)

def ajax_task_postpone(request):
    task_id = int(request.GET.get('task_id', None))
    delay_shift = int(request.GET.get('delay_shift', None))
    _postponeTask(task_id, delay_shift)
    data = {
        'result': ("Task %d postponed for %d days" % (task_id, delay_shift))
    }

    return JsonResponse(data)





def task_postpone(request, task_id, delay_shift):
    _postponeTask(task_id, delay_shift)
    return HttpResponse("Task %d postponed for %d days, <a href='javascript:history.go(-1)'>Go back</a>" % (task_id, delay_shift))

def task(request, task_id):

    # task_list = Task.objects.order_by('-id')[:5]
    template = loader.get_template('main/task.html')
    task_row = Task.objects.get(pk=task_id)
    log_row = Changelog.objects.filter(task_id = task_id).order_by('-id')[:20]
    
    context = {
        'task_id': task_id,
        'task' : task_row,
        'log': log_row,
        'action_enum': {TASK_LOG_START : 'started', TASK_LOG_POSTPONE : 'postponed' , TASK_LOG_DONE : 'marked as done' }
    }
    return HttpResponse(template.render(context, request))


def authorize(request):
    template = loader.get_template('main/authorize.html')
    return HttpResponse(template.render(None, request))

