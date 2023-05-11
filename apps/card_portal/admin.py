from django.contrib import admin

from apps.card_portal.models import Employee, EmployeesDesignation, EmployeesImage, EmployeesDailyAttendance, Machine, \
    MachinePermittedEmployee, EmployeeAccessCardUsageLog


class EmployeesImageAdminInline(admin.TabularInline):
    fk_name = "employee"
    model = EmployeesImage
    readonly_fields = ('image_tag',)

    def get_extra(self, request, obj=None, **kwargs):
        extra = 0
        if obj:
            return extra
        return extra


class EmployeesDesignationAdminInline(admin.TabularInline):
    fk_name = "employee"
    model = EmployeesDesignation

    def get_extra(self, request, obj=None, **kwargs):
        extra = 0
        if obj:
            return extra
        return extra


class EmployeesDailyAttendanceAdminInline(admin.TabularInline):
    fk_name = "employee"
    model = EmployeesDailyAttendance

    def get_extra(self, request, obj=None, **kwargs):
        extra = 0
        if obj:
            return extra
        return extra

    def has_add_permission(self, request, obj):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Employee)
class EmployeesAdmin(admin.ModelAdmin):
    list_display = (
        'first_name', 'last_name', 'email', 'phone_number', 'address', 'district', 'division', 'post_code',
        'rdf_number', 'dob')
    list_filter = (
        'first_name', 'last_name', 'email', 'district', 'division', 'post_code',
        'rdf_number', 'dob')
    search_fields = (
        'first_name', 'last_name', 'email', 'phone_number', 'address', 'district', 'division', 'post_code',
        'rdf_number', 'dob')
    inlines = [EmployeesImageAdminInline, EmployeesDesignationAdminInline, EmployeesDailyAttendanceAdminInline]


@admin.register(EmployeesDesignation)
class EmployeesDesignationAdmin(admin.ModelAdmin):
    list_display = ('employee', 'designation', 'start_date', 'end_date', 'is_active')
    list_filter = (
        'employee__first_name', 'employee__last_name', 'employee__email', 'designation', 'start_date', 'end_date',
        'is_active'
    )
    search_fields = (
        'employee__first_name', 'employee__last_name', 'employee__email', 'designation', 'start_date', 'end_date',
        'is_active'
    )
    readonly_fields = ('employee',)


@admin.register(EmployeesImage)
class EmployeesImageAdmin(admin.ModelAdmin):
    list_display = ('employee', 'image', 'image_tag')
    list_filter = ('employee__first_name', 'employee__last_name', 'employee__email',)
    search_fields = ('employee__first_name', 'employee__last_name', 'employee__email',)
    readonly_fields = ('image_tag', 'employee',)


@admin.register(EmployeesDailyAttendance)
class EmployeesDailyAttendanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'in_time', 'out_time', 'is_present')
    list_filter = (
        'employee__first_name', 'employee__last_name', 'employee__email', 'date', 'in_time', 'out_time', 'is_present'
    )
    search_fields = ('employee__first_name', 'employee__last_name', 'employee__email', 'date', 'in_time', 'out_time')
    readonly_fields = ('created_at', 'updated_at', 'date', 'in_time', 'out_time', 'employee', 'is_present', "employee")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class MachineAdminInline(admin.TabularInline):
    fk_name = "employee"
    model = Machine

    def get_extra(self, request, obj=None, **kwargs):
        extra = 0
        if obj:
            return extra
        return extra


class EmployeesMachineAdminInline(admin.TabularInline):
    fk_name = "machine"
    model = MachinePermittedEmployee

    def get_extra(self, request, obj=None, **kwargs):
        extra = 0
        if obj:
            return extra
        return extra


@admin.register(Machine)
class MachineAdmin(admin.ModelAdmin):
    list_display = ('model', 'manufacturer')
    list_filter = ('model', 'manufacturer')
    search_fields = ('model', 'manufacturer')
    inlines = [EmployeesMachineAdminInline]


@admin.register(MachinePermittedEmployee)
class MachinePermittedEmployeeAdmin(admin.ModelAdmin):
    list_display = ('employee', 'machine', 'start_date', 'expiry_date')
    list_filter = (
        'employee__first_name', 'employee__last_name', 'employee__email', 'machine__model', 'start_date', 'expiry_date')
    search_fields = (
        'employee__first_name', 'employee__last_name', 'employee__email', 'machine__model', 'start_date', 'expiry_date')


@admin.register(EmployeeAccessCardUsageLog)
class EmployeeAccessCardUsageLogAdmin(admin.ModelAdmin):
    list_display = ('employee', 'machine', 'date', 'access_type', 'time')
    list_filter = (
        'employee__first_name', 'employee__last_name', 'employee__email', 'machine', 'access_type'
    )
    search_fields = (
        'employee__first_name', 'employee__last_name', 'employee__email', 'machine', 'access_type'
    )
    # readonly_fields = ('employee', 'machine', 'access_card_number', 'access_card_type', 'access_time')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
