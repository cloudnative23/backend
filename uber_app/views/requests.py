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
            query = query.filter(Status="new")
            result = []
            #TODO 排序日期 上下班
            # Produce the response
            for _request in query:
                result.append(_request.to_dict())
            result = sorted(result,key=sort_by_date_and_status,reverse=True if body['order-mode'] == 'desc' else False)
            return JsonResponse(result, safe=False)
        except:
            raise HttpResponseException(BadRequestResponse())
    def sort_by_date_and_status(self,d):
        return (d['Date'], d['Work_Status'])

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
                on = Station.objects.get(StationID=body["on-station"], Enable=True)# not sure
                off = Station.objects.get(StationID=body["off-station"], Enable=True)# not sure
            except Station.DoesNotExist:
                raise HttpResponseException(ErrorResponse(f"找不到 ID 為 {id} 的站點。", 404))
            _request=Request()
            _request.Passenger=request.user
            _request.Route=Route.objects.get(pk=body["route"])
            _request.Work_Status=body["workStatus"]
            _request.On=on
            _request.Off=off
            _request.Status="new"
            _request.Date=date.today()
            _request.save()
            res = {}
            res['id'] = request.user.UserID
            res['status'] = "new"
            res['date'] = str(date.today())
            res['workStatus'] = body["workStatus"]
            return JsonResponse(_request.to_dict())
        except (KeyError, ValueError):
            raise HttpResponseException(BadRequestResponse())

class RequestsIDView(ProtectedView):
    @method_decorator(json_api)
    def get(self,request,id):
        body = copy.deepcopy(request.json)
        try:
            if not isinstance(body["id"], int):
                raise ValueError()
            try:
                _request = Request.objects.get(pk=id)
            except:
                raise HttpResponseException(ErrorResponse(f"找不到 ID 為 {id} 的Request。", 404))
            return JsonResponse(_request.to_dict())
        except:
            raise HttpResponseException(BadRequestResponse())

    @transaction.atomic
    @method_decorator(json_api)
    def delete(self,request,id):
        body = copy.deepcopy(request.json)
        try:
            if not isinstance(body["id"], int):
                raise ValueError()
            try:
                _request = Request.objects.get(pk=id)
            except:
                raise HttpResponseException(ErrorResponse(f"找不到 ID 為 {id} 的Request。", 404))
            if _request.Passenger != request.user.UserID:
                raise HttpResponseException(ErrorResponse(f"權限錯誤", 400))
            _request.Status = 'deleted'
            _request.save()
            return HttpResponseNoContent()
        except:
            raise HttpResponseException(BadRequestResponse())
    
class RequestsIDAcceptView(ProtectedView):
    @transaction.atomic
    @method_decorator(json_api)
    def put(self,request,id):
        body = copy.deepcopy(request.json)
        user_id = request.user.UserID
        try:
            if not isinstance(body["id"], int):
                raise ValueError()
            try:
                _request = Request.objects.get(pk=id)
            except:
                raise HttpResponseException(ErrorResponse(f"找不到 ID 為 {id} 的Request。", 404))
            try:
                _RoutePassenger = RoutePassenger()
                _RoutePassenger.Passenger = user_id
                _RoutePassenger.Route = _request.Route
                _RoutePassenger.Request = _request.RequestID
                _RoutePassenger.On = _request.On
                _RoutePassenger.Off = _request.Off
                _RoutePassenger.Work_Status = _request.Work_Status
                _RoutePassenger.save()
                _request.Status = "accept"
                _request.save()
                return HttpResponseNoContent()
            except:
                raise HttpResponseException(BadRequestResponse())
        except:
            raise HttpResponseException(BadRequestResponse())

class RequestsIDDenyView(ProtectedView):
    @transaction.atomic
    @method_decorator(json_api)
    def put(self,request,id):
        body = copy.deepcopy(request.json)
        try:
            if not isinstance(body["id"], int):
                raise ValueError()
            try:
                _request = Request.objects.get(pk=id)
                _request.Status = "deny"
                _request.save()
                return HttpResponseNoContent()
            except:
                raise HttpResponseException(ErrorResponse(f"找不到 ID 為 {id} 的Request。", 404))
        except:
            raise HttpResponseException(BadRequestResponse())