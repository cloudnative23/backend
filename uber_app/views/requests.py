from uber_app.models import *
from django.http import JsonResponse
from uber_app.views.base import *
from django.utils.decorators import method_decorator
from datetime import date, datetime
from django.db import transaction
from django.db import models
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
        try:
            # 前端會進行 Filter
            query.order_by("Date", "-Work_Status")
            result = [_request.to_dict() for _request in query]
            return JsonResponse(result, safe=False)
        except:
            raise HttpResponseException(BadRequestResponse())

    # Post New Request
    @transaction.atomic
    @method_decorator(json_api)
    def post(self, request):
        body = copy.deepcopy(request.json)
        try:
            # Check workStatus
            if not isinstance(body["workStatus"], bool):
                raise ValueError()
            # Check CarInfo
            if not isinstance(body["route"], int):
                raise ValueError()
            #Check on-station
            if not isinstance(body["on-station"], int):
                raise ValueError()
            #Check off-station
            if not isinstance(body["off-station"], int):
                raise ValueError()
            try:
                on = Station.objects.get(StationID=body["on-station"], Enable=True)
                off = Station.objects.get(StationID=body["off-station"], Enable=True)
            except Station.DoesNotExist:
                raise HttpResponseException(ErrorResponse(f"找不到 ID 為 {id} 的站點", 404))
            try:
                route=Route.objects.get(pk=body["route"])
            except Route.DoesNotExist:
                raise HttpResponseException(ErrorResponse(f"找不到 ID 為 {id} 的路線", 404))
            if route.update_status():
                route.save()
            if route.Status != "available":
                raise HttpResponseException(ErrorResponse(f"此路線不再接受乘客", 403))
            _request=Request()
            _request.Passenger=request.user
            _request.Route=Route.objects.get(pk=body["route"])
            _request.Work_Status=body["workStatus"]
            _request.On=on
            _request.Off=off
            _request.Status="new"
            _request.Date=date.today()
            _request.save()
            return JsonResponse(_request.to_dict())
        except (KeyError, ValueError):
            raise HttpResponseException(BadRequestResponse())

class RequestsIDView(ProtectedView):
    def get(self,request,id):
        try:
            _request = Request.objects.get(pk=id)
        except Request.DoesNotExist:
            raise HttpResponseException(ErrorResponse(f"找不到 ID 為 {id} 請求", 404))
        return JsonResponse(_request.to_dict())

    @transaction.atomic
    def delete(self,request,id):
        try:
            _request = Request.objects.get(pk=id)
            if _request.Passenger.UserID != request.user.UserID:
                raise HttpResponseException(ErrorResponse(f"您沒有權限刪除此請求", 403))
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
        if _request.Status != "new":
            raise HttpResponseException(ErrorResponse("此請求已失效", 400))
        if _request.Route.Driver.UserID != request.user.UserID:
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
        return HttpResponseNoContent()

class RequestsIDDenyView(ProtectedView):
    @transaction.atomic
    def put(self,request,id):
        try:
            _request = Request.objects.get(pk=id)
            if _request.Status != "new":
                raise HttpResponseException(ErrorResponse("此請求已失效", 400))
            if _request.Route.Driver.UserID != request.user.UserID:
                raise HttpResponseException(ErrorResponse("您沒有權限接受此請求", 403))
            _request.Status = "denied"
            _request.save()
            return HttpResponseNoContent()
        except Request.DoesNotExist:
            raise HttpResponseException(ErrorResponse(f"找不到 ID 為 {id} 的請求", 404))
