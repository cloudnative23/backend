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
            return JsonResponse({'message': 'json load fails'},status=403)
    return JsonResponse({'error': 'Invalid request method'}, status=403)


def logout_view(request):
    logout(request)
    return HttpResponse("Logout sucessful",status=204)

