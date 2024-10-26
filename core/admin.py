from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from import_export.admin import ImportExportModelAdmin
from core.models import Employee, Workflow, Location, Position, Department, JobOffering, JobOfferingRequiredDocument, \
    Task, Assignment, JobAssignments, Notification, SurveyField, SurveyFieldChoice, SurveyRecord, SurveyRecordValue, \
    SurveyHeading


# Register your models here.

class JobOfferingRequiredDocumentAdmin(admin.TabularInline):
    model = JobOfferingRequiredDocument


class TaskAdmin(admin.TabularInline):
    model = Task


class SurveyFieldChoiceAdmin(admin.TabularInline):
    model = SurveyFieldChoice


@admin.register(SurveyField)
class SurveyFieldAdmin(ImportExportModelAdmin):
    list_display = ["ordinal", 'label', "heading", 'type', 'placeholder', 'required', "dp", "minimum", "maximum"]
    search_fields = ['label', 'placeholder']
    inlines = [SurveyFieldChoiceAdmin]


@admin.register(Workflow)
class WorkflowAdmin(ImportExportModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name', 'description']
    inlines = [TaskAdmin]


@admin.register(Location)
class LocationAdmin(ImportExportModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(Employee)
class MemberAdmin(UserAdmin, ImportExportModelAdmin):
    model = Employee
    ordering = ['last_name', "first_name"]
    list_filter = ('is_staff', 'is_active', "role")
    readonly_fields = ('date_joined', 'employee_number')
    list_display = ('employee_number', 'nationalIdNo', 'first_name', 'last_name', 'email', 'date_of_birth', "role")
    search_fields = ('first_name', 'employee_number', 'last_name', 'email', 'nationalIdNo')

    fieldsets = (
        (None, {'fields': ('email', 'password', "username", 'role')}),
        ('Personal Info',
         {'fields': (
             'profilePhoto', "employee_number", "nationalIdNo", 'first_name', 'last_name', 'phone', 'sex', "address_line_1", 'address_line_2')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser',)}),
        ('Important dates', {'fields': ['date_joined']}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'profilePhoto',
                'username',
                "nationalIdNo",
                'email', 'password1', 'password2', 'first_name', 'last_name',
                'sex',
                'date_of_birth',
                'phone',
                'sex', 'role',
                'address_line_1',
                'address_line_2'),
        }),
    )


@admin.register(JobOffering)
class JobOfferingAdmin(ImportExportModelAdmin):
    list_display = ["job_id", "position", "position__department", "status", "publish_date", "due_date",
                    "number_of_candidates"]
    search_fields = ["position__department", "position__position__name"]
    inlines = [JobOfferingRequiredDocumentAdmin]


@admin.register(Department)
class DepartmentAdmin(ImportExportModelAdmin):
    list_display = ["code", "name", "parent"]
    search_fields = ["code", "name"]


@admin.register(JobAssignments)
class JobAssignmentAdmin(ImportExportModelAdmin):
    list_display = ["position__name", "position__department", "employee", "type", "start_date", "end_date", ]
    search_fields = [
        "position__name",
        "position__department__name",
        "employee__first__name",
        "employee__last__name"
    ]


@admin.register(Position)
class DepartmentAdmin(ImportExportModelAdmin):
    list_display = ["code", "name", "department", "salaryMin", "salaryMax", "parent", "keywords"]
    search_fields = ["code", "name", "keywords"]


admin.site.register(Assignment)


@admin.register(Notification)
class NotificationAdmin(ImportExportModelAdmin):
    list_display = ["subject", "description", "recipient", "author", "unread", "public", "emailed"]
    search_fields = ["code", "description"]


@admin.register(SurveyHeading)
class NotificationAdmin(ImportExportModelAdmin):
    list_display = ["ordinal", "name"]
    search_fields = ["name"]
