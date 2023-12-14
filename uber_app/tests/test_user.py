from django.test import TestCase
from uber_app.models import *
from django.http import *
from django.urls import reverse
import json

class userTest(TestCase):
    def test_create(self):
        url =  reverse('user_register')
        data = {
            "email": "user1@example.com",
            "password": "pa$$word",
            "name": "username",
            "avatar": "useravatar@email.com",
            "phone": "0912121212"
            }
        response = self.client.post(url,json.dumps(data),content_type = 'application/json')
        self.assertEqual(response.status_code, 200)

    def test_login(self):
        url =  reverse('user_register')
        data = {
            "email": "user2@example.com",
            "password": "pa$$word",
            "name": "username",
            "avatar": "useravatar@email.com",
            "phone": "0912121212"
        }
        response = self.client.post(url,json.dumps(data),content_type = 'application/json')
        url =  reverse('user_login')
        data = {
            "email": "user2@example.com",
            "password": "pa$$word",
        }
        response = self.client.post(url,json.dumps(data),content_type = 'application/json')
        self.assertEqual(response.status_code, 204)

    def test_logout(self):
        url =  reverse('user_register')
        data = {
            "email": "user3@example.com",
            "password": "pa$$word",
            "name": "username",
            "avatar": "useravatar@email.com",
            "phone": "0912121212"
        }
        response = self.client.post(url,json.dumps(data),content_type = 'application/json')
        url =  reverse('user_login')
        data = {
            "email": "user3@example.com",
            "password": "pa$$word",
        }
        response = self.client.post(url,json.dumps(data),content_type = 'application/json')
        self.assertEqual(response.status_code, 204)
        url =  reverse('user_logout')
        response = self.client.post(url,content_type = 'application/json')
        self.assertEqual(response.status_code, 204)
        response = self.client.post(url,content_type = 'application/json')
        self.assertEqual(response.status_code, 401)
    
    def test_me(self):
        url =  reverse('user_register')
        data1 = {
            "email": "user4@example.com",
            "password": "pa$$word",
            "name": "username",
            "avatar": "useravatar@email.com",
            "phone": "0912121212"
        }
        response = self.client.post(url,json.dumps(data1),content_type = 'application/json')
        url =  reverse('user_login')
        data2 = {
            "email": "user4@example.com",
            "password": "pa$$word",
        }
        response = self.client.post(url,json.dumps(data2),content_type = 'application/json')
        self.assertEqual(response.status_code, 204)
        url =  reverse('user_me')
        response = self.client.get(url,content_type = 'application/json')
        self.assertEqual(response.status_code, 200)
        decode_content = json.loads(response.content.decode("unicode_escape"))
        self.assertEqual(data1['name'], decode_content['name'])
        self.assertEqual(data1['avatar'], decode_content['avatar'])
        self.assertEqual(data1['email'], decode_content['email'])
        self.assertEqual(data1['phone'], decode_content['phone'])