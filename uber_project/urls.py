"""
URL configuration for uber_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from uber_app.views.users import *
from uber_app.views.stations import *
from uber_app.views.routes import *
from uber_app.views.requests import *
from uber_app.views.notifications import *

urlpatterns = [
    path("me", UsersView.as_view(),name = 'user_me'),
    path("login", LoginView.as_view(),name = 'user_login'),
    path("logout", LogoutView.as_view(),name = 'user_logout'),
    path("register", RegisterView.as_view(),name = 'user_register'),
    path("stations", StationsView.as_view(),name = 'all_stations'),
    path("stations/<int:id>", StationsIdView.as_view(),name = 'specific_station'),
    path("routes", RoutesView.as_view(),name = 'add_or_get_all_route'),
    path("routes/<int:id>", RoutesIDView.as_view(),name = 'get_or_delete_specific_route'),
    path("routes/<int:id>/stations", RoutesIDStationsView.as_view(),name = 'get_route_stop_station'),
    path("routes/<int:id>/stations/<int:station_id>", RoutesIDStationsIDView.as_view(),name = 'add_or_delete_route_stop_station'),
    path("requests", RequestsView.as_view(),name = 'add_or_get_all_request'),
    path("requests/<int:id>", RequestsIDView.as_view(),name = 'get_or_delete_specific_request'),
    path("requests/<int:id>/accept", RequestsIDAcceptView.as_view(),name = 'accept_request'),
    path("requests/<int:id>/deny", RequestsIDDenyView.as_view(),name = 'deny_request'),
    path("notifications", NotificationView.as_view()),
    path("notifications/read", NotificationReadView.as_view()),
    path("notifications/<int:id>", NotificationIDView.as_view()),
    path("notifications/<int:id>/read", NotificationIDReadView.as_view())
]
