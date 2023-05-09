from rest_framework import serializers, status

from apps.card_portal.models import EmployeesDailyAttendance, Employees


class EmployeesDailyAttendanceCreationSerializer(serializers.Serializer):  # noqa
    rdf = serializers.IntegerField(required=True, help_text="RDF number of the employee")
    date = serializers.DateField(required=True, help_text="Date of the attendance")
    check_in = serializers.TimeField(required=False, default=None, help_text="Check in time of the employee")
    check_out = serializers.TimeField(required=False, default=None, help_text="Check out time of the employee")

    def validate(self, attrs):
        if attrs.get('check_in') is None and attrs.get('check_out') is None:
            raise serializers.ValidationError("Either check_in or check_out is required")
        if attrs.get('check_in') is not None and attrs.get('check_out') is not None:
            raise serializers.ValidationError("Provide only check_in or check_out")
        return attrs

    def create(self, validated_data):
        last_attendance = EmployeesDailyAttendance.objects.filter(
            employee__rdf_number=validated_data['rdf'],
            date=validated_data['date']
        ).last()
        if last_attendance is not None:
            check_in, check_out, date, rdf = self._extract_attendance_data_from_validated_data(validated_data)
            if last_attendance.in_time is not None and last_attendance.out_time is not None:
                if check_out is not None:
                    response = serializers.ValidationError({"message": "Check-in should be done first"})
                    response.status_code = status.HTTP_201_CREATED
                    raise response
                if check_in is not None:
                    validated_data['is_present'] = True
                    validated_data['in_time'] = check_in
                    validated_data['date'] = date
                    employee = Employees.objects.get(rdf_number=rdf)
                    return EmployeesDailyAttendance.objects.create(employee=employee, **validated_data)
            if check_in is not None:
                if last_attendance.in_time is not None and last_attendance.out_time is None:
                    response = serializers.ValidationError({"message": "Check-in already done"})
                    response.status_code = status.HTTP_201_CREATED
                    raise response
            if check_out is not None:
                if last_attendance.out_time is None:
                    if last_attendance.in_time >= check_out:
                        raise serializers.ValidationError(
                            {"message": "Check-out time must be greater than check-in time"})
                    last_attendance.out_time = check_out
                    last_attendance.save()
                    return last_attendance
                else:
                    response = serializers.ValidationError({"message": "Check-out already done"},
                                                           code=status.HTTP_201_CREATED)
                    response.status_code = status.HTTP_201_CREATED
                    raise response
        else:
            if validated_data.get('check_in') is None:
                raise serializers.ValidationError({"message": "Check-in is required"})
            rdf = validated_data.pop('rdf')
            return self._create_employee(rdf, validated_data)

    @staticmethod
    def _extract_attendance_data_from_validated_data(validated_data):
        rdf = validated_data.pop('rdf')
        date = validated_data.pop('date')
        check_in = validated_data.pop('check_in', None)
        check_out = validated_data.pop('check_out', None)
        return check_in, check_out, date, rdf

    @staticmethod
    def _create_employee(rdf, validated_data):
        validated_data['is_present'] = True
        validated_data['in_time'] = validated_data.pop('check_in')
        employee = Employees.objects.get(rdf_number=rdf)
        validated_data.pop('check_out')
        return EmployeesDailyAttendance.objects.create(employee=employee, **validated_data)

    def to_representation(self, instance):
        serializer = EmployeesDailyAttendanceSerializer(instance)
        return serializer.data


class EmployeesDailyAttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeesDailyAttendance
        fields = '__all__'


class MessageSerializer(serializers.Serializer):  # noqa
    message = serializers.CharField(default="<some message>")
