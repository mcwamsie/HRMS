from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import redirect
from django.utils import timezone
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, FormView, DetailView

from HRMS import settings
from core.forms import RegistrationForm, JobOfferingForm, EmployeeForm, JobAssignmentForm, JobApplicationForm, \
    DocumentUploadForm, TaskApprovalForm, SurveyForm, EmployeeDocumentUploadForm
from core.helpers.access_required_mixin import AccessRequiredMixin
from core.helpers.search_filter import SearchFilter
from core.models import JobOffering, JobApplication, Employee, Assignment, Notification, SurveyHeading, SurveyRecord, \
    SurveyField, SurveyRecordValue, FAQCategory


# ========================================================================
#                       PUBLIC PAGES
# ========================================================================
# class IndexView(ListView, SearchFilter):
#     model = JobOffering
#     paginate_by = settings.PAGE_SIZE
#     paginator_class = Paginator
#     template_name = "pages/index.html"
#     total_count = 0
#     search_fields = [
#         "position__name",
#         "position__code",
#         "position__department__name",
#         "position__department__code",
#     ]
#
#     def get_queryset(self, **kwargs):
#         today = timezone.now().today()
#         queryset = super().get_queryset().filter(
#             Q(status="open") &
#             Q(published=True) &
#             Q(due_date__gte=today)
#         )
#         self.total_count = queryset.count()
#         return self.filter_queryset_here(request=self.request, queryset=queryset)
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#
#         job_offering = JobOffering.objects.none()
#
#         if job_offering_id := self.request.GET.get('job_offering'):
#             try:
#                 job_offering = JobOffering.objects.get(id=job_offering_id)
#             except JobOffering.DoesNotExist:
#                 messages.error(self.request, "Job offering not found")
#                 return redirect("index")
#
#         context['job_offering'] = job_offering
#         context["total"] = self.total_count
#         return context

def index_view(request):
    if request.user.is_authenticated:
        return redirect('app_dashboard')
    else:
        return redirect('login')


class UserRegistrationView(CreateView):
    template_name = 'registration/register.html'
    form_class = RegistrationForm
    success_url = "/accounts/login/"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['larger'] = True
        return context

    def form_valid(self, form):
        employee = form.save(commit=False)
        employee.role = "APPLICANT"
        employee.is_active = True
        employee.is_staff = False
        employee.is_superuser = False
        employee.save()

        raw_password = form.cleaned_data.get('password1')
        user = authenticate(username=employee.email, password=raw_password)

        if user is not None:
            messages.success(self.request, "Welcome to Grace Care!")
            login(self.request, user)
            if self.request.GET.get('next'):
                return redirect(self.request.GET.get('next'))
            return redirect('app_dashboard')
        return redirect('index')


class JobApplicationView(LoginRequiredMixin, UpdateView):
    # required_roles = ["ADMIN", "HR OFFICER", "EMPLOYEE", "APPLICANT"]
    template_name = "pages/apply-job.html"
    model = JobOffering
    form_class = JobApplicationForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


# ========================================================================
#                       PERSONAL DASHBOARD
# ========================================================================
class HomeView(AccessRequiredMixin, TemplateView):
    template_name = "pages/home.html"
    required_roles = ["ADMIN", "HR OFFICER", "EMPLOYEE", "APPLICANT"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tasks = Assignment.objects.filter(assigned_to=self.request.user)
        context['tasks'] = tasks[:3]
        context['now'] = timezone.now()
        return context


class ProfileView(AccessRequiredMixin, FormView):
    template_name = "pages/profile.html"
    required_roles = ["ADMIN", "HR OFFICER", "EMPLOYEE", "APPLICANT"]
    form_class = EmployeeDocumentUploadForm
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        context['form'] = self.form_class(instance=self.request.user)
        return context

    def post(self, request, *args, **kwargs):
        user = request.user
        form = self.form_class(request.POST, request.FILES, instance=user)

        if form.is_valid():
            form.save()
            messages.success(self.request, "Your profile documents has been updated!")
            return redirect('app_profile')
        return self.render_to_response({
            "form": form,
            "user": request.user,
        })



# ========================================================================
#                       FAQ
# ========================================================================
class FAQView(LoginRequiredMixin, ListView):
    template_name = "pages/faq.html"
    model = FAQCategory
    total_count = 0

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total"] = self.total_count
        context["support_email"] = settings.SUPPORT_EMAIL
        return context

# ========================================================================
#                       Surveys
# ========================================================================
class PersonalSurveyListView(LoginRequiredMixin, ListView, SearchFilter):
    template_name = "pages/personal_surveys.html"
    model = SurveyRecord
    paginate_by = settings.PAGE_SIZE
    paginator_class = Paginator
    total_count = 0
    search_fields = [
        "employee__first_name",
        "employee__last_name",
        "employee__employee_number",
        "employee__nationalIdNo",
    ]

    def get_queryset(self, **kwargs):
        today = timezone.now().today()
        queryset = super().get_queryset().filter(
            employee=self.request.user
        )
        self.total_count = queryset.count()
        return self.filter_queryset_here(request=self.request, queryset=queryset)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total"] = self.total_count
        return context


class NewSurveyView(AccessRequiredMixin, FormView):
    template_name = "pages/survey-new.html"
    form_class = SurveyForm
    required_roles = ["ADMIN", "HR OFFICER", "EMPLOYEE", "APPLICANT"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["headings"] = SurveyHeading.objects.all().prefetch_related("survey_fields", )
        return context

    def form_invalid(self, form):
        print(form.errors)
        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        record = SurveyRecord.objects.create(
            employee=self.request.user,
        )

        for fieldName in form.cleaned_data.keys():
            try:
                field = SurveyField.objects.get(name=fieldName)
                SurveyRecordValue.objects.create(
                    field=field,
                    record=record,
                    textValue=form.cleaned_data[fieldName] if field.type != "N" else None,
                    numberValue=form.cleaned_data[fieldName] if field.type == "N" else None
                )
            except SurveyRecordValue.DoesNotExist:
                pass

        messages.success(self.request, "Thank you! Your survey has been recorded.")
        return redirect("app_personal_surveys_list")


class PersonalSurveyDetailsView(AccessRequiredMixin, DetailView):
    template_name = 'pages/personal_survey_details.html'
    required_roles = ["ADMIN", "HR OFFICER", "EMPLOYEE"]
    form_class = DocumentUploadForm
    model = SurveyRecord

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["headings"] = SurveyHeading.objects.all().prefetch_related("survey_fields", )
        return context


# ========================================================================
#                       JOB APPLICATIONS
# ========================================================================
class ApplicationListView(LoginRequiredMixin, ListView, SearchFilter):
    template_name = "pages/applications.html"
    model = JobApplication
    paginate_by = settings.PAGE_SIZE
    paginator_class = Paginator
    total_count = 0
    search_fields = [
        "job_offering__position__name",
        "job_offering__position__code",
        "job_offering__position__department__name",
        "job_offering__position__department__code",
    ]

    def get_queryset(self, **kwargs):
        today = timezone.now().today()
        queryset = super().get_queryset().filter(
            employee=self.request.user
        )
        self.total_count = queryset.count()
        return self.filter_queryset_here(request=self.request, queryset=queryset)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total"] = self.total_count
        return context


# ========================================================================
#                       NOTIFICATIONS
# ========================================================================
class NotificationListView(AccessRequiredMixin, ListView, SearchFilter):
    template_name = "pages/notifications.html"
    required_roles = ["ADMIN", "HR OFFICER", "EMPLOYEE", "APPLICANT"]
    model = Notification
    paginate_by = settings.PAGE_SIZE
    paginator_class = Paginator
    total_count = 0
    search_fields = [
        "subject",
        "description",
    ]

    def get_queryset(self, **kwargs):
        queryset = super().get_queryset().filter(recipient=self.request.user)
        self.total_count = queryset.count()
        return self.filter_queryset_here(request=self.request, queryset=queryset)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total"] = self.total_count
        return context


# ========================================================================
#                       PERSONAL TASKS
# ========================================================================
class PersonalTaskListView(AccessRequiredMixin, ListView, SearchFilter):
    template_name = "pages/personal_tasks.html"
    required_roles = ["ADMIN", "HR OFFICER", "EMPLOYEE"]
    model = Assignment
    paginate_by = settings.PAGE_SIZE
    paginator_class = Paginator
    total_count = 0
    search_fields = [
        "task__name",
        "task__description",
    ]

    def get_queryset(self, **kwargs):
        today = timezone.now().today()
        queryset = super().get_queryset().filter(assigned_to=self.request.user)
        self.total_count = queryset.count()
        return self.filter_queryset_here(request=self.request, queryset=queryset)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total"] = self.total_count
        context["personal"] = True
        return context


class PersonalTaskDetailsView(AccessRequiredMixin, UpdateView):
    template_name = 'pages/personal_tasks_details.html'
    required_roles = ["ADMIN", "HR OFFICER", "EMPLOYEE"]
    form_class = DocumentUploadForm
    model = Assignment

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["now"] = timezone.now()
        context["personal"] = True
        return context

    def form_valid(self, form):
        assignment = form.save(commit=False)

        if assignment.task.task_type != "file":
            if assignment.due_date < timezone.now():
                messages.error(self.request, "This task is not yet due! It can not be approved.")
                return redirect('personal_task_details', assignment.pk)
        else:
            assignment.status = "Submitted"
        assignment.save()
        messages.success(self.request, f"Document for task: '{assignment.task.name.title()}' submitted successfully")
        return redirect('app_tasks_personal_list')


# ========================================================================
#                       JOB OFFERINGS
# ========================================================================
class JobOfferingListView(AccessRequiredMixin, ListView, SearchFilter):
    template_name = "pages/job_offerings.html"
    required_roles = ["ADMIN", "HR OFFICER"]
    model = JobOffering
    paginate_by = settings.PAGE_SIZE
    paginator_class = Paginator
    total_count = 0
    search_fields = [
        "position__name",
        "position__code",
        "position__department__name",
        "position__department__code",
    ]

    def get_queryset(self, **kwargs):
        today = timezone.now().today()
        queryset = super().get_queryset()
        self.total_count = queryset.count()
        return self.filter_queryset_here(request=self.request, queryset=queryset)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total"] = self.total_count
        return context


class NewJobOfferingView(AccessRequiredMixin, CreateView):
    template_name = 'pages/job_offerings_new.html'
    form_class = JobOfferingForm
    model = JobOffering
    required_roles = ["ADMIN", "HR OFFICER"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['larger'] = True
        return context

    def form_valid(self, form):
        print("locations", form.cleaned_data.get("locations"))
        job_offering = form.save(commit=False)
        job_offering.save()
        form.save_m2m()
        messages.success(self.request, "Job offering created successfully")
        return redirect('app_job_offerings_list')


class JobOfferingDetailsView(AccessRequiredMixin, UpdateView):
    template_name = 'pages/job_offerings_details.html'
    required_roles = ["ADMIN", "HR OFFICER"]
    form_class = JobOfferingForm
    model = JobOffering

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        job_offering = form.save(commit=False)
        job_offering.save()
        form.save_m2m()
        messages.success(self.request, "Job offering updated successfully")
        return redirect('app_job_offerings_list')


# ========================================================================
#                       EMPLOYEES
# ========================================================================
class EmployeeListView(AccessRequiredMixin, ListView, SearchFilter):
    template_name = "pages/employees.html"
    required_roles = ["ADMIN", "HR OFFICER"]
    model = Employee
    paginate_by = settings.PAGE_SIZE
    paginator_class = Paginator
    total_count = 0
    search_fields = [
        "first_name",
        "last_name",
        "employee_number",
        "nationalIdNo",
    ]

    def get_queryset(self, **kwargs):
        queryset = super().get_queryset().filter(is_staff=False)
        self.total_count = queryset.count()
        return self.filter_queryset_here(request=self.request, queryset=queryset)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total"] = self.total_count
        return context


class NewEmployeeView(AccessRequiredMixin, CreateView):
    template_name = 'pages/employees_new.html'
    form_class = EmployeeForm
    model = JobOffering
    required_roles = ["ADMIN", "HR OFFICER"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['assignment_form'] = JobAssignmentForm()
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        assignment_form = JobAssignmentForm(request.POST, request.FILES)
        if form.is_valid() and assignment_form.is_valid():
            employee = form.save(commit=False)
            employee.role = "EMPLOYEE"
            employee.save()
            assignment = assignment_form.save(commit=False)
            assignment.employee = employee

            assignment.save()
            if workflow := assignment.workflow:
                for task in workflow.tasks.all():
                    if task.stage == "pre-onboarding":
                        date_due = assignment.start_date
                    else:
                        date_due = assignment.start_date + timezone.timedelta(days=task.days, minutes=task.minutes,
                                                                              hours=task.hours)

                    Assignment.objects.create(
                        task=task,
                        assigned_to=employee,
                        due_date=date_due
                    )
            messages.success(self.request, "Employee created successfully")
            return redirect('app_employees_list')
        else:
            print("form errors", form.errors)
            print("assignment_form errors", assignment_form.errors)
            return self.render_to_response({
                "form": form,
                "assignment_form": assignment_form
            })


class EmployeeDetailsView(UpdateView):
    template_name = 'pages/employees_details.html'
    form_class = EmployeeForm
    model = Employee

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        employee = form.save(commit=True)
        # employee.save()
        # form.save_m2m()
        messages.success(self.request, "Employee updated successfully")
        return redirect('app_employees_list')


# ========================================================================
#                       TASKS
# ========================================================================
class TaskListView(AccessRequiredMixin, ListView, SearchFilter):
    template_name = "pages/personal_tasks.html"
    required_roles = ["ADMIN", "HR OFFICER", ]
    model = Assignment
    paginate_by = settings.PAGE_SIZE
    paginator_class = Paginator
    total_count = 0
    search_fields = [
        "task__name",
        "task__description",
        "assigned_to__first_name",
        "assigned_to__last_name",
        "assigned_to__employee_number"
    ]

    def get_queryset(self, **kwargs):
        today = timezone.now().today()
        queryset = super().get_queryset()
        self.total_count = queryset.count()
        return self.filter_queryset_here(request=self.request, queryset=queryset)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total"] = self.total_count
        context["personal"] = False
        return context


class NewTaskFileUploadView(AccessRequiredMixin, CreateView):
    template_name = 'pages/job_offerings_new.html'
    form_class = JobOfferingForm
    model = JobOffering
    required_roles = ["ADMIN", "HR OFFICER"]

    def form_valid(self, form):
        job_offering = form.save(commit=False)
        job_offering.save()
        form.save_m2m()
        messages.success(self.request, "Job offering created successfully")
        return redirect('app_job_offerings_list')


class TaskDetailsView(AccessRequiredMixin, UpdateView):
    template_name = 'pages/personal_tasks_details.html'
    required_roles = ["ADMIN", "HR OFFICER"]
    form_class = TaskApprovalForm
    model = Assignment

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["now"] = timezone.now()
        context["personal"] = False
        return context

    def form_valid(self, form):
        assignment = form.save(commit=True)
        messages.success(self.request, "Task approved successfully")
        return redirect('app_tasks_list')
# ========================================================================
#                       SURVEYS
# ========================================================================
class SurveyListView(AccessRequiredMixin, ListView, SearchFilter):
    template_name = "pages/surveys.html"
    model = SurveyRecord
    paginate_by = settings.PAGE_SIZE
    paginator_class = Paginator
    total_count = 0
    required_roles = ["ADMIN", "HR OFFICER", ]
    search_fields = [
        "employee__first_name",
        "employee__last_name",
        "employee__employee_number",
        "employee__nationalIdNo",
    ]

    def get_queryset(self, **kwargs):
        today = timezone.now().today()
        queryset = super().get_queryset()
        self.total_count = queryset.count()
        return self.filter_queryset_here(request=self.request, queryset=queryset)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total"] = self.total_count
        return context

class SurveyDetailsView(AccessRequiredMixin, DetailView):
    template_name = 'pages/survey_details.html'
    required_roles = ["ADMIN", "HR OFFICER"]
    form_class = DocumentUploadForm
    model = SurveyRecord

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["headings"] = SurveyHeading.objects.all().prefetch_related("survey_fields", )
        return context
