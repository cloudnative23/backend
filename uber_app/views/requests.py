from uber_app.models import *
from django.http import JsonResponse
from uber_app.views.base import *

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
            query = query.filter(Passenger__Passenger__UserID=request.user.UserID)
        else:
            query = query.filter(Route__Driver__UserID=request.user.UserID)
        # TODO: add other filters
        try:
            if _from := request.GET.get("from", None):
                _from = datetime_from_str(_from)
                query = query.filter(Time__ge=_from)
            if _to := request.GET.get("to", None):
                _to = datetime_from_str(_to)
                query = query.filter(Time__le=_to)
        except ValueError:
            return BadRequestResponse()
        query = query.filter(status="new")
        result = []
        # Produce the response
        for _request in query:
            result.append(_request.to_dict())
        return JsonResponse(result)

    # Post New Request
    def post(self, request):
        pass
