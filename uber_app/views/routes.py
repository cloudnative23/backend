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
        try:
            on_station = int(request.GET["on-station"])
            off_station = int(request.GET["off-station"])
            on_datetime = datetime.fromisoformat(request.GET["on-datetime"])
            off_datetime = datetime.fromisoformat(request.GET["off-datetime"])
        except (KeyError, ValueError):
            return BadRequestResponse()
        if on_datetime.date() != off_datetime.date():
            return ErrorResponse("上車和下車的日期不一致（目前不支援跨日乘車）", 400)
        date = on_datetime.date()
        query = Route.objects.filter(Date=date, Status="available").annotate(
            on_station=FilteredRelation("RouteStations",
                                        condition=Q(RouteStations__Station_id=on_station)),
            off_station=FilteredRelation("RouteStations",
                                         condition=Q(RouteStations__Station_id=off_station))
        ).filter(on_station__isnull=False, off_station__isnull=False,
                 on_station__Time__lt=F("off_station__Time"),
                 on_station__Time__gte=on_datetime,
                 off_station__Time__lte=off_datetime).annotate(
            similiarity=(F("on_station__Time") - on_datetime) +
                        (off_datetime - F("off_station__Time"))
        ).order_by("similiarity")
        if n > 0:
            query = query[:n]
        result = []
        for route in query:
            if route.update_status():
                route.save()
            if route.Status == "available":
                result.append(route.to_dict())
        return JsonResponse(result, safe=False)

    def driver(self, user, n, history=False):
        query = Route.objects.filter(Driver=user.UserID).exclude(Status="deleted")
        now = datetime.now()
        if history:
            query = query.exclude(RouteStations__Time__gte=now)
        else:
            query = query.filter(RouteStations__Time__gte=now)
        query = query.order_by("Date", "-Work_Status")
        if history:
            query.reverse()
        if n > 0:
            query = query[:n]
        result = []
        for route in query:
            if route.update_status():
                route.save()
            result.append(route.to_dict())
        return JsonResponse(result, safe=False)

    def passenger(self, user, n, history=False):
        now = datetime.now()
        query = Route.objects.exclude(Status="deleted").annotate(
            UserPassenger=FilteredRelation(
                "RoutePassengers",
                condition=Q(RoutePassengers__Passenger_id=user.UserID),
            )
        ).filter(UserPassenger__isnull=False)
        condition = Q(UserPassenger__Off__Time__gte=now)
        if history:
            query = query.exclude(condition)
        else:
            query = query.filter(condition)
        query.order_by("Date", "-UserPassenger__Work_Status")
        if history:
            query.reverse()
        if n > 0:
            query = query[:n]
        result = []
        for route in query:
            if route.update_status():
                route.save()
            result.append(route.to_dict())
        return JsonResponse(result, safe=False)

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
            # TODO: cancel all requests
            route.Status = "deleted"
            route.save()
        except Route.DoesNotExist:
            raise HttpResponseException(ErrorResponse(f"找不到 ID 為 {id} 的行程", 404))
        return HttpResponseNoContent()

class RoutesIDStationsView(ProtectedView):
    def get(self, request, id):
        try:
            route = Route.objects.exclude(Status="deleted").get(pk=id)
        except Route.DoesNotExist:
            return ErrorResponse(f"找不到 ID 為 {id} 的行程", 404)
        return JsonResponse(route.to_dict()['stations'], safe=False)

class RoutesIDStationsIDView(ProtectedView):
    @transaction.atomic
    def get(self, request, id, station_id):
        if not Route.objects.exclude(Status="deleted").filter(pk=id).exists():
            return ErrorResponse(f"找不到 ID 為 {id} 的行程", 404)
        try:
            route_station = RouteStation.objects.get(Route=id, Station=station_id)
        except RouteStation.DoesNotExist:
            return ErrorResponse("在行程中找不到站點", 403)
        return JsonResponse(route_station.to_dict())

    @transaction.atomic
    @method_decorator(json_api)
    def put(self, request, id, station_id):
        try:
            route = Route.objects.exclude(Status="deleted").get(pk=id)
            if route.update_status():
                route.save()
        except Route.DoesNotExist:
            return ErrorResponse(f"找不到 ID 為 {id} 的行程", 404)
        if route.Driver_id != request.user.UserID:
            return ErrorResponse("您沒有權限修改此行程的停靠站", 403)
        try:
            route_station = route.RouteStations.exclude(Status="deleted").get(Station=station_id)
            if route_station.OnPassengers.exists() or route_station.OffPassengers.exists():
                return ErrorResponse("此停靠站已有上下車乘客，無法編輯")
        except RouteStation.DoesNotExist:
            route_station = RouteStation()
            route_station.Route=route
        try:
            route_station.Station=Station.objects.get(pk=station_id)
            route_station.Time=datetime.fromisoformat(request.json["datetime"])
        except Station.DoesNotExist:
            return ErrorResponse(f"找不到 ID 為 {station_id} 的站點")
        except (KeyError, ValueError):
            return BadRequestResponse()
        route_station.save()
        # TODO: Cancel requests with this station
        return HttpResponseNoContent()

    @transaction.atomic
    def delete(self, request, id, station_id):
        try:
            route = Route.objects.exclude(Status="deleted").get(pk=id)
            if route.Driver_id != request.user.UserID:
                return ErrorResponse("您沒有權限修改此行程的停靠站", 403)
            route_station = route.RouteStations.exclude(Status="deleted").get(Station=station_id)
        except Route.DoesNotExist:
            return ErrorResponse(f"找不到 ID 為 {id} 的行程", 404)
        except RouteStation.DoesNotExist:
            return ErrorResponse("沒有指定的停靠站", 404)
        if route.Status not in ["available", "full"]:
            return ErrorResponse("此行程已過期", 403)
        if route_station.OnPassengers.exists() or route_station.OffPassengers.exists():
            return ErrorResponse("此停靠站已有上下車乘客，無法刪除", 403)
        route_station.Status = "deleted"
        route_station.save()
        # TODO: Cancel requests with this station
        return HttpResponseNoContent()
