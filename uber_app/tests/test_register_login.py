from django.test import TestCase
from uber_app.models import *
from django.http import *
from django.urls import reverse
import json

class register_login_Test(TestCase):
    def test_create(self):
        url =  reverse('user_register')
        data = {
            "email": "user@example.com",
            "password": "pa$$word",
            "name": "username",
            "avatar": "useravatar.png",
            "phone": "0912121212"
            }
        response = self.client.post(url,json.dumps(data),content_type = 'application/json')
        self.assertEqual(response.status_code, 200)
    
    def test_login(self):
        url =  reverse('user_register')
        data = {
            "email": "user@example.com",
            "password": "pa$$word",
            "name": "username",
            "avatar": "useravatar.png",
            "phone": "0912121212"
        }
        response = self.client.post(url,json.dumps(data),content_type = 'application/json')
        url =  reverse('user_login')
        response = self.client.post(url,json.dumps(data),content_type = 'application/json')
        self.assertEqual(response.status_code, 204)