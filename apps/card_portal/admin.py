from django.contrib import admin

from apps.card_portal.models import Employees, EmployeesDesignation, EmployeesImage

# Register your models here.
admin.site.register(Employees)
admin.site.register(EmployeesDesignation)
admin.site.register(EmployeesImage)
