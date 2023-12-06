from uber_app.models import *
from django.http import JsonResponse
from uber_app.views.base import *
from django.utils.decorators import method_decorator
from datetime import date, datetime
from django.db import transaction
from django.db import models
import copy

class RoutesView(ProtectedView):
    def get(self, request):
        try:
            mode = request.GET["mode"]
            if mode not in ["available", "attending", "driving"]:
                raise ValueError()
            order_by = request.GET.get("order-by", "datetime")
            if order_by not in ["datetime", "similiarity"]:
                raise ValueError()
        except (KeyError, ValueError):
            return BadRequestResponse()
        query = Route.objects.exclude(Status="deleted")
        # Add filters
        if _from := request.GET.get("from", None):
            _from = datetime_from_str(_from)
            if isinstance(_from, date):
                query = query.filter(RouteStations__Time__date__gte=_from)
            else:
                query = query.filter(RouteStations__Time__gte=_from)
        if _to := request.GET.get("to", None):
            _to = datetime_from_str(_to)
            if isinstance(_to, date):
                query = query.filter(RouteStations__Time__date__gte=_to)
            else:
                query = query.filter(RouteStations__Time__gte=_to)
        if mode == "attending":
            query.filter(Passengers__UserID=request.user.UserID)
        elif mode == "driving":
            query.filter(Driver__UserID=request.user.UserID)
        query = query.distinct("RouteID")
        query = query.prefetch_related("RoutePassengers", "Passengers")
        result = []
        for route in query:
            if route.update_status():
                route.save()
            result.append(route.to_dict(uid=request.user.UserID))
        return JsonResponse(result, safe=False)

    @transaction.atomic
    @method_decorator(json_api)
    def post(self, request):
        body = copy.deepcopy(request.json)
        try:
            body["date"] = date.fromisoformat(body["date"])
            if body["date"] < date.today():
                raise HttpResponseException(ErrorResponse("新建立的行程不得為過去行程。", 400))
            # Check stations
            if not isinstance(body["stations"], list):
                raise ValueError()
            for station in body["stations"]:
                if not isinstance(station["id"], int):
                    raise ValueError()
                station["datetime"] = datetime_from_str(station["datetime"])
                if station["datetime"] < datetime.now():
                    raise HttpResponseException(ErrorResponse("站點時間不得為過去時間。", 400))
                if station["datetime"].date() != body["date"]:
                    raise HttpResponseException(ErrorResponse("站點時間的日期與行程日期不符", 400))
            # Check workStatus
            if not isinstance(body["workStatus"], bool):
                raise ValueError()
            # Check CarInfo
            if not isinstance(body["carInfo"]["capacity"], int):
                raise ValueError()
            # Check conflict
            if Route.objects.exclude(Status="deleted").filter(
                                 Driver__UserID=request.user.UserID,
                                 Date=body["date"],
                                 Work_Status=body["workStatus"]).count():
                workStatus = "上班" if body["workStatus"] else "下班" 
                raise HttpResponseException(ErrorResponse(f"{body['date']} 已有{workStatus}的行程", 400))
            route = Route()
            route.Date = body["date"]
            route.Work_Status = body["workStatus"]
            route.Status = "available"
            route.Driver = request.user
            route.Car_Model = body["carInfo"]["model"]
            route.Car_Capacity = body["carInfo"]["capacity"]
            route.Car_Color = body["carInfo"]["color"]
            route.LicensePlateNumber = body["carInfo"]["licensePlateNumber"]
            route.save()
            # Create Stations
            try:
                for station in body["stations"]:
                    route.RouteStations.create(Route=route,
                                               Station=Station.objects
                                                   .filter(Enable=True)
                                                   .get(pk=station["id"]),
                                               Time=station["datetime"])
            except Station.DoesNotExist:
                raise HttpResponseException(ErrorResponse(f"找不到編號為 {station['id']} 的站點", 400))
        except (KeyError, ValueError):
            raise HttpResponseException(BadRequestResponse())
        return JsonResponse(route.to_dict(uid=request.user.UserID))

class RoutesIDView(ProtectedView):
    def get(self, request, id):
        try:
            route = Route.objects.exclude(Status="deleted").get(pk=id)
            if route.update_status():
                route.save()
        except Route.DoesNotExist:
            return ErrorResponse(f"找不到 ID 為 {id} 的行程", 404)
        return JsonResponse(route.to_dict(uid=request.user.UserID))

    @transaction.atomic
    def delete(self, request, id):
        try:
            route = Route.objects.exclude(Status="deleted").get(pk=id)
            if route.Driver.UserID != request.user.UserID:
                raise HttpResponseException(ErrorResponse("您沒有權限刪除此行程", 403))
            if route.RoutePassengers.count() > 0:
                raise HttpResponseException(ErrorResponse("此行程已有乘客搭乘，不能刪除", 403))
            route.Status = "deleted"
            route.save()
        except Route.DoesNotExist:
            raise HttpResponseException(ErrorResponse(f"找不到 ID 為 {id} 的行程", 404))
        return HttpResponseNoContent()
