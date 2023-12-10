from uber_app.models import *
from django.http import JsonResponse
from uber_app.views.base import *
from django.utils.decorators import method_decorator
from datetime import date, datetime
from django.db import transaction
from django.db.models import *
import copy

class RoutesView(ProtectedView):
    def search(self, request, n):
        pass
    def driver(self, user, n, history=False):
        query = Route.objects.filter(Driver=user.UserID)
        if history:
            query = query.exclude(RouteStations__Time__gte=datetime.now())
        else:
            query = query.filter(RouteStations__Time__gte=datetime.now())
        query = query.distinct()
        query = query.order_by(["Date", "-Work_Status"])
        if n > 0:
            result = list(query[:n])
        return JsonResponse(result, safe=False)

    def passenger(self, user, n, history=False):
        pass

    def get(self, request):
        try:
            mode = request.GET["mode"]
            if mode not in ["search", "driver-future", "driver-history",
                            "passenger-future", "passenger-history"]:
                raise ValueError()
            n = int(request.GET.get("n", 0))
        except (KeyError, ValueError):
            return BadRequestResponse()
        if mode == "driver-future":
            return self.driver(request.user, n, False)
        elif mode == "driver-history":
            return self.driver(request.user, n, True)
        elif mode == "passenger-future":
            return self.passenger(request.user, n, False)
        elif mode == "passenger-history":
            return self.passenger(request.user, n, True)
        else:
            return self.search(request, n)

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
                                 Driver=request.user.UserID,
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

class RoutesIDStationsView(ProtectedView):
    def get(self, id):
        try:
            route = Route.objects.exclude(Status="deleted").get(pk=id)
        except Route.DoesNotExist:
            return ErrorResponse(f"找不到 ID 為 {id} 的行程", 404)
        return JsonResponse(route.to_dict()['stations'], safe=False)

class RoutesIDStationsIDView(ProtectedView):
    def get(self, id, station_id):
        pass
    def put(self, id, station_id):
        pass
    def delete(self, id, station_id):
        pass
