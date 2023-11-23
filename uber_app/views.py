from django.shortcuts import render
from django.http import *
import json
from .models import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.sessions.models import Session
from django.contrib.auth.decorators import login_required
# Create your views here.
ERROR_PARA = 400
NOT_LOGIN = 401
NOT_FOUND = 404
PERMISSION_ERROR = 403

def login_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data['email']
            password = data['password']
            user = authenticate(request,username = email, password = password)
            if user is not None:
                login(request, user)
                response = JsonResponse({'message': '登入成功'}, status=204)
                return response
            else:
                return JsonResponse({'error': '無此使用者'}, status=NOT_FOUND)
        except:
            return JsonResponse({'message': 'Json讀取失敗'},status=ERROR_PARA)
    return JsonResponse({'error': '錯誤要求方法'}, status=ERROR_PARA)


def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        return JsonResponse({"message":"登出成功"},status=204)
    else:
        return JsonResponse({"message":"未登入"},status=NOT_LOGIN)

def station_detail_view(request,station_id):
    if request.user.is_authenticated:
        if request.method == 'GET':
            try:
                obj = Station.objects.get(pk=station_id)
                data = {'id':obj.StationID,'name':obj.StationName}
                return JsonResponse(data, status=200)
            except:
                return JsonResponse({'error': '找不到此站點'}, status=NOT_FOUND)
        else:
            return JsonResponse({'error': '錯誤要求方法'}, status=ERROR_PARA)
    else:
        return JsonResponse("未登入",status=NOT_LOGIN)

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
                return JsonResponse(res,status=200,safe=False)
            except:
                return JsonResponse([], status=200)
        else:
            return JsonResponse({'error': '錯誤要求方法'}, status=ERROR_PARA)
    else:
        return JsonResponse("未登入",status=NOT_LOGIN)
