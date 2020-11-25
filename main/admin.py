from django.contrib import admin

from .models import Task, Schedule, Changelog, Category, Period, Notification

admin.site.register(Task)
admin.site.register(Schedule)
admin.site.register(Changelog)
admin.site.register(Category)
admin.site.register(Period)
admin.site.register(Notification)

# Register your models here.
