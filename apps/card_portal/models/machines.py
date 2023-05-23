from django.db import models

from utils.mixins import BaseModelMixin


class Machine(BaseModelMixin):
    """
    Machine model
    """
    from apps.card_portal.models.employees import Employee
    model = models.CharField(max_length=128, null=True, blank=True)
    manufacturer = models.CharField(max_length=128, null=True, blank=True)
    employee = models.ManyToManyField(Employee, related_name='machine', through='MachinePermittedEmployee')

    def __str__(self):
        return "ID: " + str(self.id) + ", Model: " + str(
            self.model)


class MachinePermittedEmployee(BaseModelMixin):
    """
    Machine Permitted Employee Association Table
    """
    from apps.card_portal.models.employees import Employee
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE)
    start_date = models.DateField(auto_now_add=True)
    expiry_date = models.DateField(null=True, blank=True)
