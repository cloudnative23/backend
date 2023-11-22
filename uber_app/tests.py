from django.test import TestCase
from uber_app.models import *
from django.http import *
from django.urls import reverse
import json
from django.contrib.auth.models import User

# Create your tests here.
class ModelTest(TestCase):
    def setUp(self):
        user = User.objects.create_user('test@gmail.com','test@gmail.com','1234')
        Account.objects.create(Name="TestMan",Email='test@gmail.com',Password="1234")

    def test_login(self):
        data = {'email': 'test@gmail.com', 'password': '1234'}
        url = reverse('login')
        response = self.client.post(url, json.dumps(data), content_type='application/json')
        self.assertTrue(self.client.session['_auth_user_id'])
        self.assertEqual(response.status_code, 204)
        self.assertIsInstance(response, JsonResponse)

    def test_logout(self):
        url = reverse('logout')
        user = User.objects.create_user('testuser', 'test@example.com', 'testpassword')
        self.client.login(username='testuser', password='testpassword')
        self.assertTrue(self.client.session['_auth_user_id'])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(self.client.session.get('_auth_user_id'))
    
    def test_logout_fail(self):
        url = reverse('logout')
        self.client.login(username='testuser', password='testpassword')
        self.assertFalse(self.client.session.get('_auth_user_id'))
        response = self.client.post(url)
        self.assertFalse(self.client.session.get('_auth_user_id'))
        self.assertEqual(response.status_code, 401)