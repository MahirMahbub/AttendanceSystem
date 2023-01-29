from django.urls import include, path

from .views import *
from rest_framework.routers import DefaultRouter

app_name = "face_portal"
router = DefaultRouter()
urlpatterns = [
    path("", include(router.urls))
]