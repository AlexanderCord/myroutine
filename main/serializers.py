from rest_framework import serializers
from . import models


class PeriodSerializer(serializers.ModelSerializer):
    class Meta:        
        fields = ('id', 'name')
        model = models.Period


class CategorySerializer(serializers.ModelSerializer):
    class Meta:        
        fields = ('id', 'name')
        model = models.Category


class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:        
        fields = ('task_id', 'next_date')
        model = models.Schedule



class TaskSerializer(serializers.ModelSerializer):

    period_info = PeriodSerializer(source='period')
    category_info = CategorySerializer(source='category_id')
    schedule_info = serializers.SerializerMethodField('get_schedule')
    
    def get_schedule(self, task_id):
        qs = models.Schedule.objects.filter(task_id = task_id)
        serializer = ScheduleSerializer(instance = qs, many = True)
        return serializer.data
        
    class Meta:
        fields = ('id', 'user_id',  'task','period','active', 'start_date', 'category_id', 'period_data', 'period_info', 'category_info', 'schedule_info')
        model = models.Task

        
        
