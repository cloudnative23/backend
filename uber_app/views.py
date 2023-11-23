from django.shortcuts import render
from django.http import *
import json
from .models import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.sessions.models import Session
from django.contrib.auth.decorators import login_required
# Create your views here.


def login_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data['email']
            password = data['password']
            user = authenticate(request,username = email, password = password)
            if user is not None:
                login(request, user)
                response = JsonResponse({'message': 'Login successful'}, status=204)
                return response
            else:
                return JsonResponse({'error': 'Object not found'}, status=403)
        except:
            return JsonResponse({'message': 'json load fails'},status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=403)


def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        return JsonResponse({"message":"Logout sucessful"},status=204)
    else:
        return JsonResponse({"message":"Not authenticated user"},status=401)

def station_detail_view(request,station_id):
    if request.user.is_authenticated:
        if request.method == 'GET':
            try:
                obj = Station.objects.get(pk=station_id)
                data = {'id':obj.id,'name':obj.name}
                return JsonResponse(data, status=200)
            except:
                return JsonResponse({'error': 'Object not found'}, status=400)
        else:
            return JsonResponse({'error': 'Invalid request method'}, status=403)
    else:
        return JsonResponse("Not authenticated user",status=401)

def station_list_view(request):
    if request.user.is_authenticated:
        if request.method == 'GET':
            try:
                stations = Station.objects.order_by('id').values('id', 'name')
                stations_list = list(stations)
                return JsonResponse(stations_list,status=200,safe=False)
            except:
                return JsonResponse({'error': 'Object not found'}, status=400)
        else:
            return JsonResponse({'error': 'Invalid request method'}, status=403)
    else:
        return JsonResponse("Not authenticated user",status=401)
