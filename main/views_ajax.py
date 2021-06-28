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
AJAX for tasks page
"""

@login_required
def ajax_task_stats(request):

    filter_date_from = date.today() + timedelta(days=-30)
    filter_date_to = date.today() + timedelta(days=1)
                  
    print(filter_date_from)
    print(filter_date_to)

    log_rows = {}
    log_types = ['all', TASK_LOG_DONE, TASK_LOG_POSTPONE]    
    for log_type in log_types:
        qs = Changelog.objects.filter(task_id__user_id=request.user.id)
        if not log_type == 'all':
            qs = qs.filter(action=log_type)
        log_rows[log_type] = (qs
            .values(_id = Cast('log_date', DateField()))
            .annotate(count = Count('task_id', distinct = True))
            .filter(log_date__range=[filter_date_from, filter_date_to])
            .order_by('_id')
        )    
        print(log_rows[log_type].query)
        log_rows[log_type] = list(log_rows[log_type].all())
    data = {
        'result' : {
            'data_all': log_rows['all'],
            'data_yes': log_rows[TASK_LOG_DONE],
            'data_no': log_rows[TASK_LOG_POSTPONE],
            
        }
    }
    return JsonResponse(data)



##################################
# AJAX METHODS AND HELPERS 
##################################



"""
UI AJAX Methods 
"""
@login_required
def ajax_task_start(request):
    task_id = int(request.GET.get('task_id', None))

    start_date = request.GET.get('start_date', None)
    
    next_date_val = TA._startTask(task_id, start_date)
        

    data = {
        'result': ("Task %d has now start date %s" % (task_id, start_date)),
        'next_date_val': datetime.strptime(next_date_val, '%Y-%m-%d').strftime('%b %d, %Y')  
    }

    return JsonResponse(data)
@login_required
def ajax_task_assign(request):
    try:

        task_id = int(request.GET.get('task_id', None))
        delay_shift = int(request.GET.get('delay_shift', None))
        next_date_val = TA._setNextDate(task_id, TA._getNextDate(delay_shift))
        data = {
            'result': ("Task %d assign for date %s" % (task_id, next_date_val)),
            'next_date_val': datetime.strptime(next_date_val, '%Y-%m-%d').strftime('%b %d, %Y')  
        }

        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)})






@login_required
def ajax_task_done(request):
    task_id = int(request.GET.get('task_id', None))
    try:
        next_date_val = TA._completeTask(task_id)

        data = {
            'result': ("Task %d marked as done" % task_id),
            'next_date_val': datetime.strptime(next_date_val, '%Y-%m-%d').strftime('%b %d, %Y')  
        }
        return JsonResponse(data)

    except Exception as e:
        return JsonResponse({'error': str(e)})


@login_required
def ajax_task_postpone(request):
    try:

        task_id = int(request.GET.get('task_id', None))
        delay_shift = int(request.GET.get('delay_shift', None))
        next_date_val = TA._postponeTask(task_id, delay_shift)
        data = {
            'result': ("Task %d postponed for %d days" % (task_id, delay_shift)),
            'next_date_val': datetime.strptime(next_date_val, '%Y-%m-%d').strftime('%b %d, %Y')  
        }

        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)})

@login_required
def ajax_task_archive(request):
    task_id = int(request.GET.get('task_id', None))
    TA._archiveTask(task_id)
    data = {
        'result': ("Task %d has been archived" % (task_id)),
    }
    
    return JsonResponse(data)

@login_required
def ajax_task_history(request):

    template = loader.get_template('main/ajax_task_history.html')
    task_id = int(request.GET.get('task_id', None))
    task_row = Task.objects.get(pk=task_id)
        
    log_row =  Changelog.objects.filter(task_id = task_id).order_by('-id')[:20] 
    
    context = {
        'task_id': task_id,
        'task' : task_row,
        'log': log_row,
        'action_enum': TASK_LOG_ENUM
    }
    return HttpResponse(template.render(context, request))


@login_required
def ajax_task_dates_done(request):

    task_id = int(request.GET.get('task_id', None))
        
    log_row =  list(Changelog.objects.filter(task_id = task_id, action=TASK_LOG_DONE).order_by('-log_date').values_list('log_date', flat = True))
    log_row = list( map( lambda x: x.strftime('%m/%d/%Y'), log_row ) )
    data = {
        'result' : log_row
    }
    return JsonResponse(data)


@login_required
def ajax_category_remove(request):
    category_id = int(request.GET.get('category_id', None))

    TA._removeCategory(category_id, request.user.id)
    data = {
        'result': ("Category %d has been removed" % (category_id)),
    }

    return JsonResponse(data)






