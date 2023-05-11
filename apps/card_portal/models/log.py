from django.db import models

from apps.card_portal.models import Employee
from apps.card_portal.models.machines import Machine
from utils.mixins import BaseModelMixin


class EmployeeAccessCardUsageLog(BaseModelMixin):
    """
    Employee access card usage log model
    """

    class AccessType(models.TextChoices):
        SIGN_IN = 'Sign In'
        SIGN_OUT = 'Sign Out'

    employee = models.ForeignKey(Employee, on_delete=models.DO_NOTHING)
    date = models.DateField()
    access_type = models.CharField(max_length=255, choices=AccessType.choices)
    machine = models.ForeignKey(Machine, on_delete=models.DO_NOTHING, blank=True, null=True)
    time = models.TimeField()
    success = models.BooleanField(default=True)

    def __str__(self):
        return "MACHINE_ID: " + str(self.id) + ", EMPLOYEE_ID: " + str(
            self.employee.id) + ", DATE: " + str(self.date) + ", ACCESS TYPE: " + str(
            self.access_type) + ", TIME: " + str(self.time)
