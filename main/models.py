from django.db import models
#from django.contrib.auth.models import User
from django.conf import settings




class Category(models.Model):
    name = models.CharField('Task period name',max_length=250)

    def __str__(self):
        return self.name


class Period(models.Model):
    name = models.CharField('Task period type',max_length=250)

    days = models.IntegerField(default=0)


    def __str__(self):
        return self.name


    

class Task(models.Model):
    user_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,  null = True)
    category_id = models.ForeignKey('Category',  on_delete=models.SET_NULL, null=True, related_name="category")
    
    
    task = models.CharField(max_length=250)
    start_date = models.DateField('initial date')
    active = models.BooleanField('Active', default = True)
    period = models.ForeignKey('Period',  on_delete=models.SET_NULL, null= True)
    period_data = models.IntegerField("Period data", default=0)

    def __str__(self):
        return str(self.user_id) + "-" + self.task 


class Schedule(models.Model):
        
    task_id = models.OneToOneField('Task', on_delete=models.CASCADE)
    next_date = models.DateField('next task date')

    def __str__(self):
        return str(self.task_id) + '-' + str(self.next_date)

    
class Changelog(models.Model):

    task_id = models.ForeignKey('Task', on_delete=models.CASCADE)

    """
    1 = started
    2 = postponed
    3 = done
    
    """
    action = models.IntegerField(default=0)
    log_date  = models.DateTimeField('action date', auto_now_add = True)


    def __str__(self):
        return str(self.task_id) + '-' + str(self.action) + '-' + str(self.log_date)

