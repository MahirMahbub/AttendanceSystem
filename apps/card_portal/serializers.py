import traceback
from datetime import date

from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import update_last_login
from django.db import transaction, DatabaseError
from django.utils import timezone
from rest_framework import serializers, status
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
import logging

from apps.card_portal.models import EmployeesDailyAttendance, Employee, EmployeeAccessCardUsageLog, Machine

logger = logging.getLogger(__name__)
class EmployeesDailyAttendanceCreationSerializer(serializers.Serializer):  # noqa
    rdf = serializers.CharField(required=True, help_text="RDF number of the employee")
    # date = serializers.DateField(required=True, help_text="Date of the attendance")
    check_in = serializers.BooleanField(required=False, default=None, help_text="Check in time of the employee")
    check_out = serializers.BooleanField(required=False, default=None, help_text="Check out time of the employee")

    def validate(self, attrs):
        if attrs.get('check_in') is None and attrs.get('check_out') is None:
            raise serializers.ValidationError("Either check_in or check_out is required")
        if attrs.get('check_in') is not None and attrs.get('check_out') is not None:
            raise serializers.ValidationError("Provide only check_in or check_out")
        return attrs

    def create(self, validated_data):
        context = self.context['request']
        _date: date = timezone.now().astimezone(tz=timezone.get_current_timezone()).date()
        current_time = timezone.now().astimezone(tz=timezone.get_current_timezone()).time()
        last_attendance = EmployeesDailyAttendance.objects.filter(
            employee__rdf_number=validated_data['rdf'],
            date=_date
        ).last()

        # TODO: Check if the employee is permitted to use the machine
        machine = context.user
        employee = Employee.objects.filter(rdf_number=validated_data['rdf']).first()
        if employee is None:
            raise serializers.ValidationError({"message": "Employee not found"})
        machine_permitted_employee = machine.machinepermittedemployee_set.filter(employee=employee).first()
        if machine_permitted_employee is None:
            raise serializers.ValidationError(
                {"message": "Access Denied. Employee is not permitted to use this machine"})
        if machine_permitted_employee.expiry_date is not None and machine_permitted_employee.expiry_date < _date:
            raise serializers.ValidationError({"message": "Access Denied. Employee is not expired to use this machine"})

        if last_attendance is not None:
            check_in, check_out, rdf = self._extract_attendance_data_from_validated_data(validated_data)
            if last_attendance.in_time is not None and last_attendance.out_time is not None:
                try:
                    with transaction.atomic():
                        if check_out is not None:
                            self._create_access_card_log(
                                employee=last_attendance.employee,
                                _date=_date,
                                time=current_time,
                                access_type=EmployeeAccessCardUsageLog.AccessType.SIGN_OUT,
                                machine=machine,
                                success=True
                            )
                            response = serializers.ValidationError({"message": "Check-in should be done first"})
                            response.status_code = status.HTTP_200_OK
                            raise response
                        if current_time < last_attendance.out_time and _date <= last_attendance.date:
                            self._create_access_card_log(
                                employee=last_attendance.employee,
                                _date=_date,
                                time=current_time,
                                access_type=EmployeeAccessCardUsageLog.AccessType.SIGN_IN,
                                machine=machine,
                                success=False
                            )
                            response = serializers.ValidationError(
                                {"message": "Check-in time must be greater than check-out time of last attendance"})
                            raise response
                        if check_in is not None:
                            validated_data['is_present'] = True
                            validated_data['in_time'] = current_time
                            employee = Employee.objects.get(rdf_number=rdf)
                            self._create_access_card_log(
                                employee=last_attendance.employee,
                                _date=_date,
                                time=current_time,
                                access_type=EmployeeAccessCardUsageLog.AccessType.SIGN_IN,
                                machine=machine,
                                success=True
                            )
                            return EmployeesDailyAttendance.objects.create(employee=employee, **validated_data)
                except DatabaseError as db_exec:
                    logger.error(traceback.format_exc())
                    raise serializers.ValidationError({"message": "Check-in failed"})
            if check_in is not None:
                if last_attendance.in_time is not None and last_attendance.out_time is None:
                    response = serializers.ValidationError({"message": "Check-in already done"})
                    response.status_code = status.HTTP_200_OK
                    self._create_access_card_log(
                        employee=last_attendance.employee,
                        _date=_date,
                        time=current_time,
                        access_type=EmployeeAccessCardUsageLog.AccessType.SIGN_IN,
                        machine=machine,
                        success=True
                    )
                    raise response
            if check_out is not None:
                if last_attendance.out_time is None:
                    if last_attendance.in_time >= current_time:
                        raise serializers.ValidationError(
                            {"message": "Check-out time must be greater than check-in time"})
                    last_attendance.out_time = current_time
                    last_attendance.save()
                    self._create_access_card_log(
                        employee=last_attendance.employee,
                        _date=_date,
                        time=current_time,
                        access_type=EmployeeAccessCardUsageLog.AccessType.SIGN_OUT,
                        machine=machine,
                        success=False
                    )
                    return last_attendance
                else:
                    self._create_access_card_log(
                        employee=last_attendance.employee,
                        _date=_date,
                        time=current_time,
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
                check_in, check_out, rdf = self._extract_attendance_data_from_validated_data(validated_data)
                employee = Employee.objects.filter(rdf_number=rdf).first()
                self._create_access_card_log(
                    employee=employee,
                    _date=_date,
                    time=current_time,
                    access_type=EmployeeAccessCardUsageLog.AccessType.SIGN_IN,
                    machine=machine,
                    success=True
                )
                raise serializers.ValidationError({"message": "Check-in is required"})
            rdf = validated_data.pop('rdf')
            employee = Employee.objects.filter(rdf_number=rdf).first()
            if employee is None:
                raise serializers.ValidationError({"message": "Employee not found"})
            try:
                with transaction.atomic():
                    employee_daily_attendance = self._create_employee_attendance(rdf, validated_data, current_time,
                                                                                 _date, machine)
                    if employee_daily_attendance is not None:
                        self._create_access_card_log(
                            employee=employee,
                            _date=_date,
                            time=current_time,
                            access_type=EmployeeAccessCardUsageLog.AccessType.SIGN_IN,
                            machine=machine,
                            success=True
                        )
            except DatabaseError:
                traceback.print_exc()
                raise serializers.ValidationError({"message": "Check-in failed. Contact the admin"})

            return employee_daily_attendance

    @staticmethod
    def _extract_attendance_data_from_validated_data(validated_data):
        rdf = validated_data.pop('rdf')
        check_in = validated_data.pop('check_in', None)
        check_out = validated_data.pop('check_out', None)
        return check_in, check_out, rdf

    @staticmethod
    def _create_access_card_log(access_type, employee, _date, time, machine, success):
        return EmployeeAccessCardUsageLog.objects.create(
            employee=employee,
            date=_date,
            time=time,
            access_type=access_type,
            machine=machine,
            success=success
        )

    @staticmethod
    def _create_employee_attendance(rdf, validated_data, current_time, _date, machine):
        validated_data['is_present'] = True
        validated_data['in_time'] = current_time
        validated_data['date'] = _date
        validated_data['machine'] = machine
        employee = Employee.objects.get(rdf_number=rdf)
        validated_data.pop('check_out')
        validated_data.pop('check_in')
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


class MachineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Machine
        fields = ['email', 'password']


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):  # noqa

    def validate(self, attrs):
        data = {}
        self.user = Machine.objects.filter(email=attrs['email']).first()  # noqa
        if self.user is None:
            raise serializers.ValidationError({"message": "Invalid Email, Machine not found"})
        if not check_password(attrs['password'], self.user.password):
            raise serializers.ValidationError({"message": "Invalid Password"})
        refresh = self.get_token(self.user)

        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)
        update_last_login(None, self.user)
        return data
