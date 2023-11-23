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
SUCCESS_NO_DATA = 204
SUCESS_WITH_DATA = 200
# Create your tests here.
class ModelTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        user = User.objects.create_user('test@gmail.com','test@gmail.com','1234')
        Account.objects.create(UserID=user.id,Name="TestMan",Email='test@gmail.com',Password="1234")
        Station.objects.create(StationName='台北車站')
        Station.objects.create(StationName='台大校門口')
        Station.objects.create(StationName='台積電新竹3廠東側門')
        Station.objects.create(StationName='台積電台南2廠西側門')

    def test_login(self):
        data = {'email': 'test@gmail.com', 'password': '1234'}
        url = reverse('login')
        response = self.client.post(url, json.dumps(data), content_type='application/json')
        self.assertTrue(self.client.session['_auth_user_id'])
        self.assertEqual(response.status_code, SUCCESS_NO_DATA)

    def test_logout(self):
        url = reverse('logout')
        user = User.objects.create_user('testuser', 'test@example.com', 'testpassword')
        self.client.login(username='testuser', password='testpassword')
        self.assertTrue(self.client.session['_auth_user_id'])
        response = self.client.post(url,content_type='application/json')
        self.assertEqual(response.status_code, SUCCESS_NO_DATA)
        self.assertFalse(self.client.session.get('_auth_user_id'))
    
    def test_logout_fail(self):
        url = reverse('logout')
        self.client.login(username='testuser', password='testpassword')
        self.assertFalse(self.client.session.get('_auth_user_id'))
        response = self.client.post(url,content_type='application/json')
        self.assertFalse(self.client.session.get('_auth_user_id'))
        self.assertEqual(response.status_code, NOT_LOGIN)
    
    def test_station_detail(self):
        url = reverse('station_detail',args=[1])
        user = User.objects.create_user('testuser', 'test@example.com', 'testpassword')
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(url,content_type='application/json')
        self.assertEqual(response.status_code, SUCESS_WITH_DATA)
        decode_content = json.loads(response.content.decode("unicode_escape"))
        self.assertEqual(decode_content['id'], 1)
        self.assertEqual(decode_content['name'], '台北車站')

        url = reverse('station_detail',args=[2])
        response = self.client.get(url,content_type='application/json')
        self.assertEqual(response.status_code, SUCESS_WITH_DATA)
        decode_content = json.loads(response.content.decode("unicode_escape"))
        self.assertEqual(decode_content['id'], 2)
        self.assertEqual(decode_content['name'], '台大校門口')

        url = reverse('station_detail',args=[3])
        response = self.client.get(url,content_type='application/json')
        self.assertEqual(response.status_code, SUCESS_WITH_DATA)
        decode_content = json.loads(response.content.decode("unicode_escape"))
        self.assertEqual(decode_content['id'], 3)
        self.assertEqual(decode_content['name'], '台積電新竹3廠東側門')

        url = reverse('station_detail',args=[5])
        response = self.client.get(url,content_type='application/json')
        self.assertEqual(response.status_code, NOT_FOUND)
        decode_content = json.loads(response.content.decode("unicode_escape"))
    
    def test_station_list_view(self):
        url = reverse('station_list')
        user = User.objects.create_user('testuser', 'test@example.com', 'testpassword')
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(url,content_type='application/json')
        decode_content = json.loads(response.content.decode("unicode_escape"))
        answer = [{"id": 1,"name": "台北車站"},{"id": 2,"name": "台大校門口"},{"id": 3,"name": "台積電新竹3廠東側門"},{"id": 4,"name": "台積電台南2廠西側門"}]
        self.assertEqual(response.status_code, SUCESS_WITH_DATA)
        self.assertEqual(decode_content, answer)
    
    def test_add_route(self):
        url = reverse('add_route')
        user = User.objects.create_user('testuser', 'test@example.com', 'testpassword')
        Account.objects.create(UserID=user.id,Name='testuser',Email='test@example.com',Password='testpassword')
        self.client.login(username='testuser', password='testpassword')
        data = {"date": "2023-10-22","workStatus": False,"stations": [{"id": 3,"datetime": "2023-10-22T17:30"},{"id": 1,"datetime": "2023-10-22T17:50"},{"id": 2,"datetime": "2023-10-22T18:10"}],"carInfo": {"color": "紅色","capacity": 4,"licensePlateNumber": "ABC-1234"}}
        response = self.client.post(url,json.dumps(data),content_type='application/json')
        self.assertEqual(response.status_code, SUCESS_WITH_DATA)
        decode_content = json.loads(response.content.decode("unicode_escape"))
        self.assertNotEqual(len(decode_content),0)
    
    def test_delete_route(self):
        url1 = reverse('add_route')
        user = User.objects.create_user('testuser', 'test@example.com', 'testpassword')
        Account.objects.create(UserID=user.id,Name='testuser',Email='test@example.com',Password='testpassword')
        self.client.login(username='testuser', password='testpassword')
        data = {"date": "2023-10-22","workStatus": False,"stations": [{"id": 3,"datetime": "2023-10-22T17:30"},{"id": 1,"datetime": "2023-10-22T17:50"},{"id": 2,"datetime": "2023-10-22T18:10"}],"carInfo": {"color": "紅色","capacity": 4,"licensePlateNumber": "ABC-1234"}}
        response = self.client.post(url1,json.dumps(data),content_type='application/json')
        self.assertEqual(response.status_code, SUCESS_WITH_DATA)
        decode_content = json.loads(response.content.decode("unicode_escape"))
        RoutePassenger.objects.create(PassengerID=5,RouteID=decode_content['id'],On=6,Off=7)
        url2 = reverse('get_delete_route',args=[decode_content['id']])
        response = self.client.delete(url2,content_type='application/json')
        self.assertEqual(response.status_code, SUCCESS_NO_DATA)
        self.assertEqual(len(Route.objects.filter(RouteID=decode_content['id'])),0)
        self.assertEqual(len(RouteCar.objects.filter(RouteID=decode_content['id'])),0)
        self.assertEqual(len(RouteStation.objects.filter(RouteID=decode_content['id'])),0)
        self.assertEqual(len(RoutePassenger.objects.filter(RouteID=decode_content['id'])),0)
    
    def test_add_stop_station(self):
        url1 = reverse('add_route')
        user = User.objects.create_user('testuser', 'test@example.com', 'testpassword')
        Account.objects.create(UserID=user.id,Name='testuser',Email='test@example.com',Password='testpassword')
        self.client.login(username='testuser', password='testpassword')
        data = {"date": "2023-10-22","workStatus": False,"stations": [{"id": 3,"datetime": "2023-10-22T17:30"},{"id": 2,"datetime": "2023-10-22T18:10"}],"carInfo": {"color": "紅色","capacity": 4,"licensePlateNumber": "ABC-1234"}}
        response = self.client.post(url1,json.dumps(data),content_type='application/json')
        self.assertEqual(response.status_code, SUCESS_WITH_DATA)
        decode_content = json.loads(response.content.decode("unicode_escape"))
        id = decode_content['id']
        data = {"datetime": "2023-10-22T10:30"}
        url2 = reverse('add_delete_stop_station',args=[id,1])
        response = self.client.put(url2,json.dumps(data),content_type='application/json')
        decode_content = json.loads(response.content.decode("unicode_escape"))
        self.assertEqual(response.status_code,SUCESS_WITH_DATA)
        self.assertEqual(decode_content['id'],1)
        self.assertEqual(decode_content['name'],Station.objects.get(StationID=1).StationName)
        self.assertEqual(decode_content['datetime'],data['datetime'])
        self.assertEqual(decode_content['on'],[])
        self.assertEqual(decode_content['off'],[])
    
    def test_delete_stop_station(self):
        url1 = reverse('add_route')
        user = User.objects.create_user('testuser', 'test@example.com', 'testpassword')
        Account.objects.create(UserID=user.id,Name='testuser',Email='test@example.com',Password='testpassword')
        self.client.login(username='testuser', password='testpassword')
        data = {"date": "2023-10-22","workStatus": False,"stations": [{"id": 3,"datetime": "2023-10-22T17:30"},{"id": 1,"datetime": "2023-10-22T17:50"},{"id": 2,"datetime": "2023-10-22T18:10"}],"carInfo": {"color": "紅色","capacity": 4,"licensePlateNumber": "ABC-1234"}}
        response = self.client.post(url1,json.dumps(data),content_type='application/json')
        self.assertEqual(response.status_code, SUCESS_WITH_DATA)
        decode_content = json.loads(response.content.decode("unicode_escape"))
        id = decode_content['id']
        url2 = reverse('add_delete_stop_station',args=[id,1])
        response = self.client.delete(url2,json.dumps(data),content_type='application/json')
        self.assertEqual(response.status_code,SUCCESS_NO_DATA)
        station_ids_to_check = [2, 3]
        existing_station_ids = set(RouteStation.objects.filter(RouteID=id).values_list('StationID', flat=True))
        self.assertEqual(set(station_ids_to_check) == existing_station_ids, True)

    def test_myinfo(self):
        url = reverse('myinfo')
        user = User.objects.create_user('testuser', 'test@example.com', 'testpassword')
        Account.objects.create(UserID=user.id,Name='testuser',Email='test@example.com',Password='testpassword',Avatar="https://example.com/avatar.png",Phone="0912123456")
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(url,content_type='application/json')
        decode_content = json.loads(response.content.decode("unicode_escape"))
        self.assertEqual(response.status_code,SUCESS_WITH_DATA)
    
    def test_get_route(self):
        url1 = reverse('add_route')
        user = User.objects.create_user('testuser', 'test@example.com', 'testpassword')
        Account.objects.create(UserID=user.id,Name='John James',Email='test@example.com',Password='testpassword',Phone='0928123456',Avatar="https://example.com/avatar.png")
        self.client.login(username='testuser', password='testpassword')
        data = {"date": "2023-10-22","workStatus": False,"stations": [{"id": 3,"datetime": "2023-10-22T17:30"},{"id": 1,"datetime": "2023-10-22T17:50"},{"id": 2,"datetime": "2023-10-22T18:10"}],"carInfo": {"color": "紅色","capacity": 4,"licensePlateNumber": "ABC-1234"}}
        response = self.client.post(url1,json.dumps(data),content_type='application/json')
        self.assertEqual(response.status_code, SUCESS_WITH_DATA)
        decode_content = json.loads(response.content.decode("unicode_escape"))

        user = User.objects.create_user('testuser2', 'test2@example.com', 'testpassword')
        Account.objects.create(UserID=user.id,Name='Bill Gates',Email='test2@example.com',Password='testpassword',Phone='0982104928')
        self.client.login(username='testuser2', password='testpassword')
        RoutePassenger.objects.create(PassengerID=user.id,RouteID=decode_content['id'],On=3,Off=2)
        url2 = reverse('get_delete_route',args=[decode_content['id']])
        response = self.client.get(url2,content_type='application/json')
        self.assertEqual(response.status_code,SUCESS_WITH_DATA)
    
    def test_get_stop_station(self):
        url1 = reverse('add_route')
        user = User.objects.create_user('testuser', 'test@example.com', 'testpassword')
        Account.objects.create(UserID=user.id,Name='John James',Email='test@example.com',Password='testpassword',Phone='0928123456',Avatar="https://example.com/avatar.png")
        self.client.login(username='testuser', password='testpassword')
        data = {"date": "2023-10-22","workStatus": False,"stations": [{"id": 3,"datetime": "2023-10-22T17:30"},{"id": 1,"datetime": "2023-10-22T17:50"},{"id": 2,"datetime": "2023-10-22T18:10"}],"carInfo": {"color": "紅色","capacity": 4,"licensePlateNumber": "ABC-1234"}}
        response = self.client.post(url1,json.dumps(data),content_type='application/json')
        self.assertEqual(response.status_code, SUCESS_WITH_DATA)
        decode_content = json.loads(response.content.decode("unicode_escape"))
        route_id = decode_content['id']

        user = User.objects.create_user('testuser2', 'test2@example.com', 'testpassword')
        Account.objects.create(UserID=user.id,Name='Bill Gates',Email='test2@example.com',Password='testpassword',Phone='0982104928')
        self.client.login(username='testuser2', password='testpassword')
        RoutePassenger.objects.create(PassengerID=user.id,RouteID=decode_content['id'],On=3,Off=2)
        url2 = reverse('get_stop_station',args=[route_id])
        response = self.client.get(url2,content_type='application/json')
        self.assertEqual(response.status_code,SUCESS_WITH_DATA)
        decode_content = json.loads(response.content.decode("unicode_escape"))