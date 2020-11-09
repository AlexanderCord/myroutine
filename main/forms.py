
from django import forms

from .models import Category, Period

class NewTaskForm(forms.Form):
    task = forms.CharField(label='Task', max_length=250)
    category  = forms.ModelChoiceField(queryset=Category.objects.all().order_by('name'))
    period = forms.ModelChoiceField(queryset=Period.objects.all().order_by('name'))
    
    
