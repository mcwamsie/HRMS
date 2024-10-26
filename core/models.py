import random
import re
import string
import uuid
from decimal import Decimal

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from notifications.utils import id2slug
from phonenumber_field.modelfields import PhoneNumberField
from sequences import Sequence

from HRMS import settings
from core.helpers.functions import cleanNumber


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def make_random_password(self, chars=string.ascii_letters + r"!#$%&()*?@[]" + string.digits):
        return ''.join(random.choice(chars) for _ in range(8))

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class Employee(AbstractUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee_number = models.CharField(max_length=10, editable=False, unique=True)
    nationalIdNo = models.CharField(max_length=150, help_text="format:XX-XXXXXX-A-XX", unique=True,
                                    verbose_name="Nation ID Number")
    profilePhoto = models.ImageField(blank=True, null=True, upload_to="users/profile-photos",
                                     verbose_name="Profile Photo")
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(max_length=255, unique=True, )
    phone = PhoneNumberField(max_length=20, verbose_name="Phone Number")
    SEX_CHOICES = [
        ("MALE", "Male"),
        ("FEMALE", "Female"),
        ("UNKNOWN", "Unknown"),
    ]
    date_of_birth = models.DateField(blank=True, null=True)
    sex = models.CharField(max_length=10, choices=SEX_CHOICES, default="UNKNOWN", verbose_name="Sex")
    address_line_1 = models.CharField(max_length=255, blank=True, null=True, verbose_name="Address Line 1")
    address_line_2 = models.CharField(max_length=255, blank=True, null=True, verbose_name="Address Line 2")
    ROLE_CHOICES = [
        ('ADMIN', 'Admin'),
        ('APPLICANT', 'Applicant'),
        ('HR OFFICER', 'HR Officer'),
        ("EMPLOYEE", "Employee")
    ]
    role = models.CharField(max_length=255, choices=ROLE_CHOICES, default="ADMIN")
    active_assignment = models.OneToOneField('JobAssignments', on_delete=models.SET_NULL,
                                             related_name="active_employee", null=True, blank=True)
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        "phone",
        "username",
        "first_name",
        "last_name",
        "nationalIdNo"
    ]

    @property
    def pre_onboarding_percentage(self):
        total = self.assignments.filter(task__stage="pre-onboarding").count()
        done = self.assignments.filter(task__stage="pre-onboarding", status="Done").count()
        if total == 0:
            return 0
        return int(done / total * 100)

    @property
    def complete_onboarding_percentage(self):
        done = self.pre_onboarding_percentage + self.onboarding_percentage
        return int(done / 200 * 100)

    @property
    def onboarding_percentage(self):
        total = self.assignments.filter(task__stage="onboarding").count()
        done = self.assignments.filter(task__stage="onboarding", status="Done").count()
        if total == 0:
            return 0
        return int(done / total * 100)

    @property
    def address(self):
        address = ""
        if self.address_line_1:
            address += self.address_line_1
        if self.address_line_2:
            if self.address_line_1:
                address += "\n" + self.address_line_2
            else:
                address += self.address_line_2
        return address

    @property
    def employment_status(self):
        if self.active_assignment is not None:
            if self.active_assignment.status == "open":
                if not self.active_assignment.end_date:
                    return self.active_assignment.get_type_display()
                else:
                    return f"Here until {self.active_assignment.end_date.strftime('%B %d, %Y')}"
        else:
            if self.is_active:
                return "Unassigned"
        return "Unknown"

    def __str__(self):
        return self.last_name.upper() + " " + self.first_name.upper()

    def save(self, *args, **kwargs):
        if not self.employee_number:
            sequenceNumber = Sequence(f"employees").get_next_value()
            randomNumber = "".join(random.choice(string.digits) for _ in range(2))
            self.employee_number = f"{sequenceNumber:04d}{randomNumber}"

        return super().save(*args, **kwargs)

    def clean(self):
        regex = r"^\d{2}[\s\-/]?\d{6,7}[\s\-/]?[A-Z][\s\-/]?\d{2}$"
        if self.nationalIdNo:
            if not re.match(regex, self.nationalIdNo):
                raise ValidationError({"nationalIdNo": "Invalid NationalId No format"})
            self.nationalIdNo = cleanNumber(self.nationalIdNo)
        return super(Employee, self).clean()

    def get_role_display(self):
        return dict(self.ROLE_CHOICES).get(self.role)

    class Meta:
        ordering = ["first_name", "last_name"]
        unique_together = [("nationalIdNo")]
        verbose_name = "Employee"
        verbose_name_plural = "Employees"


class Location(BaseModel):
    name = models.CharField(max_length=255)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name.upper()


class Department(BaseModel):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=3)
    parent = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        if self.parent:
            return f"{self.parent} / {self.name.upper()}"
        return self.name.upper()

    def save(self, *args, **kwargs):
        if self.parent:
            self.code = self.parent.code + "-" + self.code
        return super().save(*args, **kwargs)

    class Meta:
        ordering = ["parent__name", "name"]
        unique_together = [("parent", "name"), ("parent", "code")]
        verbose_name = "Department"
        verbose_name_plural = "Departments"


class Position(BaseModel):
    name = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=10, editable=False, unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, blank=True, null=True, verbose_name="Reports To")
    salaryMin = models.DecimalField(max_digits=11, decimal_places=2, default=Decimal(0), verbose_name="Salary Minimum")
    salaryMax = models.DecimalField(max_digits=11, decimal_places=2, default=Decimal(0), verbose_name="Salary Maximum")
    keywords = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.department} / {self.name.upper()}"

    def save(self, *args, **kwargs):
        if not self.code:
            departmentCode = self.department.code
            sequenceNumber = Sequence(f"position-{departmentCode}").get_next_value()
            self.code = f"{departmentCode}{sequenceNumber:03d}"
        return super().save(*args, **kwargs)

    class Meta:
        ordering = ["name"]
        verbose_name = "Position"
        verbose_name_plural = "Positions"
        unique_together = [("code", "name")]


class JobOffering(BaseModel):
    job_id = models.CharField(max_length=20, editable=False, unique=True)
    position = models.ForeignKey(Position, on_delete=models.CASCADE, verbose_name="Position")
    description = models.TextField()
    status_choices = [
        ('open', 'Open'),
        ('closed', 'Closed'),
    ]
    status = models.CharField(max_length=10, choices=status_choices, default='open')
    TYPE_CHOICES = [
        ("FULL TIME", "Full Time"),
        ("PART TIME", "Part Time"),
        ("CONTRACT", "Contract"),
    ]
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='FULL TIME')

    published = models.BooleanField(default=False)
    publish_date = models.DateTimeField(blank=True, null=True)
    due_date = models.DateTimeField()
    number_of_candidates = models.IntegerField(default=0)
    locations = models.ManyToManyField(Location, blank=False, verbose_name="Locations")
    contract_months = models.PositiveIntegerField(default=0)
    workflow = models.ForeignKey("Workflow", on_delete=models.CASCADE, related_name="job_offerings",
                                 verbose_name="Workflow Template")

    def __str__(self):
        return f"{self.job_id}: {self.position}"

    def clean(self):
        if self.type and self.contract_months:
            if self.type == "CONTRACT" and self.contract_months <= 0:
                raise ValidationError({"contract_months": "Enter a number greater than 0"})
        if self.position:
            if JobOffering.objects.filter(
                    ~Q(id=self.id) &
                    Q(position=self.position) &
                    Q(due_date__gte=timezone.now()) &
                    Q(status="open")
            ).exists():
                raise ValidationError(
                    f"There is another job offering for position '{str(self.position).title()}' that has already been open before, close it or wait for its due date to create this one")
        if self.due_date and timezone.now() > self.due_date:
            raise ValidationError({"due_date": "Due date cannot be in the past"})
        return super().clean()

    def save(self, *args, **kwargs):
        if not self.job_id:
            positionCode = self.position.code
            sequenceNumber = Sequence(f"job-offering-{positionCode}").get_next_value()
            self.job_id = f"{positionCode}-{sequenceNumber:03d}"

        if self.published:
            self.publish_date = timezone.now()
        return super().save(*args, **kwargs)

    class Meta:
        ordering = ['job_id']
        verbose_name = "Job Offering"
        verbose_name_plural = "Job Offerings"


class JobOfferingRequiredDocument(BaseModel):
    name = models.CharField(max_length=255)
    job_offering = models.ForeignKey(JobOffering, on_delete=models.CASCADE, related_name="required_documents",
                                     verbose_name="Job Offering")
    optional = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = "Job Offering Required Document"
        verbose_name_plural = "Job Offering Required Documents"


class JobApplication(BaseModel):
    job_offering = models.ForeignKey(JobOffering, on_delete=models.CASCADE, related_name="applications",
                                     verbose_name="Job Offering")
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name="Employee")
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("INTERVIEWED", "Interviewed"),
        ("COMPLETED", "Completed"),
    ]
    status = models.CharField(max_length=11, choices=STATUS_CHOICES, default='PENDING')

    def __str__(self):
        return f"{self.job_offering}: {self.status}"

    class Meta:
        verbose_name = "Job Application"
        verbose_name_plural = "Job Applications"


class JobAssignments(BaseModel):
    position = models.ForeignKey(Position, on_delete=models.CASCADE, verbose_name="Position")
    job_offering = models.ForeignKey(JobOffering, blank=True, null=True, related_name="assigned_employees",
                                     on_delete=models.CASCADE, verbose_name="Job Offering")
    location = models.ForeignKey(Location, on_delete=models.CASCADE, verbose_name="Location")
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="position_assignments",
                                 verbose_name="Employee")
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(blank=True, null=True)
    salary = models.DecimalField(max_digits=11, decimal_places=2, default=Decimal(0))
    status_choices = [
        ('open', 'Active'),
        ('closed', 'Terminated'),
        ('inactive', 'Suspended'),
    ]
    status = models.CharField(max_length=10, choices=status_choices, default='open')
    TYPE_CHOICES = [
        ("FULL TIME", "Full Time"),
        ("PART TIME", "Part Time"),
        ("CONTRACT", "Contract"),
    ]
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='FULL TIME')
    TERMINATION_REASON_CHOICES = [
        ("NEW POSITION", "New Position"),
        ("DISCIPLINARY", "Disciplinary")
    ]
    termination_reason = models.CharField(max_length=50, choices=TERMINATION_REASON_CHOICES, default='NEW POSITION')
    termination_description = models.TextField(blank=True, null=True)
    workflow = models.ForeignKey("Workflow", on_delete=models.CASCADE, related_name="job_assignments",
                                 verbose_name="Onboarding Workflow")

    def clean(self):
        if getattr(self, "position_id"):
            if self.salary > self.position.salaryMax or self.salary < self.position.salaryMin:
                raise ValidationError({
                    "salary": f"Salary is invalid, Should be between ${self.position.salaryMin} - ${self.position.salaryMax}"})

        if self.start_date and timezone.now() > self.start_date:
            raise ValidationError({"start_date": "Date cannot be in the past"})

        if self.end_date and timezone.now() > self.end_date:
            raise ValidationError({"end_date": "Date cannot be in the past"})

        if self.end_date and self.start_date and self.start_date > self.end_date:
            raise ValidationError({"end_date": "Date cannot be before start date"})

        if self.type in ["CONTRACT", "PART TIME"] and self.end_date in ["", None]:
            raise ValidationError({"end_date": "End date cannot be empty for contracts and part time"})

        if self.type in ["FULL TIME"]:
            self.end_date = None
        return super().clean()

    def __str__(self):
        return f"{self.position}: {self.employee}"

    class Meta:
        verbose_name = "Job Assignment"
        verbose_name_plural = "Job Assignments"


class Workflow(BaseModel):
    name = models.CharField(max_length=255)  # E.g., 'Before First Day', 'Paper Work - First Week on the Job'
    description = models.TextField(blank=True, null=True)  # Optional description for workflow phase

    def __str__(self):
        return self.name


class Task(BaseModel):
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, related_name="tasks")
    name = models.CharField(max_length=255)  # Task name (e.g., 'Prepare welcome kit', 'Training')
    description = models.TextField(blank=True, null=True, verbose_name="Task Description")
    type_choices = [
        ('file', 'File Upload'),
        ('meeting', 'Meeting'),
        ('interview', 'Interview'),
        ('training', 'Training Session'),
    ]
    task_type = models.CharField(max_length=10, choices=type_choices)  # Type of task
    stage_choices = [
        ('pre-onboarding', 'Pre-Onboarding'),
        ('onboarding', 'Onboarding'),
    ]
    days = models.PositiveIntegerField(default=0, verbose_name="Days from Start Date")
    hours = models.PositiveIntegerField(default=0, verbose_name="Hours from Start Date")
    minutes = models.PositiveIntegerField(default=0, verbose_name="Hours from Start Date")
    stage = models.CharField(max_length=14, default="pre-onboarding", choices=stage_choices)
    document_name = models.FileField(max_length=255, upload_to="tasks/documents", blank=True,
                                     null=True,
                                     verbose_name="Instruction Document")  # Optional document associated with the task
    created_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True)  # Who created the task

    def save(self, *args, **kwargs):
        if self.stage == 'pre-onboarding':
            self.days = 0
        return super(Task, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.workflow.name})"


class AssignmentQuerySet(models.query.QuerySet):
    def pending(self):
        return self.filter(status="Pending")

    def submitted(self):
        return self.filter(status="Submitted")

    def done(self):
        return self.filter(status="Done")


class Assignment(BaseModel):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="assignments")
    assigned_to = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="assignments")
    due_date = models.DateTimeField()
    STATUS_CHOICES = [
        ('Pending', 'Not Done'),
        ('Submitted', 'Pending'),
        ('Done', 'Done')
    ]
    file_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="File Name")
    file = models.FileField(upload_to='documents/', blank=True, null=True,
                            verbose_name="File")  # Path to the uploaded document

    day_before_notification = models.BooleanField(default=False)
    hours_before_notification = models.BooleanField(default=False)
    hours_after_notification = models.BooleanField(default=False)
    day_after_notification = models.BooleanField(default=False)
    status = models.CharField(max_length=14, choices=STATUS_CHOICES, default='Pending')

    objects = AssignmentQuerySet.as_manager()

    def __str__(self):
        return f"{self.task.name} - {self.assigned_to}"

    class Meta:
        verbose_name = "Assignment"
        verbose_name_plural = "Assignments"
        unique_together = ("task", "assigned_to")
        ordering = ["-status", "due_date"]


class NotificationQuerySet(models.query.QuerySet):
    def unsent(self):
        return self.filter(emailed=False)

    def sent(self):
        return self.filter(emailed=True)

    def unread(self, include_deleted=False):
        """Return only unread items in the current queryset"""
        return self.filter(unread=True, deleted=False)

    def read(self, include_deleted=False):
        """Return only read items in the current queryset"""
        return self.filter(unread=False, deleted=False)

    def mark_all_as_read(self, recipient=None):
        qset = self.unread(True)
        if recipient:
            qset = qset.filter(recipient=recipient)

        return qset.update(unread=False)

    def mark_all_as_unread(self, recipient=None):
        """Mark as unread any read messages in the current queryset.

        Optionally, filter these by recipient first.
        """
        qset = self.read(True)

        if recipient:
            qset = qset.filter(recipient=recipient)

        return qset.update(unread=True)

    def deleted(self):
        return self.filter(deleted=True)

    def active(self):
        return self.filter(deleted=False)

    def mark_all_as_deleted(self, recipient=None):
        qset = self.active()
        if recipient:
            qset = qset.filter(recipient=recipient)

        return qset.update(deleted=True)

    def mark_all_as_active(self, recipient=None):
        qset = self.deleted()
        if recipient:
            qset = qset.filter(recipient=recipient)

        return qset.update(deleted=False)

    def mark_as_unsent(self, recipient=None):
        qset = self.sent()
        if recipient:
            qset = qset.filter(recipient=recipient)
        return qset.update(emailed=False)

    def mark_as_sent(self, recipient=None):
        qset = self.unsent()
        if recipient:
            qset = qset.filter(recipient=recipient)
        return qset.update(emailed=True)


class Notification(BaseModel):
    LEVELS_CHOICES = [('success', "Success"), ('info', "info"), ('warning', "Warning"), ('error', "Danger")]
    level = models.CharField(verbose_name='Level', choices=LEVELS_CHOICES, default="success", max_length=20)
    subject = models.CharField("Subject", max_length=255, default="Subject")
    description = models.TextField("Description", default="Description")
    recipient = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='notifications',
                                  verbose_name='Recipient', blank=False, )
    unread = models.BooleanField(verbose_name='Unread', default=True, db_index=True)
    author = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='sent_notifications',
                               verbose_name='Author', blank=False, )
    public = models.BooleanField(verbose_name='public', default=True, db_index=True)
    deleted = models.BooleanField(verbose_name='deleted', default=False, db_index=True)
    emailed = models.BooleanField(verbose_name='emailed', default=False, db_index=True)

    data = models.JSONField(verbose_name='data', blank=True, null=True)

    objects = NotificationQuerySet.as_manager()

    class Meta:
        ordering = ("-unread", '-createdAt',)
        verbose_name = "Notification"
        verbose_name_plural = 'Notifications'

    @property
    def timesince(self, now=None):
        from django.utils.timesince import timesince as timesince_
        return timesince_(self.createdAt, now)

    @property
    def slug(self):
        return id2slug(self.id)

    def mark_as_read(self):
        if self.unread:
            self.unread = False
            self.save()

    def mark_as_unread(self):
        if not self.unread:
            self.unread = True
            self.save()


class SurveyHeading(BaseModel):
    name = models.CharField(max_length=255, )
    ordinal = models.IntegerField(unique=True, default=1)

    def __str__(self):
        return str(self.ordinal) + ". " + self.name.upper()

    @property
    def field_names(self):
        return [field.name for field in self.survey_fields.all()]

    class Meta:
        verbose_name = "Survey Heading"
        verbose_name_plural = "Survey Headings"
        ordering = ['ordinal']


class SurveyField(BaseModel):
    heading = models.ForeignKey(SurveyHeading, on_delete=models.CASCADE, related_name='survey_fields')
    name = models.CharField(max_length=255, unique=True, editable=False)
    type = models.CharField(max_length=50, choices=[
        ('D', 'Date'),
        ('B', 'Boolean'),
        ('E', 'Date Time'),
        ('T', 'Short Text'),
        ('L', 'Long Text'),
        # ('X', 'Multiple Choice'),
        ('N', 'Number'),
        ('S', 'Select Choice'),
        ('R', 'Radio Choice'),
    ])
    cssClass = models.CharField(max_length=255, blank=True, null=True, default="col-12 col-sm-6",
                                verbose_name="Css Classes")
    label = models.CharField(max_length=255)
    helpText = models.CharField(max_length=255, null=True, blank=True)
    placeholder = models.CharField(max_length=255, null=True, blank=True)
    active = models.BooleanField(default=False)
    required = models.BooleanField(default=False)
    allowCustom = models.BooleanField(default=False)
    dp = models.PositiveIntegerField(default=0)
    minimum = models.DecimalField(default=0, max_digits=11, decimal_places=3)
    maximum = models.DecimalField(default=0, max_digits=11, decimal_places=3)
    ordinal = models.IntegerField(unique=True, default=1)

    def __str__(self):
        return str(self.ordinal) + ". " + self.name.upper() + " - " + self.label.upper()

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = ''.join(random.choice(string.ascii_lowercase) for _ in range(10))
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Survey Field"
        verbose_name_plural = "Survey Fields"
        ordering = ['ordinal']


class SurveyFieldChoice(BaseModel):
    field = models.ForeignKey(SurveyField, on_delete=models.CASCADE, related_name="choices")
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = "Survey Field Choice"
        verbose_name_plural = "Survey Field Choices"
        unique_together = ['field', 'name']
        ordering = ['field', 'name']


class SurveyRecord(BaseModel):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="surveys")

    class Meta:
        ordering=["-createdAt"]
        verbose_name = "Survey Record"
        verbose_name_plural = "Survey Records"

class SurveyRecordValue(BaseModel):
    record = models.ForeignKey(SurveyRecord, on_delete=models.CASCADE, related_name="values")
    field = models.ForeignKey(SurveyField, on_delete=models.CASCADE, related_name="values")
    textValue = models.TextField(blank=True, null=True)
    numberValue = models.DecimalField(decimal_places=3, max_digits=11, null=True, blank=True)

    def __str__(self):
        if self.field.type == "N":
            return self.field.name + " : " + str(self.numberValue)
        else:
            return self.field.name + " : " + str(self.textValue)

    class Meta:
        unique_together = ["record", "field"]


@receiver(post_save, sender=Employee)
def send_password_to_user(sender, instance, created, **kwargs):
    if created and not instance.password:
        # Generate a random password
        password = Employee.objects.make_random_password()

        # Set the password for the new user
        instance.set_password(password)
        instance.save()

        # Send email with the password to the user
        send_mail(
            subject="Your Account Has Been Created",
            message=f"Hello {instance.username},\n\nYour account has been created. Your password is: {password}\n\nPlease log in and change your password.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[instance.email],
            fail_silently=False,
        )


@receiver(post_save, sender=JobAssignments)
def assign_to_employee(sender, instance, created, **kwargs):
    if created:
        employee = instance.employee
        employee.active_assignment = instance
        employee.save()


@receiver(post_save, sender=Assignment)
def notify_admin_about_file_upload(sender, instance: Assignment, created, **kwargs):
    if instance.status == "Submitted":
        link = reverse("app_tasks_details", kwargs={"pk": instance.id})
        admins_and_hr = Employee.objects.filter(
            Q(role__in=["ADMIN", "HR OFFICER"]) &
            Q(is_active=True)
        )
        subject = "New File Upload"
        description = f"{instance.assigned_to} has sent a file for {instance.task.name}. Please review and approve it."
        for admin in admins_and_hr:
            notify(recipient=admin, subject=subject, description=description, author=instance.assigned_to,
                   data={"link": link, "icon": "fas fa-wrench"})
    if instance.status == "Pending":
        link = reverse("app_tasks_personal_details", kwargs={"pk": instance.id})
        subject = "New Onboarding Task Assigned"
        description = f"You have a new onboarding task {instance.task.name}. Please attend to it."
        notify(recipient=instance.assigned_to, subject=subject, description=description,
               author=instance.assigned_to,
               data={"link": link, "icon": "fas fa-wrench"})

    if instance.status == "Done":
        link = reverse("app_tasks_personal_details", kwargs={"pk": instance.id})

        subject = "Onboarding Task Done"
        description = f"Your onboarding task: {instance.task.name} now set to done."
        notify(recipient=instance.assigned_to, subject=subject, description=description,
               author=instance.assigned_to, data={"link": link, "icon": "fas fa-wrench"})

        if instance.assigned_to.onboarding_percentage == 100 or instance.assigned_to.pre_onboarding_percentage == 100:
            link = reverse("app_personal_surveys_news")

            subject = "Onboarding Survey"
            description = f"{instance.assigned_to.first_name}, you have completed onboarding task. Please let us know about how you feel about this onboarding process"
            notify(recipient=instance.assigned_to, subject=subject, description=description,
                   author=instance.assigned_to, data={"link": link, "icon": "fas fa-wrench"})


def notify(**kwargs):
    Notification.objects.create(**kwargs)
