from django.db import models

from utils.mixins import BaseModelMixin


class Employees(BaseModelMixin):
    """
    Employees model
    """
    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)
    email = models.EmailField()
    phone_number = models.CharField(max_length=128, null=True, blank=True)
    address = models.CharField(max_length=128, null=True, blank=True)
    district = models.CharField(max_length=128, null=True, blank=True)
    division = models.CharField(max_length=128, null=True, blank=True)
    post_code = models.CharField(max_length=128, null=True, blank=True)
    rdf_number = models.CharField(max_length=128)
    dob = models.DateField()

    def __str__(self):
        return "ID: " + str(self.id) + ", NAME: " + self.first_name + " " + self.last_name + ", EMAIL: " + self.email


class EmployeesDesignation(BaseModelMixin):
    """
    Employees designation model
    """
    employee = models.ForeignKey(Employees, on_delete=models.CASCADE)
    designation = models.CharField(max_length=128)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return "ID: " + str(self.id) + ", EMPLOYEE_ID: " + str(self.employee.id) + \
            ", DESIGNATION: " + self.designation + ", IS_ACTIVE: " + str(
                self.is_active)


class EmployeesImage(BaseModelMixin):
    """
    Employees image model
    """
    employee = models.ForeignKey(Employees, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="employees/images/")

    def __str__(self):
        return "ID: " + str(self.id) + ", EMPLOYEE_ID: " + str(
            self.employee.id) + ", IMAGE: " + self.image.name
