from django.test import TestCase
from uber_app.models import *
from django.http import *
from django.urls import reverse
import json
from django.contrib.auth.models import User


ERROR_PARA = 400
NOT_LOGIN = 401
NOT_FOUND = 404
PERMISSION_ERROR = 403

# Create your tests here.
class ModelTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        user = User.objects.create_user('test@gmail.com','test@gmail.com','1234')
        Account.objects.create(Name="TestMan",Email='test@gmail.com',Password="1234")
        Station.objects.create(StationName='台北車站')
        Station.objects.create(StationName='台大校門口')
        Station.objects.create(StationName='台積電新竹3廠東側門')
        Station.objects.create(StationName='台積電台南2廠西側門')

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
        self.assertEqual(response.status_code, NOT_LOGIN)
    
    def test_station_detail(self):
        url = reverse('station_detail',args=[1])
        user = User.objects.create_user('testuser', 'test@example.com', 'testpassword')
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        decode_content = json.loads(response.content.decode("unicode_escape"))
        self.assertEqual(decode_content['id'], 1)
        self.assertEqual(decode_content['name'], '台北車站')

        url = reverse('station_detail',args=[2])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        decode_content = json.loads(response.content.decode("unicode_escape"))
        self.assertEqual(decode_content['id'], 2)
        self.assertEqual(decode_content['name'], '台大校門口')

        url = reverse('station_detail',args=[3])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        decode_content = json.loads(response.content.decode("unicode_escape"))
        self.assertEqual(decode_content['id'], 3)
        self.assertEqual(decode_content['name'], '台積電新竹3廠東側門')

        url = reverse('station_detail',args=[5])
        response = self.client.get(url)
        self.assertEqual(response.status_code, NOT_FOUND)
        decode_content = json.loads(response.content.decode("unicode_escape"))
    
    def test_station_list_view(self):
        url = reverse('station_list')
        user = User.objects.create_user('testuser', 'test@example.com', 'testpassword')
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(url)
        decode_content = json.loads(response.content.decode("unicode_escape"))
        answer = [{"id": 1,"name": "台北車站"},{"id": 2,"name": "台大校門口"},{"id": 3,"name": "台積電新竹3廠東側門"},{"id": 4,"name": "台積電台南2廠西側門"}]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(decode_content, answer)