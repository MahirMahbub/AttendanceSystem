from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, status
from rest_framework.response import Response

from apps.card_portal.models import EmployeesDailyAttendance
from apps.card_portal.serializers import EmployeesDailyAttendanceCreationSerializer, EmployeesDailyAttendanceSerializer, \
    MessageSerializer


class EmployeesDailyAttendanceViewSet(viewsets.ModelViewSet):
    serializer_class = EmployeesDailyAttendanceCreationSerializer
    queryset = EmployeesDailyAttendance.objects.all()
    http_method_names = ['post']

    @extend_schema(
        request=EmployeesDailyAttendanceCreationSerializer,
        responses={201: EmployeesDailyAttendanceSerializer,
                   200: MessageSerializer,
                   400: MessageSerializer},
    )
    def create(self, request):
        # your non-standard behaviour
        return super().create(request)