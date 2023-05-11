from rest_framework import serializers, status

from apps.card_portal.models import EmployeesDailyAttendance, Employee, EmployeeAccessCardUsageLog


class EmployeesDailyAttendanceCreationSerializer(serializers.Serializer):  # noqa
    rdf = serializers.CharField(required=True, help_text="RDF number of the employee")
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

        # TODO: Check if the employee is permitted to use the machine
        machine = None

        if last_attendance is not None:
            check_in, check_out, date, rdf = self._extract_attendance_data_from_validated_data(validated_data)
            if last_attendance.in_time is not None and last_attendance.out_time is not None:
                if check_out is not None:
                    self._create_access_card_log(
                        employee=last_attendance.employee,
                        date=date,
                        time=check_out,
                        access_type=EmployeeAccessCardUsageLog.AccessType.SIGN_OUT,
                        machine=machine,
                        success=True
                    )
                    response = serializers.ValidationError({"message": "Check-in should be done first"})
                    response.status_code = status.HTTP_200_OK
                    raise response
                if check_in < last_attendance.out_time and date <= last_attendance.date:
                    self._create_access_card_log(
                        employee=last_attendance.employee,
                        date=date,
                        time=check_in,
                        access_type=EmployeeAccessCardUsageLog.AccessType.SIGN_IN,
                        machine=machine,
                        success=False
                    )
                    response = serializers.ValidationError(
                        {"message": "Check-in time must be greater than check-out time of last attendance"})
                    raise response
                if check_in is not None:
                    validated_data['is_present'] = True
                    validated_data['in_time'] = check_in
                    validated_data['date'] = date
                    employee = Employee.objects.get(rdf_number=rdf)
                    self._create_access_card_log(
                        employee=last_attendance.employee,
                        date=date,
                        time=check_in,
                        access_type=EmployeeAccessCardUsageLog.AccessType.SIGN_IN,
                        machine=machine,
                        success=True
                    )
                    return EmployeesDailyAttendance.objects.create(employee=employee, **validated_data)
            if check_in is not None:
                if last_attendance.in_time is not None and last_attendance.out_time is None:
                    response = serializers.ValidationError({"message": "Check-in already done"})
                    response.status_code = status.HTTP_200_OK
                    self._create_access_card_log(
                        employee=last_attendance.employee,
                        date=date,
                        time=check_in,
                        access_type=EmployeeAccessCardUsageLog.AccessType.SIGN_IN,
                        machine=machine,
                        success=True
                    )
                    raise response
            if check_out is not None:
                if last_attendance.out_time is None:
                    if last_attendance.in_time >= check_out:
                        raise serializers.ValidationError(
                            {"message": "Check-out time must be greater than check-in time"})
                    last_attendance.out_time = check_out
                    last_attendance.save()
                    self._create_access_card_log(
                        employee=last_attendance.employee,
                        date=date,
                        time=check_out,
                        access_type=EmployeeAccessCardUsageLog.AccessType.SIGN_OUT,
                        machine=machine,
                        success=False
                    )
                    return last_attendance
                else:
                    self._create_access_card_log(
                        employee=last_attendance.employee,
                        date=date,
                        time=check_out,
                        access_type=EmployeeAccessCardUsageLog.AccessType.SIGN_OUT,
                        machine=machine,
                        success=True
                    )
                    response = serializers.ValidationError({"message": "Check-out already done"},
                                                           code=status.HTTP_201_CREATED)
                    response.status_code = status.HTTP_200_OK
                    raise response
        else:
            if validated_data.get('check_in') is None:
                check_in, check_out, date, rdf = self._extract_attendance_data_from_validated_data(validated_data)
                employee = Employee.objects.get(rdf_number=rdf)
                self._create_access_card_log(
                    employee=employee,
                    date=date,
                    time=check_in,
                    access_type=EmployeeAccessCardUsageLog.AccessType.SIGN_IN,
                    machine=machine,
                    success=True
                )
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
    def _create_access_card_log(access_type, employee, date, time, machine, success):
        return EmployeeAccessCardUsageLog.objects.create(
            employee=employee,
            date=date,
            time=time,
            access_type=access_type,
            machine=machine,
            success=success
        )

    @staticmethod
    def _create_employee(rdf, validated_data):
        validated_data['is_present'] = True
        validated_data['in_time'] = validated_data.pop('check_in')
        employee = Employee.objects.get(rdf_number=rdf)
        validated_data.pop('check_out')
        return EmployeesDailyAttendance.objects.create(employee=employee, **validated_data)

    def to_representation(self, instance):
        instance.name = instance.employee.first_name + " " + instance.employee.last_name
        serializer = EmployeesDailyAttendanceSerializer(instance)
        return serializer.data


class EmployeesDailyAttendanceSerializer(serializers.Serializer):  # noqa
    name = serializers.CharField(required=True, help_text="Name of the employee")
    date = serializers.DateField(required=False, default=None, help_text="Date of the attendance")
    in_time = serializers.TimeField(required=False, default=None, help_text="Check in time of the employee")
    out_time = serializers.TimeField(required=False, default=None, help_text="Check out time of the employee")


class MessageSerializer(serializers.Serializer):  # noqa
    message = serializers.CharField(default="<some message>")
