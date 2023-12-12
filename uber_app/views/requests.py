from uber_app.models import *
from django.http import JsonResponse
from uber_app.views.base import *
from django.utils.decorators import method_decorator
from datetime import date, datetime
from django.db import transaction
from django.db import models
from django.db.models import Q
import copy

# /requests
class RequestsView(ProtectedView):
    # Get All Requests
    def get(self, request):
        query = Request.objects
        try:
            mode = request.GET["mode"]
            if mode != "available" and mode != "me":
                raise ValueError()
        except (KeyError, ValueError):
            return BadRequestResponse()
        if mode == "me":
            query = query.filter(Passenger=request.user.UserID)
        else:
            query = query.filter(Route__Driver=request.user.UserID)
        # 前端會進行 Filter
        query = query.order_by("-Timestamp")
        result = []
        for _request in query:
            if _request.Route.update_status():
                _request.Route.save()
            if _request.update_status():
                _request.save()
            result.append(_request.to_dict())
        return JsonResponse(result, safe=False)

    # Post New Request
    @transaction.atomic
    @method_decorator(json_api)
    def post(self, request):
        body = copy.deepcopy(request.json)
        try:
            if not isinstance(body["workStatus"], bool):
                raise ValueError()
            if not isinstance(body["route"], int):
                raise ValueError()
            if not isinstance(body["on-station"], int):
                raise ValueError()
            if not isinstance(body["off-station"], int):
                raise ValueError()
            try:
                route=Route.objects.get(pk=body["route"])
            except Route.DoesNotExist:
                raise HttpResponseException(ErrorResponse(f"找不到 ID 為 {id} 的路線", 404))
            try:
                on = route.RouteStations.exclude(Status="deleted").get(Station=body["on-station"])
                off = route.RouteStations.exclude(Status="deleted").get(Station=body["off-station"])
            except RouteStation.DoesNotExist:
                raise HttpResponseException(ErrorResponse(f"停靠站 {id} 不在路線上", 404))
            if off.Time < on.Time:
                raise HttpResponseException(ErrorResponse("上車站點的停靠時間為下車站點後面", 400))
            if Request.objects.filter(Q(Status="new") | Q(Status="accepted")).filter(
                On=on, Off=off, Route=route, Passenger=request.user.UserID).exists():
                raise HttpResponseException(ErrorResponse("已提出相同的請求，請求不能重複", 404))
            if route.update_status():
                route.save()
            if route.Status != "available":
                raise HttpResponseException(ErrorResponse("此路線不再接受乘客", 403))
            _request=Request()
            _request.Passenger=request.user
            _request.Route=Route.objects.get(pk=body["route"])
            _request.Work_Status=body["workStatus"]
            _request.On=on
            _request.Off=off
            _request.Status="new"
            _request.Date=date.today()
            _request.save()
            notification = Notification()
            notification.Request = _request
            notification.User_id = route.Driver_id
            notification.Category = "request"
            notification.For = "driver"
            notification.save()
            return JsonResponse(_request.to_dict())
        except (KeyError, ValueError):
            raise HttpResponseException(BadRequestResponse())

class RequestsIDView(ProtectedView):
    def get(self,request,id):
        try:
            _request = Request.objects.get(pk=id)
            if _request.Route.update_status():
                _request.Route.save()
            if _request.update_status():
                _request.save()
        except Request.DoesNotExist:
            raise HttpResponseException(ErrorResponse(f"找不到 ID 為 {id} 請求", 404))
        return JsonResponse(_request.to_dict())

    @transaction.atomic
    def delete(self,request,id):
        try:
            _request = Request.objects.get(pk=id)
            if _request.Passenger.UserID != request.user.UserID:
                raise HttpResponseException(ErrorResponse(f"您沒有權限刪除此請求", 403))
            if _request.Route.update_status():
                _request.Route.save()
            if _request.update_status():
                _request.save()
            if _request.Status != "new":
                raise HttpResponseException(ErrorResponse(f"此請求已失效，無法刪除", 403))
            _request.Status = "deleted"
            _request.save()
        except Request.DoesNotExist:
            raise HttpResponseException(ErrorResponse(f"找不到 ID 為 {id} 的請求", 404))
        return HttpResponseNoContent()

class RequestsIDAcceptView(ProtectedView):
    @transaction.atomic
    def put(self,request,id):
        try:
            _request = Request.objects.get(pk=id)
        except Request.DoesNotExist:
            raise HttpResponseException(ErrorResponse(f"找不到 ID 為 {id} 的請求", 404))
        if _request.Route.update_status():
            _request.Route.save()
        if _request.update_status():
            _request.save()
        if _request.Status != "new":
            raise HttpResponseException(ErrorResponse("此請求已失效", 400))
        if _request.Route.Driver_id != request.user.UserID:
            raise HttpResponseException(ErrorResponse("您沒有權限接受此請求", 403))
        _RoutePassenger = RoutePassenger()
        _RoutePassenger.Passenger = _request.Passenger
        _RoutePassenger.Route = _request.Route
        _RoutePassenger.Request = _request
        _RoutePassenger.On = _request.On
        _RoutePassenger.Off = _request.Off
        _RoutePassenger.Work_Status = _request.Work_Status
        _RoutePassenger.save()
        _request.Status = "accepted"
        _request.save()
        notification = Notification()
        notification.Request = _request
        notification.Category = "request-accepted"
        notification.User = _request.Passenger
        notification.For = "passenger"
        notification.save()
        # check whether the route is full or not
        route = _request.Route
        route.refresh_from_db()
        if route.Passengers.count() >= route.Car_Capacity:
            # Set route as full
            route.Status="full"
            route.save()
            # Cancel other requests
            for _request in route.requests.filter(Status="new"):
                _request.Status="canceled"
                _request.save()
                notification = Notification()
                notification.Request = _request
                notification.Category = "request-canceled"
                notification.User_id = _request.Passenger_id
                notification.For = "passenger"
                notification.save()
        return HttpResponseNoContent()

class RequestsIDDenyView(ProtectedView):
    @transaction.atomic
    def put(self,request,id):
        try:
            _request = Request.objects.get(pk=id)
            if _request.Route.update_status():
                _request.Route.save()
            if _request.update_status():
                _request.save()
            if _request.Status != "new":
                raise HttpResponseException(ErrorResponse("此請求已失效", 400))
            if _request.Route.Driver.UserID != request.user.UserID:
                raise HttpResponseException(ErrorResponse("您沒有權限接受此請求", 403))
            _request.Status = "denied"
            _request.save()
            notification = Notification()
            notification.Request = _request
            notification.Category = "request-denied"
            notification.User_id = _request.Passenger_id
            notification.For = "passenger"
            notification.save()
            return HttpResponseNoContent()
        except Request.DoesNotExist:
            raise HttpResponseException(ErrorResponse(f"找不到 ID 為 {id} 的請求", 404))
