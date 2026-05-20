from django.urls import path, include
from rest_framework.routers import DefaultRouter

from client_registry.views import *
from core import views

router = DefaultRouter()

app_name = 'client'

urlpatterns = [
     path('', include(router.urls)),
     path("request-code/", RegistrySendCodeView.as_view(), name="request_code"),
     path("registry-code/", RegistryAppointmentsView.as_view(), name="registry_code"),
     path("tv-dashboard/", TVDashboardAPIView.as_view(), name="tv_dashboard"),
]