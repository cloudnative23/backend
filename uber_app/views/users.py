from uber_app.models import Account
from django.http import HttpResponse, JsonResponse
from uber_app.views.base import *
from django.contrib.auth.hashers import check_password
from django.utils.decorators import method_decorator

# /me
class UsersView(ProtectedView):
    def get(self, request):
        user: Account = request.user
        return JsonResponse({
            'id': user.UserID,
            'name': user.Name,
            'avatar': user.Avatar,
            'email': user.Email,
            'phone': user.Phone
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
