from django.db import models


class Author(models.Model):
    login = models.CharField(max_length=250)
    def __str__(self):
        return self.login


class Category(models.Model):
    name = models.CharField('Task period name',max_length=250)

    def __str__(self):
        return self.name


class Period(models.Model):
    name = models.CharField('Task period type',max_length=250)

    def __str__(self):
        return self.name


    

class Task(models.Model):
    user_id = models.ForeignKey('Author', on_delete=models.CASCADE, null = True)
    category_id = models.ForeignKey('Category', on_delete=models.CASCADE, null=True)
    
    
    task = models.CharField(max_length=250)
    start_date = models.DateField('initial date')
    active = models.BooleanField('Active', default = True)
    period = models.ForeignKey('Period', on_delete=models.CASCADE, null= True)
    period_data = models.IntegerField("Period data", default=0)

    def __str__(self):
        return self.task


class Schedule(models.Model):
        
    task_id = models.OneToOneField('Task', on_delete=models.CASCADE)
    next_date = models.DateField('next task date')

    def __str__(self):
        return str(self.task_id) + '-' + str(self.next_date)

    
class Changelog(models.Model):
    task_id = models.ForeignKey('Task', on_delete=models.CASCADE)
    action = models.IntegerField(default=0)
    log_date  = models.DateTimeField('action date')
