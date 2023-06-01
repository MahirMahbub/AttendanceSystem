from django.contrib.auth.hashers import make_password
from django.db import models
from django.utils import timezone
from apps.card_portal.models.user import AbstractUser, CallableUser
from utils.mixins import BaseModelMixin


class Machine(BaseModelMixin, AbstractUser):
    """
    Machine model
    """
    from apps.card_portal.models.employees import Employee
    model = models.CharField(max_length=128, null=True, blank=True)
    manufacturer = models.CharField(max_length=128, null=True, blank=True)
    employee = models.ManyToManyField(Employee, related_name='machine', through='MachinePermittedEmployee', blank=True)

    # def save(self, *args, **kwargs):
    #     now = timezone.now()
    #     u = CallableUser(last_login=now)
    #     u.set_password(self.password)
    #     u.save()
    #     self.callableuser_ptr_id = u.id
    #     super().save(*args, **kwargs)
    def save(self, *args, **kwargs):
        # self.password =
        self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return "ID: " + str(self.id) + ", Model: " + str(
            self.model)


class MachinePermittedEmployee(BaseModelMixin):
    """
    Machine Permitted Employee Association Table
    """
    from apps.card_portal.models.employees import Employee
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True, blank=True)
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, null=True, blank=True)
    start_date = models.DateField(auto_now_add=True)
    expiry_date = models.DateField(null=True, blank=True)
