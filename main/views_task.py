from django.http import HttpResponse,Http404, JsonResponse
from django.shortcuts import HttpResponseRedirect

from django.template import loader
from .models import *
from django.db import *
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.db.models.functions import Cast
from django.db.models.fields import DateField
from datetime import datetime, date
from datetime import timedelta
from django.contrib.auth.decorators import login_required


from .static import *

import main.actions.task_actions as TA
from django.db.models import (Count, Case, When, Value, CharField, Q)






"""
TASK DETAILS PAGE
"""
@login_required
def task(request, task_id):


    # task_list = Task.objects.order_by('-id')[:5]
    template = loader.get_template('main/task.html')
    if request.user.is_authenticated:
        try:
            task_row = Task.objects.get(pk=task_id, user_id = request.user.id)
            log_row = Changelog.objects.filter(task_id = task_id).order_by('-id')[:20]
        except Task.DoesNotExist:
            raise Http404("Task doesn't exist")
        except DatabaseError as e:
            print(str(e))
                                
            raise Http404("Error during loading task")
    else:
        task_row = []
        log_row = []
        
    context = {
        'task_id': task_id,
        'task' : task_row,
        'log': log_row,
        'action_enum': TASK_LOG_ENUM
    }
    return HttpResponse(template.render(context, request))




"""
ADD NEW TASK PAGE 
"""
from .forms import NewTaskForm, EditTaskForm

from datetime import date

@login_required
def task_add(request):

    # task_list = Task.objects.order_by('-id')[:5]
    template = loader.get_template('main/task_add.html')

    result = ""
    
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = NewTaskForm(request.POST, user=request.user)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # redirect to a new URL:
            
            result = "Task has been added" 
            # @todo move to action file + use correct fields from model
            
            try:

                print("saving task".encode('utf-8'))
            
                qs = Task.objects.create(
                    user_id =  User.objects.get(pk=request.user.id), 
                    category_id = form.cleaned_data['category'], #Category.objects.get(pk = form.cleaned_data['category']), 
                    task = form.cleaned_data['task'],
                    start_date = date.today(), 
                    period = form.cleaned_data['period'],
                    period_data = form.cleaned_data['period_data'],
                    priority = form.cleaned_data['priority'] if form.cleaned_data['priority'] else 0
                    
                    
                          
                )
                qs.save()


            except Error as e:
                print(str(e))
            
                result = "Error during save"
                
                raise Http404("Error during save")
            
            print(str(qs).encode("utf-8"))
            
            
            form = ""                                                                    
    else:
        
        
        form = NewTaskForm(user=request.user, initial = {
            'period_data' : 1
        })

    
    context = {
        'form': form,
        'result' : result,
        
    }
    return HttpResponse(template.render(context, request))


"""
TASK EDIT PAGE
"""
@login_required
def task_edit(request,task_id):

    # task_list = Task.objects.order_by('-id')[:5]
    template = loader.get_template('main/task_edit.html')

    result = ""
    task_row = Task.objects.get(pk=task_id, user_id = request.user.id)
    
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = EditTaskForm(request.POST, user=request.user)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # redirect to a new URL:
            
            result = "Task has been updated"
            # @todo move to action file + use correct fields from model
            
            try:

                print("saving task".encode('utf-8'))
            
                qs = Task.objects.filter(pk = task_id).update(
                    category_id = form.cleaned_data['category'], #Category.objects.get(pk = form.cleaned_data['category']), 
                    task = form.cleaned_data['task'],
                    period = form.cleaned_data['period'],
                    period_data = form.cleaned_data['period_data'],
                    priority = form.cleaned_data['priority']
                          
                )
                
                TA._setNextDate(task_id, form.cleaned_data['next_date'])


            except Error as e:
                print(str(e))
            
                result = "Error during save"
                
                raise Http404("Error during save")
            
            print(str(qs).encode("utf-8"))
            
            
            form = ""                                                                    
    else:
        
        try:
            task_next_date = task_row.schedule.next_date 
        except Schedule.DoesNotExist:
            task_next_date = ""
        
        form = EditTaskForm(user=request.user, initial = {
            'task' : task_row.task,
            'category' : task_row.category_id,
            'period' : task_row.period  ,
            'period_data' : task_row.period_data  ,
            'priority' : task_row.priority,            
            'next_date' : task_next_date

        })

    
    context = {
        'form': form,
        'result' : result,
        'task_id' : task_id,
        'task' : task_row
        
    }
    return HttpResponse(template.render(context, request))





# @todo - insert check for authorization + user_id task ownership task into all actions / ajax methods/ API
@login_required
def task_start(request, task_id):
    start_date = request.POST.get('start_date', None)

    TA._startTask(task_id, start_date)

    return HttpResponse("Task %d now has start date %s, <a href='javascript:history.go(-1)'>Go back</a>" % (task_id, start_date))
@login_required
def task_done(request, task_id):


    TA._completeTask(task_id)
    return HttpResponse("Task %d marked as done, <a href='javascript:history.go(-1)'>Go back</a>" % task_id)

@login_required
def task_postpone(request, task_id, delay_shift):
    TA._postponeTask(task_id, delay_shift)
    return HttpResponse("Task %d postponed for %d days, <a href='javascript:history.go(-1)'>Go back</a>" % (task_id, delay_shift))

@login_required
def task_assign(request, task_id, delay_shift):
    try:

        task_id = int(task_id)
        delay_shift = int(delay_shift)
        next_date_val = TA._setNextDate(task_id, TA._getNextDate(delay_shift))
        data = {
            'result': ("Task %d assign for date %s" % (task_id, next_date_val)),
            'next_date_val': datetime.strptime(next_date_val, '%Y-%m-%d').strftime('%b %d, %Y')
        }

        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)})



@login_required
def task_archive(request, task_id):
    TA._archiveTask(task_id)
    return HttpResponse("Task %d has been archived, <a href='javascript:history.go(-1)'>Go back</a>" % (task_id))
        
        