from uber_app.models import Account, Request, Route
from django.http import JsonResponse
from uber_app.views.base import *
from django.contrib.auth.hashers import check_password, make_password
from django.utils.decorators import method_decorator
from django.core.validators import validate_email
from django.db import IntegrityError

# /register
class RegisterView(ProtectedView):
    @method_decorator(json_api)
    def post(self, request):
        user = Account()
        try:
            user.Email = request.json["email"]
            user.Password = make_password(request.json["password"])
            user.Avatar = request.json["avatar"]
            user.Phone = request.json["phone"]
            user.Name = request.json["name"]
            user.save()
        except IntegrityError:
            return ErrorResponse("E-mail 已被使用")
        return JsonResponse(user.to_dict())

# /me
class UsersView(ProtectedView):
    def get(self, request):
        user: Account = request.user
        driver_req_count = Request.objects.filter(Status="new", Route__Driver=user.UserID).count()
        passenger_req_count = Request.objects.filter(Status="new", Passenger=user.UserID).count()
        return JsonResponse({
            'id': user.UserID,
            'name': user.Name,
            'avatar': user.Avatar,
            'email': user.Email,
            'phone': user.Phone,
            'notificationCount': {
                'driver': user.Driver_Notification_Count,
                'passenger': user.Passenger_Notification_Count
            },
            'requestCount':{
                'driver': driver_req_count,
                'passenger': passenger_req_count
            }
        })

class LoginView(BaseView):
    @method_decorator(json_api)
    def post(self, request):
        try:
            email = request.json['email']
            password = request.json['password']
        except KeyError:
            return BadRequestResponse()
        if not isinstance(email, str) or not isinstance(password, str):
            return BadRequestResponse()
        try:
            user = Account.objects.get(Email=email)
        except Account.DoesNotExist:
            return ErrorResponse("E-mail 錯誤", 403)
        if not check_password(password, user.Password):
            return ErrorResponse("密碼錯誤", 403)
        request.session['user'] = user.UserID
        return HttpResponseNoContent()

class LogoutView(ProtectedView):
    def post(self, request):
        request.session['user']=None
        request.session.clear()
        return HttpResponseNoContent()
