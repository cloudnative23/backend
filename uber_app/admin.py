from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(Account)
admin.site.register(Request)
admin.site.register(Route)
admin.site.register(RoutePassenger)
admin.site.register(RouteStation)
admin.site.register(Station)
admin.site.register(RouteCar)
