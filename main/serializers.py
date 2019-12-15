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


class TaskSerializer(serializers.ModelSerializer):

    period_info = PeriodSerializer(source='period')
    category_info = CategorySerializer(source='category_id')
    class Meta:
        fields = ('id', 'user_id',  'task','period','active', 'start_date', 'category_id', 'period_data', 'period_info', 'category_info')
        model = models.Task

        
        
