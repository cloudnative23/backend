from uber_app.models import *
from django.http import JsonResponse
from uber_app.views.base import *
from django.utils.decorators import method_decorator
from datetime import date, datetime
from django.db import transaction
from django.db import models
import copy

class NotificationView(ProtectedView):
    def get(self, request):
        mode = request.GET.get("mode", "all")
        if mode not in ["all", "passenger", "driver"]:
            return BadRequestResponse()
        query = Notification.objects.filter(User=request.user.UserID)
        if mode == "passenger":
            query = query.filter(For="passenger")
        elif mode == "driver":
            query = query.filter(For="driver")
        query.order_by("Timestamp")
        notifications = query.all()
        result = [notification for notification in notifications]
        return JsonResponse(result, safe=False)

class NotificationReadView(ProtectedView):
    def put(self, request):
        mode = request.GET.get("mode", "all")
        if mode not in ["all", "passenger", "driver"]:
            return BadRequestResponse()
        user = Request.user
        if mode == "driver" or mode == "all":
            user.Driver_Notification_Count = 0
            user.save(update_fields=["Driver_Notification_Count"])
        if mode == "passenger" or mode == "all":
            user.Driver_Notification_Count = 0
            user.save(update_fields=["Driver_Notification_Count"])
        return HttpResponseNoContent()

class NotificationIDView(ProtectedView):
    def get(self, request, id):
        try:
            _notification = Notification.objects.get(pk=id)
            if _notification.User.UserID != request.user.UserID:
                return ErrorResponse("您存取讀取此通知的權限", 403)
        except Notification.DoesNotExist:
            return ErrorResponse(f"找不到 ID 為 {id} 的Notification。", 404)
        return JsonResponse(_notification.to_dict())

class NotificationIDReadView(ProtectedView):
    def put(self, request, id):
        try:
            notification = Notification.objects.get(pk=id)
            if notification.User.UserID != request.user.UserID:
                return ErrorResponse("您沒有存取此通知的權限", 403)
            notification.Read=True
            notification.save()
        except Notification.DoesNotExist:
            return ErrorResponse(f"找不到 ID 為 {id} 的Notification。", 404)
        return HttpResponseNoContent()
