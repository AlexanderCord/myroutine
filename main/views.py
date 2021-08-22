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
Google OAuth logout
"""
@login_required
def signout(request):
    logout(request)
    return HttpResponseRedirect('/')


"""
Backend API methods
"""
from .views_api import *




##################################
# UI 
##################################

"""
MAIN PAGE
"""

def index(request):
    filter_category_id = -1
    
    if request.user.is_authenticated:
        
        filter_args = {
            'active' :True, 
            'user_id' : request.user.id
        }
        filter_category_id = int(request.GET.get('category_id', -1))

        if filter_category_id != -1:
            filter_args['category_id'] = Category.objects.get(pk=filter_category_id)


        date_blocks = {
            'past' : 'Past',
            'today' : 'Today',
            'tomorrow' : 'Tomorrow',
            'next7' : 'Next 7 days',
            'next30' : 'Next 30 days',
            'other' : 'Other'
        }
            
        task_list = Task.objects.annotate(week_day=Case(
            When(schedule__next_date = date.today(), then=Value(date_blocks['today'])),
            When(schedule__next_date = date.today() + timedelta(days=1) , then=Value(date_blocks['tomorrow'])),
            When(Q(schedule__next_date__gt = date.today() + timedelta(days=1)) & Q(schedule__next_date__lte = date.today() + timedelta(days=7)) , then=Value(date_blocks['next7'])),
            When(Q(schedule__next_date__gt = date.today()) & Q(schedule__next_date__lte = date.today() + timedelta(days=30)) , then=Value(date_blocks['next30'])),
            When(schedule__next_date__lt = date.today(), then=Value(date_blocks['past'])),
            default=Value(date_blocks['other']),
            output_field=CharField(),
        )).filter(**filter_args).order_by('schedule__next_date','priority')
        
        category_list = Task.objects.select_related("category_id__name").values("category_id","category_id__name").filter(active=True, user_id = request.user.id).order_by("-task_count").annotate(task_count = Count("id"))
        #print(category_list)
    else:
        task_list = []
        date_blocks = {}
        category_list = []
    template = loader.get_template('main/index.html')
    context = {
        'task_list': task_list,
        'category_list' : category_list,
        'filter_category_id' : filter_category_id,
        'date_blocks' : date_blocks
    }
    return HttpResponse(template.render(context, request))

"""
PROGRESS LOG PAGE
"""
@login_required
def progress_log(request):
    filter_category_id = -1


    filter_date_from = date.today() + timedelta(days=-30)
    filter_date_to = date.today() + timedelta(days=1)
        
    qs = Changelog.objects.filter(task_id__user_id=request.user.id)
    qs = qs.filter(action=TASK_LOG_DONE)
    log_rows = (qs
        .values(_id = Cast('log_date', DateField()))
        .annotate(count = Count('task_id', distinct = True))
        .filter(log_date__range=[filter_date_from, filter_date_to])
        .order_by('-_id')
    )    
    print(log_rows.query)
    log_rows = list(log_rows.all())
    log_rows = [{'date_block':x['_id']} for x in log_rows]
    for k,dt in enumerate(log_rows):
        current_date_from = dt['date_block']
        current_date_to = current_date_from + timedelta(days=1)
        task_obj = Task.objects.distinct().filter(active = True, user_id = request.user.id, changelog__action = TASK_LOG_DONE, changelog__log_date__range=[current_date_from, current_date_to])
        print(task_obj.query)
        log_rows[k]['task_list'] = task_obj.order_by('priority').all()
#    return HttpResponse(str(log_rows))
    template = loader.get_template('main/progress_log.html')
    context = {
        'log_rows': log_rows,
    }
    return HttpResponse(template.render(context, request))










"""
ARCHIVE PAGE
"""
@login_required
def archive(request):
    
    if request.user.is_authenticated:
        task_list = Task.objects.filter(active=False, user_id = request.user.id).order_by('-id')
    else:
        task_list = []
    template = loader.get_template('main/archive.html')
    context = {
        'task_list': task_list,
    }
    return HttpResponse(template.render(context, request))




"""
ARCHIVE DETAILS PAGE
"""
@login_required
def archive_detail(request, task_id):


    # task_list = Task.objects.order_by('-id')[:5]
    template = loader.get_template('main/archive_detail.html')
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
TASK STATS PAGE
"""
@login_required
def stats(request):
    
    if request.user.is_authenticated:
        category_list = Category.objects.filter(user_id = request.user.id).order_by('name')
    else:
        category_list = []
    template = loader.get_template('main/stats.html')
    context = {
        'category_list': category_list,
    }
    return HttpResponse(template.render(context, request))



"""
NOTIFICATION SETTINGS PAGE
"""
from .forms import NotificationForm
@login_required
def notifications(request):
    template = loader.get_template('main/notifications.html')

    result = ""
    
    try:
        settings_row = Notification.objects.get(user_id = request.user.id)
    except Notification.DoesNotExist:
        settings_row = []
        
    
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = NotificationForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # redirect to a new URL:
            
            result = "Settings has been saved" 
            # @todo move to action file + use correct fields from model
            
            try:

                print("saving settings".encode('utf-8'))
                
                if settings_row:
                    qs = Notification.objects.filter(user_id=request.user.id).update(
                        email = form.cleaned_data['email']
                    )
                else:
                    qs = Notification.objects.create(
                        user_id =  User.objects.get(pk=request.user.id), 
                        email = form.cleaned_data['email']
                    )
                    qs.save()

                


            except Error as e:
                print(str(e))
            
                result = "Error during save"
                
                raise Http404("Error during save")
            
            print(str(qs).encode("utf-8"))
            
            
#            form = ""                                                                    
    else:
        
        form = NotificationForm(initial = {'email' : settings_row.email if settings_row else False})

    
    context = {
        'form': form,
        'result' : result,
        'settings' : settings_row
        
    }
    return HttpResponse(template.render(context, request))




"""
AUTHORIZATION
"""



def authorize(request):
    template = loader.get_template('main/authorize.html')
    return HttpResponse(template.render(None, request))

