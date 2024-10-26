from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Employee, JobOffering, JobAssignments, JobApplication, Assignment, SurveyField


class RegistrationForm(UserCreationForm):
    first_name = forms.CharField(label='First Name', max_length=50, required=True)
    nationalIdNo = forms.CharField(label='National ID No', max_length=50, required=True)
    last_name = forms.CharField(label='Last Name', max_length=50, required=True)
    email = forms.EmailField(label='Email', required=True)
    phone = forms.CharField(label='Phone Number', max_length=50, required=True)
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Password'}),
    )
    password2 = forms.CharField(
        label="Password Confirmation",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Password Confirmation'}),
    )

    class Meta:
        model = Employee
        fields = [
            "nationalIdNo",
            "first_name",
            "username",
            "email",
            "last_name",
            "phone",
            "sex",
            "date_of_birth",
        ]

        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'email': forms.EmailInput(attrs={
                'placeholder': 'Email'
            })
        }


class JobOfferingForm(forms.ModelForm):
    class Meta:
        model = JobOffering
        exclude = ["publish_date", "job_id", "status"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
            "locations": forms.CheckboxSelectMultiple(),
            "due_date": forms.DateInput(attrs={'type': 'datetime-local'}),
        }


class EmployeeForm(forms.ModelForm):
    first_name = forms.CharField(label='First Name', max_length=50, required=True)
    nationalIdNo = forms.CharField(label='National ID No', max_length=50, required=True)
    last_name = forms.CharField(label='Last Name', max_length=50, required=True)
    email = forms.EmailField(label='Email', required=True)
    phone = forms.CharField(label='Phone Number', max_length=50, required=True)
    date_of_birth = forms.DateField(label='Date Of Birth', widget=forms.DateInput(attrs={'type': 'date'}),
                                    required=True)

    class Meta:
        model = Employee
        fields = [
            "profilePhoto",
            "nationalIdNo",
            "first_name",
            "username",
            "email",
            "last_name",
            "phone",
            "sex",
            "date_of_birth",
            "address_line_1",
            "address_line_2",
        ]

        # widgets = {
        #     "date_of_birth": ,
        # }


class JobAssignmentForm(forms.ModelForm):
    class Meta:
        model = JobAssignments
        exclude = ["employee", "status", "termination_reason", "termination_description"]
        widgets = {
            "job_offering": forms.HiddenInput(),
            "locations": forms.CheckboxSelectMultiple(),
            "start_date": forms.DateInput(attrs={'type': 'datetime-local'}),
            "end_date": forms.DateInput(attrs={'type': 'datetime-local'}),
        }


class JobApplicationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(JobApplicationForm, self).__init__(*args, **kwargs)

    class Meta:
        model = JobApplication
        fields = "__all__"


class DocumentUploadForm(forms.ModelForm):
    file = forms.FileField(widget=forms.FileInput(), required=True)
    file_name = forms.CharField(widget=forms.TextInput(), required=True)

    class Meta:
        model = Assignment
        fields = [
            "file_name",
            "file"
        ]


class TaskApprovalForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ["status"]


class SurveyForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in SurveyField.objects.filter(active=True):
            if field.type == "N":
                self.fields[field.name] = forms.DecimalField(
                    max_digits=11,
                    decimal_places=field.dp,
                    required=field.required,
                    label=field.label,
                    max_value=field.maximum, min_value=field.minimum,
                    widget=forms.NumberInput(
                        attrs={
                            "type": "number",
                            "cssClasses": "text-right " + field.cssClass,
                        }),
                )
            elif field.type == "D":
                self.fields[field.name] = forms.DateField(
                    required=field.required,
                    widget=forms.DateInput(
                        attrs={
                            "type": "date",
                            "cssClasses": field.cssClass,
                        }),
                    label=field.label
                )
            elif field.type == "B":
                self.fields[field.name] = forms.BooleanField(
                    required=field.required,
                    label=field.label,
                    widget=forms.CheckboxInput(
                        attrs={
                            "cssClasses": field.cssClass,
                            "type": "checkbox"
                        }
                    )
                )
            elif field.type == "T":
                self.fields[field.name] = forms.CharField(
                    required=field.required,
                    max_length=255,
                    label=field.label,
                    widget=forms.TextInput(
                        attrs={
                            "cssClasses": field.cssClass,
                            "type": "text",
                            "placeholder": field.placeholder
                        }
                    )
                )
            elif field.type == "L":
                self.fields[field.name] = forms.CharField(
                    required=field.required,
                    label=field.label,
                    widget=forms.Textarea(
                        attrs={
                            "cssClasses": field.cssClass,
                            "rows": "3",
                            "placeholder": field.placeholder
                        }
                    )
                )

            elif field.type == "S":
                self.fields[field.name] = forms.ChoiceField(
                    choices=[(c.name, c.name) for c in field.choices.all()],
                    required=field.required,
                    label=field.label,
                    widget=forms.Select(attrs={
                        "cssClasses": field.cssClass,
                    })
                )

            elif field.type == "R":
                self.fields[field.name] = forms.ChoiceField(
                    choices=[(c.name, c.name) for c in field.choices.all()],
                    required=field.required,
                    label=field.label,
                    widget=forms.RadioSelect(
                        attrs={
                            "cssClasses": field.cssClass,
                        }
                    )
                )

            elif field.type == "E":
                self.fields[field.name] = forms.DateTimeField(
                    label=field.label,
                    widget=forms.DateTimeInput(
                        attrs={
                            "type": "datetime-local",
                            "cssClasses": field.cssClass,
                        }),
                    required=field.required,
                )
