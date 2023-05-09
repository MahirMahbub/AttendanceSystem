from django.urls import include, path

from .views import *
from rest_framework.routers import DefaultRouter

from .views.employees import EmployeesDailyAttendanceViewSet

app_name = "card_portal"
router = DefaultRouter()
router.register(r"employees_attendance", EmployeesDailyAttendanceViewSet, basename="employees_attendance")
urlpatterns = [
    path("", include(router.urls)),
]

