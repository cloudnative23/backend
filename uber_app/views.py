from django.shortcuts import render
from django.http import *
import json
from .models import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.sessions.models import Session
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.utils import *
from django.contrib.sessions.exceptions import *
from django.db.transaction import *

# Create your views here.
ERROR_PARA = 400
NOT_LOGIN = 401
NOT_FOUND = 404
PERMISSION_ERROR = 403
SUCCESS_NO_DATA = 204
SUCESS_WITH_DATA = 200
def login_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data['email']
            password = data['password']
            if email == "" or password == "":
                return JsonResponse({'message': '帳號或密碼為空'},status=ERROR_PARA)
            user = authenticate(request,username = email, password = password)
            if user is not None:
                login(request, user)
                return HttpResponse(status=SUCCESS_NO_DATA,content_type='application/json')
            else:
                return JsonResponse({'message': '無此使用者'}, status=NOT_FOUND)
        except:
            return JsonResponse({'message': 'Json讀取失敗'},status=ERROR_PARA)
    return JsonResponse({'message': '錯誤要求方法'}, status=ERROR_PARA)


def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        return HttpResponse(status = SUCCESS_NO_DATA,content_type='application/json')
    else:
        return JsonResponse({"message":"未登入"},status=NOT_LOGIN)

def station_detail_view(request,station_id):
    if request.user.is_authenticated:
        if request.method == 'GET':
            try:
                obj = Station.objects.get(pk=station_id)
                data = {'id':obj.StationID,'name':obj.StationName}
                return JsonResponse(data, status=SUCESS_WITH_DATA)
            except:
                return JsonResponse({'message': '找不到此站點'}, status=NOT_FOUND)
        else:
            return JsonResponse({'message': '錯誤要求方法'}, status=ERROR_PARA)
    else:
        return JsonResponse({"message":"未登入"},status=NOT_LOGIN)

def station_list_view(request):
    if request.user.is_authenticated:
        if request.method == 'GET':
            try:
                stations = Station.objects.order_by('StationID').values('StationID', 'StationName')
                stations_list = list(stations)
                res = []
                for data in stations_list:
                    id = data['StationID']
                    name = data['StationName']
                    res.append({'id':id,'name':name})
                return JsonResponse(res,status=SUCESS_WITH_DATA,safe=False)
            except:
                return JsonResponse([], status=SUCESS_WITH_DATA,safe=False)
        else:
            return JsonResponse({'message': '錯誤要求方法'}, status=ERROR_PARA)
    else:
        return JsonResponse({"message":"未登入"},status=NOT_LOGIN)

def add_route(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            try:
                user_id = request.user.id
                data = json.loads(request.body)
                time = data['date']
                parsed_time = datetime.strptime(time, '%Y-%m-%d').date()
                workstatus = data['workStatus']
                carInfo = data['carInfo']
                stations = data['stations']
                res_stations = []
                if len(stations) == 0 or len(carInfo) == 0:
                    return JsonResponse({'message': '資料缺失'},status=ERROR_PARA)               
                try:
                    route = Route.objects.create(DriverID=user_id,Time=parsed_time,Work_Status=workstatus)
                    route_id = route.RouteID
                    RouteCar.objects.create(RouteID=route_id,Color=carInfo['color'],Capacity=carInfo['capacity'],LicensePlateNumber=carInfo['licensePlateNumber'])
                    for station in stations:
                        obj = Station.objects.get(pk=station['id'])
                        RouteStation.objects.create(RouteID=route_id,StationID=station['id'],Time=timezone.make_aware(datetime.strptime(station['datetime'], '%Y-%m-%dT%H:%M')))
                        append_data = {}
                        append_data['id'] = station['id']
                        append_data['name'] = obj.StationName
                        append_data['datetime'] = station['datetime']
                        append_data['on'] = []
                        append_data['off'] = []
                        res_stations.append(append_data)

                except:
                    JsonResponse({'message': '資料錯誤'},status=ERROR_PARA)
                #prepare response
                res = {}
                res['id'] = route_id
                res['date'] = time
                res['workStatus'] = workstatus
                res['status'] = Route.objects.get(pk=route_id).Status
                res['stations'] = res_stations
                res['carInfo'] = carInfo
                res['passengers'] = []
                person = Account.objects.get(UserID=user_id)
                res['driver'] = {'id':user_id,'name':person.Name,'avatar':person.Avatar,'phone':person.Phone}
                return JsonResponse(res,status=SUCESS_WITH_DATA)
            except:
                return JsonResponse({'message': 'Json讀取失敗'},status=ERROR_PARA)
        else:
            return JsonResponse({'message': '錯誤要求方法'}, status=ERROR_PARA)
    else:
        return JsonResponse({"message":"未登入"},status=NOT_LOGIN)

def delete_route_view(request,route_id):
    if request.user.is_authenticated:
        if request.method == 'DELETE':
            try:
                route = Route.objects.get(RouteID=route_id)
            except:
                return JsonResponse({'message': '找不到路線'},status=404)
            if route.DriverID != request.user.id:
                JsonResponse({'message': '權限錯誤'},status=PERMISSION_ERROR)
            try:
                Route.objects.filter(RouteID=route_id).delete()
                RouteCar.objects.filter(RouteID=route_id).delete()
                RouteStation.objects.filter(RouteID=route_id).delete()
                RoutePassenger.objects.filter(RouteID=route_id).delete()
            except:
                return JsonResponse({'message': '資料錯誤'},status=ERROR_PARA)
            return HttpResponse(status = SUCCESS_NO_DATA,content_type='application/json')
        else:
            return JsonResponse({'message': '錯誤要求方法'}, status=ERROR_PARA)
    else:
        return JsonResponse({"message":"未登入"},status=NOT_LOGIN)

def add_delete_stop_station(request,route_id,station_id):
    if request.user.is_authenticated:
        if request.method == 'PUT':
            return add_stop_station(request=request,route_id=route_id,station_id=station_id)
        elif request.method == 'DELETE':
            return delete_stop_station(request=request,route_id=route_id,station_id=station_id)
        else:
            return JsonResponse({'message': '錯誤要求方法'}, status=ERROR_PARA)
    else:
        return JsonResponse({"message":"未登入"},status=NOT_LOGIN)

def add_stop_station(request,route_id,station_id):
    try:
        user_id = request.user.id
        data = json.loads(request.body)
        time = timezone.make_aware(datetime.strptime(data['datetime'], '%Y-%m-%dT%H:%M'))
    except:
        return JsonResponse({'message': 'Json讀取失敗'},status=ERROR_PARA)
    route = Route.objects.filter(RouteID=route_id)[0]
    if not route:
        return JsonResponse({'message': '找不到物件'}, status=NOT_FOUND)
    if route.DriverID != user_id:
        JsonResponse({'message': '權限錯誤'},status=PERMISSION_ERROR)
    try:
        RouteStation.objects.create(RouteID=route_id,StationID=station_id,Time=time)
        station_name = Station.objects.get(StationID=station_id).StationName
        res = {}
        res['id'] = station_id
        res['name'] = station_name
        res['datetime'] = data['datetime']
        res['on'] = []
        res['off'] = []
        return JsonResponse(res,status=SUCESS_WITH_DATA)
    except:
        return JsonResponse({'message': '資料錯誤'},status=ERROR_PARA)

def delete_stop_station(request,route_id,station_id):
    try:
        user_id = request.user.id
    except:
        return JsonResponse({'message': 'Json讀取失敗'},status=ERROR_PARA)
    route = Route.objects.filter(RouteID=route_id)[0]
    if not route:
        return JsonResponse({'message': '找不到物件'}, status=NOT_FOUND)
    if route.DriverID != user_id:
        JsonResponse({'message': '權限錯誤'},status=PERMISSION_ERROR)
    route_station = RouteStation.objects.filter(RouteID=route_id,StationID=station_id)
    if route_station:
        route_station.delete()
    return HttpResponse(status=SUCCESS_NO_DATA,content_type='application/json')
