from django.test import TestCase
from uber_app.models import *
from django.http import *
from django.urls import reverse
import json
from django.test import Client

class routeTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        data = [
            Station(StationName = '台北車站'),
            Station(StationName = '台大校門口'),
            Station(StationName = '台積電新竹3廠東側門'),
            Station(StationName = '台積電台南2廠西側門'),
        ]
        Station.objects.bulk_create(data)
        cls.all_stations_mapping = {}
        cls.all_stations_mapping[1] = '台北車站'
        cls.all_stations_mapping[2] = '台大校門口'
        cls.all_stations_mapping[3] = '台積電新竹3廠東側門'
        cls.all_stations_mapping[4] = '台積電台南2廠西側門'
        url =  reverse('user_register')
        cls.driver_data = {
            "email": "user@example.com",
            "password": "pa$$word",
            "name": "username",
            "avatar": "useravatar.png",
            "phone": "0912121212"
        }
        cls.c = Client()
        response = cls.c.post(url,json.dumps(cls.driver_data),content_type = 'application/json')
        url =  reverse('user_login')
        response = cls.c.post(url,json.dumps(cls.driver_data),content_type = 'application/json')

    def test_add_route(self):
        url = reverse('add_or_get_all_route')
        data = {
            "date": "2024-10-22",
            "workStatus": False,
            "stations": [
                {
                "id": 3,
                "datetime": "2024-10-22T17:30"
                },
                {
                "id": 1,
                "datetime": "2024-10-22T17:50"
                },
                {
                "id": 2,
                "datetime": "2024-10-22T18:10"
                }
            ],
            "carInfo": {
                "model": "Tesla Model 3",
                "color": "紅色",
                "capacity": 4,
                "licensePlateNumber": "ABC-1234"
            }
        }
        response = self.c.post(url,json.dumps(data),content_type = 'application/json')
        self.assertEqual(response.status_code,200)
        decode_content = json.loads(response.content.decode("unicode_escape"))
        self.assertEqual(decode_content['status'],'available')
        self.assertEqual(decode_content['date'],data['date'])
        self.assertEqual(decode_content['driver']['name'],self.driver_data['name'])
        self.assertEqual(decode_content['driver']['avatar'],self.driver_data['avatar'])
        self.assertEqual(decode_content['driver']['email'],self.driver_data['email'])
        self.assertEqual(decode_content['driver']['phone'],self.driver_data['phone'])
        self.assertEqual(decode_content['carInfo'],data['carInfo'])
        self.assertEqual(decode_content['workStatus'],data['workStatus'])
        self.assertEqual(decode_content['passengers'],[])
        for i,station in enumerate(decode_content['stations']):
            self.assertEqual(self.all_stations_mapping[station['id']],station['name'])
            self.assertEqual(station['id'],data['stations'][i]['id'])
            self.assertEqual(station['datetime'][:-3],data['stations'][i]['datetime'])
            self.assertEqual(station['on-passengers'],[])
            self.assertEqual(station['off-passengers'],[])