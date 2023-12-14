from django.test import TestCase
from uber_app.models import *
from django.http import *
from django.urls import reverse
import json


class stationTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        data = [
            Station(StationName = '台北車站'),
            Station(StationName = '台大校門口'),
            Station(StationName = '台積電新竹3廠東側門'),
            Station(StationName = '台積電台南2廠西側門'),
        ]
        Station.objects.bulk_create(data)
    def setUp(self):
        url =  reverse('user_register')
        data = {
            "email": "user@example.com",
            "password": "pa$$word",
            "name": "username",
            "avatar": "useravatar@email.com",
            "phone": "0912121212"
        }
        response = self.client.post(url,json.dumps(data),content_type = 'application/json')
        url =  reverse('user_login')
        data2 = {
            "email": "user@example.com",
            "password": "pa$$word",
        }
        response = self.client.post(url,json.dumps(data),content_type = 'application/json')
        self.all_stations = [{'id': 1, 'name': '台北車站'}, {'id': 2, 'name': '台大校門口'}, {'id': 3, 'name': '台積電新竹3廠東側門'}, {'id': 4, 'name': '台積電台南2廠西側門'}]

    def tearDown(self):
        url =  reverse('user_logout')
        response = self.client.post(url,content_type = 'application/json')

    def test_all_station(self):
        url = reverse('all_stations')
        response = self.client.get(url,content_type = 'application/json')
        decode_content = json.loads(response.content.decode("unicode_escape"))
        self.assertEqual(decode_content,self.all_stations)
    
    def test_specific_station(self):
        for i in range(1,5):
            url = reverse('specific_station',args = [i])
            response = self.client.get(url,content_type = 'application/json')
            decode_content = json.loads(response.content.decode("unicode_escape"))
            self.assertEqual(decode_content,self.all_stations[i - 1])