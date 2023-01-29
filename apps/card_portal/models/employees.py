from django.db import models
from django.utils.safestring import mark_safe

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

    def images(self):
        return EmployeesImage.objects.filter(employee=self)

    images.short_description = 'Images'

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

    def image_tag(self):
        return mark_safe(f'<img src="{self.image.url}" width="80" height="80" />')

    image_tag.short_description = 'Image View'
    image_tag.allow_tags = True

    def __str__(self):
        return "ID: " + str(self.id) + ", EMPLOYEE_ID: " + str(
            self.employee.id) + ", IMAGE: " + self.image.name


class EmployeesDailyAttendance(BaseModelMixin):
    """
    Employees daily attendance model
    """
    employee = models.ForeignKey(Employees, on_delete=models.CASCADE)
    date = models.DateField()
    in_time = models.TimeField()
    out_time = models.TimeField(null=True, blank=True)
    is_present = models.BooleanField(default=True)

    def __str__(self):
        return "ID: " + str(self.id) + ", EMPLOYEE_ID: " + str(
            self.employee.id) + ", DATE: " + str(self.date) + ", IS_PRESENT: " + str(
            self.is_present)
