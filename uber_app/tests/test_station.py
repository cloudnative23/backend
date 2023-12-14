from django.test import TestCase
from uber_app.models import *
from django.http import *
from django.urls import reverse
import json
from django.test import Client

class stationTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        data = [
            Station(StationName = '台北車站'),
            Station(StationName = '台大校門口'),
            Station(StationName = '台積電新竹3廠東側門'),
            Station(StationName = '台積電台南2廠西側門'),
        ]
        Station.objects.bulk_create(data)
        url =  reverse('user_register')
        data = {
            "email": "user@example.com",
            "password": "pa$$word",
            "name": "username",
            "avatar": "useravatar.png",
            "phone": "0912121212"
        }
        cls.c = Client()
        response = cls.c.post(url,json.dumps(data),content_type = 'application/json')
        url =  reverse('user_login')
        response = cls.c.post(url,json.dumps(data),content_type = 'application/json')
        cls.all_stations = [{'id': 1, 'name': '台北車站'}, {'id': 2, 'name': '台大校門口'}, {'id': 3, 'name': '台積電新竹3廠東側門'}, {'id': 4, 'name': '台積電台南2廠西側門'}]

    def test_all_station(self):
        url = reverse('all_stations')
        response = self.c.get(url,content_type = 'application/json')
        decode_content = json.loads(response.content.decode("unicode_escape"))
        self.assertEqual(decode_content,self.all_stations)
    
    def test_specific_station(self):
        for i in range(1,5):
            url = reverse('specific_station',args = [i])
            response = self.c.get(url,content_type = 'application/json')
            decode_content = json.loads(response.content.decode("unicode_escape"))
            self.assertEqual(decode_content,self.all_stations[i - 1])