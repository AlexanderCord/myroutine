from django.http import HttpResponse
from django.template import loader


from rest_framework import generics

from .serializers import TaskSerializer

from .models import Task, Schedule

class TaskList(generics.ListAPIView):
    serializer_class = TaskSerializer
    def get_queryset(self):    
        queryset = Task.objects.select_related('period', 'category_id', 'user_id').filter(active=True)
        category = self.request.query_params.get('category', None)
        if category is not None:
            queryset = queryset.filter(category_id = category)
        queryset = queryset.all()
        print(str(queryset.query))
        return queryset
    
    


class TaskDetail(generics.RetrieveAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer


def index(request):
    task_list = Task.objects.filter(active=True).order_by('-id')[:5]
    template = loader.get_template('main/index.html')
    context = {
        'task_list': task_list,
    }
    return HttpResponse(template.render(context, request))


def task(request, task_id):
    # task_list = Task.objects.order_by('-id')[:5]
    template = loader.get_template('main/task.html')
    context = {
        'task_id': task_id,
    }
    return HttpResponse(template.render(context, request))




