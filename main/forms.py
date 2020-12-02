
from django import forms

from .models import Category, Period
from django.db.models import Q


class NewTaskForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user',None)
        super(NewTaskForm, self).__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(Q(user_id = self.user.id) | Q(pk = 1)  ).all().order_by('name')
    task = forms.CharField(label='Task', max_length=250)
    category  = forms.ModelChoiceField(queryset=Category.objects.all())
    period = forms.ModelChoiceField(queryset=Period.objects.all().order_by('name'))
    


class NewCategoryForm(forms.Form):
    name = forms.CharField(label='Category name', max_length=250)
        

class NotificationForm(forms.Form):
    email = forms.BooleanField(label='By email daily', required = False)
