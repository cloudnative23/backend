from django.test import TestCase
from uber_app.models import *
from django.http import *
from django.urls import reverse
import json

class notificationTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()