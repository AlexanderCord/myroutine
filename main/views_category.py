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


