from uber_app.models import *
from django.http import JsonResponse
from uber_app.views.base import *
from django.utils.decorators import method_decorator
from datetime import date, datetime
from django.db import transaction
from django.db import models
import copy

class NotificationView(ProtectedView):
    @transaction.atomic
    @method_decorator(json_api)
    def put(self):
        body = copy.deepcopy(request.json)
        try:
            if not isinstance(body["mode"], str):
                raise ValueError()
            mode = body['mode']
            if mode != "passenger" and mode != "driver":
                raise ValueError()
            _notification = Notification.objects.filter(User=request.user.UserID,For=mode)
            for d in _notification:
                d.Read = True
                d.save()
            return HttpResponseNoContent()
        except:
            raise HttpResponseException(BadRequestResponse())
    
    def get(self):
        body = copy.deepcopy(request.json)
        try:
            if not isinstance(body["mode"], str):
                raise ValueError()
            mode = body['mode']
            if mode != "passenger" and mode != "driver" and mode != "all":
                raise ValueError()
            if mode == "all":
                _notification = Notification.objects.filter(User=request.user.UserID)
            else:
                _notification = Notification.objects.filter(User=request.user.UserID,For=mode)
            
            return JsonResponse(list(_notification), safe=False)
        except:
            raise HttpResponseException(BadRequestResponse())


class NotificationIDView(ProtectedView):
    @transaction.atomic
    @method_decorator(json_api)
    def get(self,id):
        body = copy.deepcopy(request.json)
        try:
            if not isinstance(body["id"], int):
                raise ValueError()
            notification_id = body['id']
            try:
                _notification = Notification(pk=notification_id)
            except:
                raise HttpResponseException(ErrorResponse(f"找不到 ID 為 {id} 的Notification。", 404))
            return JsonResponse(_notification.to_dict())
        except:
            raise HttpResponseException(BadRequestResponse())
    
    @transaction.atomic
    @method_decorator(json_api)
    def put(self,id):
        body = copy.deepcopy(request.json)
        try:
            if not isinstance(body["id"], int):
                raise ValueError()
            notification_id = body['id']
            try:
                _notification = Notification(pk=notification_id)
                _notification.Read = True
                _notification.save()
            except:
                raise HttpResponseException(ErrorResponse(f"找不到 ID 為 {id} 的Notification。", 404))
            return HttpResponseNoContent()
        except:
            raise HttpResponseException(BadRequestResponse())