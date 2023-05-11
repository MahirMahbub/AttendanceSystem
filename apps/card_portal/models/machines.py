from datetime import datetime, date

from django.db import models

from apps.card_portal.models import Employee
from utils.mixins import BaseModelMixin


class Machine(BaseModelMixin):
    """
    Machine model
    """
    model = models.CharField(max_length=128, null=True, blank=True)
    manufacturer = models.CharField(max_length=128, null=True, blank=True)
    employee = models.ManyToManyField(Employee, related_name='machine', through='MachinePermittedEmployee')


class MachinePermittedEmployee(BaseModelMixin):
    """
    Machine Permitted Employee Association Table
    """
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE)
    start_date = models.DateField(auto_now_add=True)
    expiry_date = models.DateField(null=True, blank=True)