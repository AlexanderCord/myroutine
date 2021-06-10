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
        )).filter(**filter_args).order_by('schedule__next_date')
        
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
                    period_data = form.cleaned_data['period_data']
                          
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
                    period_data = form.cleaned_data['period_data']
                          
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
            'next_date' : task_next_date
        })

    
    context = {
        'form': form,
        'result' : result,
        'task_id' : task_id,
        'task' : task_row
        
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
AJAX for tasks page
"""

@login_required
def ajax_task_stats(request):

    filter_date_from = date.today() + timedelta(days=-30)
    filter_date_to = date.today() 
                  
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
            .annotate(count = Count('id'))
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


"""
CATEGORY LIST PAGE
"""
@login_required
def category(request):
    
    if request.user.is_authenticated:
        category_list = Category.objects.filter(user_id = request.user.id).order_by('name')
    else:
        category_list = []
    template = loader.get_template('main/category.html')
    context = {
        'category_list': category_list,
    }
    return HttpResponse(template.render(context, request))

"""
CATEGORY REMOVAL ACTION
"""
from .forms import NewCategoryForm
@login_required
def category_remove(request, category_id):
    TA._removeCategory(category_id, request.user.id)
    return HttpResponse("Category %d has been removed, <a href='javascript:history.go(-1)'>Go back</a>" % category_id)



"""
CATEGORY ADD PAGE
"""
@login_required
def category_add(request):
    template = loader.get_template('main/category_add.html')

    result = ""
    
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = NewCategoryForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # redirect to a new URL:
            
            result = "Category has been added" 
            # @todo move to action file + use correct fields from model
            
            try:

                print("saving category".encode('utf-8'))
            
                qs = Category.objects.create(
                    user_id =  User.objects.get(pk=request.user.id), 
                    name = form.cleaned_data['name']
                          
                )
                qs.save()


            except Error as e:
                print(str(e))
            
                result = "Error during save"
                
                raise Http404("Error during save")
            
            print(str(qs).encode("utf-8"))
            
            
            form = ""                                                                    
    else:
        
        form = NewCategoryForm()

    
    context = {
        'form': form,
        'result' : result,
        
    }
    return HttpResponse(template.render(context, request))





"""
CATEGORY EDIT PAGE
"""
@login_required
def category_edit(request, category_id):
    template = loader.get_template('main/category_edit.html')

    result = ""
    category_row = Category.objects.get(pk=category_id, user_id = request.user.id)
    
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = NewCategoryForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # redirect to a new URL:
            
            result = "Category has been added" 
            # @todo move to action file + use correct fields from model
            
            try:

                print("saving category".encode('utf-8'))
            
                qs = Category.objects.filter(pk=category_id).update(
                    name = form.cleaned_data['name']
                )


            except Error as e:
                print(str(e))
            
                result = "Error during save"
                
                raise Http404("Error during save")
            
            print(str(qs).encode("utf-8"))
            
            
            form = ""                                                                    
    else:
        
        form = NewCategoryForm(initial = {'name' : category_row.name})

    
    context = {
        'form': form,
        'result' : result,
        'category_id' : category_id,
        'category' : category_row
        
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

##################################
# AJAX METHODS AND HELPERS 
##################################


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




"""
AUTHORIZATION
"""



def authorize(request):
    template = loader.get_template('main/authorize.html')
    return HttpResponse(template.render(None, request))

