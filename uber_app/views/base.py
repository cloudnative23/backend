from django.views import View
from django.http import HttpResponse, JsonResponse
import json
from functools import wraps

class HttpResponseNoContent(HttpResponse):
    status_code = 204

class ErrorResponse(JsonResponse):
    def __init__(self, message="An error occurred", status=400):
        super().__init__({
            "message": message
        }, status=status)

class BadRequestResponse(ErrorResponse):
    def __init__(self):
        super().__init__("Bad request", 400)

class BaseView(View):
    def http_method_not_allowed(self, request, *args, **kwargs):
        return ErrorResponse("HTTP method not allowed", 400)

class ProtectedView(BaseView):
    def dispatch(self, request, *args, **kwargs):
        if not request.user:
            return ErrorResponse("您未登入，無法存取指定資源!", 401)
        return super().dispatch(request, *args, **kwargs)

def json_api(view_func):
    @wraps(view_func)
    def wrapper_view_func(request, *args, **kwargs):
        if request.content_type == 'application/json':
            if request.body:
                request.json = json.loads(request.body)
            else:
                request.json = None
        if not request.json:
            return BadRequestResponse()
        return view_func(request, *args, **kwargs)
    return wrapper_view_func