from uber_app.models import Station
from django.http import JsonResponse
from uber_app.views.base import *

class StationsView(ProtectedView):
    def get(self, request):
        stations = Station.objects.filter(Enable=True)
        result = []
        for station in stations:
            result.append(station.to_dict())
        return JsonResponse(result, safe=False)

class StationsIdView(ProtectedView):
    def get(self, request, id):
        try:
            station = Station.objects.get(StationID=id, Enable=True)
        except Station.DoesNotExist:
            return ErrorResponse(f"找不到 ID 為 {id} 的站點。", 404)
        return JsonResponse(station.to_dict())
