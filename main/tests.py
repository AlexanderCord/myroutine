import datetime

from django.test import TestCase
from django.utils import timezone

from .models import Task


class TaskModelTests(TestCase):

    def test_task_create(self):
        self.assertIs(True, True)
        print("Test ok")
