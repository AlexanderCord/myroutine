"""
Task update methods
"""

from django.http import HttpResponse,Http404, JsonResponse
from django.shortcuts import HttpResponseRedirect
from datetime import datetime, date
from datetime import timedelta
from main.static import *
from main.models import *

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

    next_date_val = None
    if task_id is not None:
        
        try:
            qs = Schedule.objects.get(task_id=task_id)
            qs.next_date = date.today() + timedelta(days=delay_shift) 
            next_date_val = str(qs.next_date)
            
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

    return next_date_val

def _archiveTask(task_id):


    if task_id is not None:
        
        try:
            task_original = Task.objects.get(pk = task_id)
            task_original.active = False
            task_original.save()
            
            print("saving changelog".encode('utf-8'))
            qs2 = Changelog.objects.create(task_id = task_original, action = TASK_LOG_ARCHIVE)
            qs2.save()

        except Task.DoesNotExist:
            raise Http404("Task does not exist")

        except DatabaseError as e:
            print(str(e))
            
            raise Http404("Error during save")
            
        print(str(task_original).encode("utf-8"))
        print(str(qs2).encode("utf-8"))

    else:
        raise Http404("Task_id parameter should be set")



def _completeTask(task_id):

    delay_shift = 7
    next_date_val = None

    if task_id is not None:
        
        try:
            task_original = Task.objects.select_related('period').get(pk = task_id)
            delay_shift = task_original.period.days
            print("Delay shift from db %d" % delay_shift)
            
            qs = Schedule.objects.get(task_id=task_id)
            qs.next_date = date.today() + timedelta(days=delay_shift) 
            next_date_val = str(qs.next_date)
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

    return next_date_val



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


    return start_date




def _removeCategory(category_id, user_id):
        
    default_category_id = 1    
    if category_id is not None:
        
        try:
        
            # updating tasks to default category
            qs = Task.objects.filter(user_id = user_id, category_id = category_id).update(category_id = default_category_id)

            # removing category            
            qs2 = Category.objects.filter(user_id = user_id, pk = category_id).delete()
        except DatabaseError as e:
            print(str(e).encode("utf-8"))
            
            raise Http404("Error during save")
            
        print(str(qs).encode("utf-8"))
        print(str(qs2).encode("utf-8"))
        

    else:
        raise Http404("Category_id parameter should be set")

