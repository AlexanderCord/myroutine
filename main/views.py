from django.http import HttpResponse,Http404, JsonResponse
from django.shortcuts import HttpResponseRedirect

from django.template import loader
from .models import *
from datetime import datetime  
from datetime import timedelta
from django.db import *
from django.contrib.auth import logout
from django.contrib.auth.models import User


from .static import *

import main.actions.task_actions as TA
from django.db.models import Count

"""
Google OAuth logout
"""
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
    
    
        filter_category_id = int(request.GET.get('category_id', -1))
        if filter_category_id == -1:
            task_list = Task.objects.filter(active=True, user_id = request.user.id).order_by('-id')
        else:
            #filter by category
            task_list = Task.objects.select_related("category_id").filter(active=True, category_id = Category.objects.get(pk=filter_category_id),user_id = request.user.id).order_by('-id')
        
        category_list = Task.objects.select_related("category_id__name").values("category_id","category_id__name").filter(active=True, user_id = request.user.id).order_by("-task_count").annotate(task_count = Count("id"))
        #print(category_list)
    else:
        task_list = []
        category_list = []
    template = loader.get_template('main/index.html')
    context = {
        'task_list': task_list,
        'category_list' : category_list,
        'filter_category_id' : filter_category_id,
    }
    return HttpResponse(template.render(context, request))




"""
TASK DETAILS PAGE
"""

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
        'action_enum': {TASK_LOG_START : 'started', TASK_LOG_POSTPONE : 'postponed' , TASK_LOG_DONE : 'marked as done' }
    }
    return HttpResponse(template.render(context, request))




"""
ADD NEW TASK PAGE 
"""
from .forms import NewTaskForm

from datetime import date


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
        
        form = NewTaskForm(user=request.user)

    
    context = {
        'form': form,
        'result' : result,
        
    }
    return HttpResponse(template.render(context, request))


"""
TASK EDIT PAGE
"""

def task_edit(request,task_id):

    # task_list = Task.objects.order_by('-id')[:5]
    template = loader.get_template('main/task_edit.html')

    result = ""
    task_row = Task.objects.get(pk=task_id, user_id = request.user.id)
    
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = NewTaskForm(request.POST, user=request.user)
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
                    period = form.cleaned_data['period'] #Period.objects.get(pk = form.cleaned_data['period']) 
                          
                )


            except Error as e:
                print(str(e))
            
                result = "Error during save"
                
                raise Http404("Error during save")
            
            print(str(qs).encode("utf-8"))
            
            
            form = ""                                                                    
    else:
        
        form = NewTaskForm(user=request.user, initial = {'task' : task_row.task, 'category' : task_row.category_id, 'period' : task_row.period   })

    
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
        'action_enum': {TASK_LOG_START : 'started', TASK_LOG_POSTPONE : 'postponed' , TASK_LOG_DONE : 'marked as done' , TASK_LOG_ARCHIVE : 'archived'}
    }
    return HttpResponse(template.render(context, request))



"""
CATEGORY LIST PAGE
"""

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
def category_remove(request, category_id):
    TA._removeCategory(category_id, request.user.id)
    return HttpResponse("Category %d has been removed, <a href='javascript:history.go(-1)'>Go back</a>" % category_id)



"""
CATEGORY ADD PAGE
"""

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



##################################
# AJAX METHODS AND HELPERS 
##################################


# @todo - insert check for authorization + user_id task ownership task into all actions / ajax methods/ API

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


def ajax_task_archive(request):
    task_id = int(request.GET.get('task_id', None))
    TA._archiveTask(task_id)
    data = {
        'result': ("Task %d has been archived" % (task_id)),
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
        'action_enum': {TASK_LOG_START : 'started', TASK_LOG_POSTPONE : 'postponed' , TASK_LOG_DONE : 'marked as done' , TASK_LOG_ARCHIVE : 'archived'}
    }
    return HttpResponse(template.render(context, request))



def task_postpone(request, task_id, delay_shift):
    TA._postponeTask(task_id, delay_shift)
    return HttpResponse("Task %d postponed for %d days, <a href='javascript:history.go(-1)'>Go back</a>" % (task_id, delay_shift))


def task_archive(request, task_id):
    TA._archiveTask(task_id)
    return HttpResponse("Task %d has been archived, <a href='javascript:history.go(-1)'>Go back</a>" % (task_id))




"""
AUTHORIZATION
"""



def authorize(request):
    template = loader.get_template('main/authorize.html')
    return HttpResponse(template.render(None, request))

