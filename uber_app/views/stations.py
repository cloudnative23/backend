from uber_app.models import Station
from django.http import HttpResponse, JsonResponse
from uber_app.views.base import *
from django.contrib.auth.hashers import check_password
from django.utils.decorators import method_decorator

class StationView(ProtectedView):
    def get(self, request):
        stations = Station.objects.filter(Enable=True)
        result = []
        for station in stations:
            result.append({
                "id": station.StationID,
                "name": station.StationName
            })
        return JsonResponse(result, safe=False)

class StationIdView(ProtectedView):
    def get(self, request, id):
        try:
            station = Station.objects.get(StationID=id, Enable=True)
        except Station.DoesNotExist:
            return ErrorResponse(f"找不到 ID 為 {id} 的站點。", 404)
        return JsonResponse({
            "id": station.StationID,
            "name": station.StationName
        })
