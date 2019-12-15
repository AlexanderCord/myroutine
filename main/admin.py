from django.contrib import admin

from .models import Task, Schedule, Changelog, Category, Period, Author

admin.site.register(Task)
admin.site.register(Schedule)
admin.site.register(Changelog)
admin.site.register(Author)
admin.site.register(Category)
admin.site.register(Period)

# Register your models here.
