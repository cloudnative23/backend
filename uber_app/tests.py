from django.test import TestCase
from uber_app.models import *

# Create your tests here.
class ModelTest(TestCase):
    def setUp(self):
        Account.objects.create(Name="TestMan",Email='test@gmail.com',Password="1234")
    def test_setup(self):
        print(Account.objects.all())
        print(Account.objects.all().values())