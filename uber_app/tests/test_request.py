from django.test import TestCase
from uber_app.models import *
from django.http import *
from django.urls import reverse
import json
from django.test import Client
from datetime import date, datetime

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
            "email": "driver@example.com",
            "password": "pa$$word",
            "name": "username",
            "avatar": "useravatar.png",
            "phone": "0912121212"
        }
        cls.driver = Client()
        response = cls.driver.post(url,json.dumps(cls.driver_data),content_type = 'application/json')
        url =  reverse('user_login')
        response = cls.driver.post(url,json.dumps(cls.driver_data),content_type = 'application/json')
        url = reverse('add_or_get_all_route')
        cls.route_data = {
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
        response = cls.driver.post(url,json.dumps(cls.route_data),content_type = 'application/json')
        decode_content = json.loads(response.content.decode("unicode_escape"))
        cls.route1_id = decode_content['id']
        url =  reverse('user_register')
        cls.passenger_data = {
            "email": "passenger@example.com",
            "password": "pa$$word",
            "name": "username",
            "avatar": "useravatar.png",
            "phone": "0912121212"
        }
        cls.passenger = Client()
        response = cls.passenger.post(url,json.dumps(cls.passenger_data),content_type = 'application/json')
        decode_content = json.loads(response.content.decode("unicode_escape"))
        cls.passenger_id = decode_content['id']
        url =  reverse('user_login')
        response = cls.passenger.post(url,json.dumps(cls.passenger_data),content_type = 'application/json')
        url = reverse('add_or_get_all_request')
        cls.passenger_request_data = {
            "workStatus": False,
            "route": cls.route1_id,
            "on-station": 3,
            "off-station": 2
        }
        response = cls.passenger.post(url,json.dumps(cls.passenger_request_data),content_type = 'application/json')
        decode_content = json.loads(response.content.decode("unicode_escape"))
        cls.request_id = decode_content['id']
    
    def test_get_and_delete_specific_request(self):
        url = reverse('get_or_delete_specific_request',args = [self.request_id])
        response = self.passenger.get(url,content_type = 'application/json')
        self.assertEqual(response.status_code,200)
        decode_content = json.loads(response.content.decode("unicode_escape"))
        self.assertEqual(decode_content['passenger']['name'], self.passenger_data['name'])
        self.assertEqual(decode_content['passenger']['avatar'], self.passenger_data['avatar'])
        self.assertEqual(decode_content['passenger']['email'], self.passenger_data['email'])
        self.assertEqual(decode_content['passenger']['phone'], self.passenger_data['phone'])
        self.assertEqual(decode_content['status'],'new')
        self.assertEqual(decode_content['date'],str(date.today()))
        self.assertEqual(decode_content['workStatus'],self.route_data['workStatus'])
        self.assertEqual(decode_content['on-station']['id'],self.passenger_request_data['on-station'])
        self.assertEqual(decode_content['off-station']['id'],self.passenger_request_data['off-station'])
        self.assertEqual(decode_content['route']['id'],self.route1_id)
        self.assertEqual(decode_content['route']['status'],'available')
        self.assertEqual(decode_content['route']['date'],self.route_data['date'])
        self.assertEqual(decode_content['route']['driver']['name'],self.driver_data['name'])
        self.assertEqual(decode_content['route']['driver']['avatar'],self.driver_data['avatar'])
        self.assertEqual(decode_content['route']['driver']['email'],self.driver_data['email'])
        self.assertEqual(decode_content['route']['driver']['phone'],self.driver_data['phone'])
        self.assertEqual(decode_content['route']['carInfo'],self.route_data['carInfo'])
        self.assertEqual(decode_content['route']['passengers'],[])
        for i,station in enumerate(decode_content['route']['stations']):
            self.assertEqual(self.all_stations_mapping[station['id']],station['name'])
            self.assertEqual(station['id'],self.route_data['stations'][i]['id'])
            self.assertEqual(station['datetime'][:-3],self.route_data['stations'][i]['datetime'])
            self.assertEqual(station['on-passengers'],[])
            self.assertEqual(station['off-passengers'],[])
        response = self.passenger.delete(url,content_type = 'application/json')
        self.assertEqual(response.status_code,204)
    
    def test_accept_request(self):
        url = reverse('accept_request',args = [self.request_id])
        response = self.driver.put(url,content_type = 'application/json')
        self.assertEqual(response.status_code,204)
        url = reverse('get_or_delete_specific_route',args = [self.route1_id])
        response = self.passenger.get(url,content_type = 'application/json')
        self.assertEqual(response.status_code,200)
        decode_content = json.loads(response.content.decode("unicode_escape"))
        for station_info in decode_content['stations']:
            if station_info['id'] == 3:
                self.assertEqual(station_info['on-passengers'],[self.passenger_id])
            elif station_info['id'] == 2:
                self.assertEqual(station_info['off-passengers'],[self.passenger_id])
    
    def test_deny_request(self):
        url = reverse('deny_request',args = [self.request_id])
        response = self.driver.put(url,content_type = 'application/json')
        self.assertEqual(response.status_code,204)
    
    def test_get_all_request(self):
        url = reverse('add_or_get_all_request')
        #TODO