from django.test import TestCase
from uber_app.models import *
from django.http import *
from django.urls import reverse
import json
from django.test import Client

class userTest(TestCase):
    def setUp(self):
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
        self.name = 'username'
        self.email = 'user@example.com'
        self.avatar = "useravatar.png"
        self.phone = '0912121212'

    def tearDown(self):
        url =  reverse('user_logout')
        response = self.client.post(url,content_type = 'application/json')

    def test_logout(self):
        url =  reverse('user_logout')
        response = self.client.post(url,content_type = 'application/json')
        self.assertEqual(response.status_code, 204)
        response = self.client.post(url,content_type = 'application/json')
        self.assertEqual(response.status_code, 401)
    
    def test_me(self):
        url =  reverse('user_me')
        response = self.client.get(url,content_type = 'application/json')
        self.assertEqual(response.status_code, 200)
        decode_content = json.loads(response.content.decode("unicode_escape"))
        self.assertEqual(self.name, decode_content['name'])
        self.assertEqual(self.avatar, decode_content['avatar'])
        self.assertEqual(self.email, decode_content['email'])
        self.assertEqual(self.phone, decode_content['phone'])