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
    path("me", UsersView.as_view()),
    path("login", LoginView.as_view()),
    path("logout", LogoutView.as_view()),
    path("stations", StationsView.as_view()),
    path("stations/<int:id>", StationsIdView.as_view()),
    path("routes", RoutesView.as_view()),
    path("routes/<int:id>", RoutesIDView.as_view()),
    path("requests", RequestsView.as_view()),
    path("requests/<int:id>", RequestsIDView.as_view()),
    path("requests/<int:id>/accept", RequestsIDAcceptView.as_view()),
    path("requests/<int:id>/deny", RequestsIDDenyView.as_view()),
    path("notifications", NotificationView.as_view()),
    path("notifications/read", NotificationReadView.as_view()),
    path("notifications/<int:id>", NotificationIDView.as_view()),
    path("notifications/<int:id>/read", NotificationIDReadView.as_view())
]
