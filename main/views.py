from django.http import HttpResponse,Http404, JsonResponse
from django.shortcuts import HttpResponseRedirect

from django.template import loader
from rest_framework import generics
from .serializers import *
from .models import *
from datetime import datetime  
from datetime import timedelta
from django.db import *
from django.contrib.auth import logout

from .static import *

import main.actions.task_actions as TA

"""
Google OAuth logout
"""
def signout(request):
    logout(request)
    return HttpResponseRedirect('/')


"""
Backend API methods
"""





class TaskPostpone(generics.ListAPIView):

    serializer_class = ScheduleSerializer
    
    # @todo refactor this postpone method to a separate model method
    def get_queryset(self):    
        task_id = self.request.query_params.get('task_id', None)
        delay_shift = self.request.query_params.get('delay_shift', None)

        TA._postponeTask(task_id, delay_shift) 
                    
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
    
    TA._startTask(task_id, start_date)
        
    return HttpResponse("Task %d now has start date %s, <a href='javascript:history.go(-1)'>Go back</a>" % (task_id, start_date))

def task_done(request, task_id):
    TA._completeTask(task_id)
    return HttpResponse("Task %d marked as done, <a href='javascript:history.go(-1)'>Go back</a>" % task_id)

"""
UI AJAX Methods 
"""

def ajax_task_start(request):
    task_id = int(request.GET.get('task_id', None))

    start_date = request.GET.get('start_date', None)
    
    next_date_val = TA._startTask(task_id, start_date)
        

    data = {
        'result': ("Task %d has now start date %s" % (task_id, start_date)),
        'next_date_val': datetime.strptime(next_date_val, '%Y-%m-%d').strftime('%b %d, %Y')  
    }

    return JsonResponse(data)


def ajax_task_done(request):
    task_id = int(request.GET.get('task_id', None))
    next_date_val = TA._completeTask(task_id)

    data = {
        'result': ("Task %d marked as done" % task_id),
        'next_date_val': datetime.strptime(next_date_val, '%Y-%m-%d').strftime('%b %d, %Y')  
    }

    return JsonResponse(data)

def ajax_task_postpone(request):
    task_id = int(request.GET.get('task_id', None))
    delay_shift = int(request.GET.get('delay_shift', None))
    next_date_val = TA._postponeTask(task_id, delay_shift)
    data = {
        'result': ("Task %d postponed for %d days" % (task_id, delay_shift)),
        'next_date_val': datetime.strptime(next_date_val, '%Y-%m-%d').strftime('%b %d, %Y')  
    }

    return JsonResponse(data)


def ajax_task_history(request):

    template = loader.get_template('main/ajax_task_history.html')
    task_id = int(request.GET.get('task_id', None))
    task_row = Task.objects.get(pk=task_id)
        
    log_row =  Changelog.objects.filter(task_id = task_id).order_by('-id')[:20] 
    
    context = {
        'task_id': task_id,
        'task' : task_row,
        'log': log_row,
        'action_enum': {TASK_LOG_START : 'started', TASK_LOG_POSTPONE : 'postponed' , TASK_LOG_DONE : 'marked as done' }
    }
    return HttpResponse(template.render(context, request))



def task_postpone(request, task_id, delay_shift):
    TA._postponeTask(task_id, delay_shift)
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




"""
UI - adding new task
"""
from .forms import NewTaskForm

from datetime import date


def task_add(request):

    # task_list = Task.objects.order_by('-id')[:5]
    template = loader.get_template('main/task_add.html')

    result = ""
    
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = NewTaskForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # redirect to a new URL:
            
            result = "Task has been added" 
            # @todo move to action file + use correct fields from model
            
            try:

                print("saving task".encode('utf-8'))
            
                qs = Task.objects.create(
                    user_id = Author.objects.get(pk=1), 
                    category_id = form.cleaned_data['category'], #Category.objects.get(pk = form.cleaned_data['category']), 
                    task = form.cleaned_data['task'],
                    start_date = date.today(), 
                    period = form.cleaned_data['period'] #Period.objects.get(pk = form.cleaned_data['period']) 
                          
                )
                qs.save()


            except Error as e:
                print(str(e))
            
                result = "Error during save"
                
                raise Http404("Error during save")
            
            print(str(qs).encode("utf-8"))
            
            
            form = ""                                                                    
    else:
        
        form = NewTaskForm()

    
    context = {
        'form': form,
        'result' : result,
        
    }
    return HttpResponse(template.render(context, request))






def authorize(request):
    template = loader.get_template('main/authorize.html')
    return HttpResponse(template.render(None, request))

