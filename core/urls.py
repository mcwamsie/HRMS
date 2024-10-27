from django.urls import path

from core.views import HomeView, ProfileView, UserRegistrationView, ApplicationListView, JobOfferingListView, \
    NewJobOfferingView, JobOfferingDetailsView, EmployeeListView, NewEmployeeView, PersonalTaskListView, \
    JobApplicationView, PersonalTaskDetailsView, TaskListView, TaskDetailsView, index_view, EmployeeDetailsView, \
    NewSurveyView, NotificationListView, PersonalSurveyListView, PersonalSurveyDetailsView, SurveyListView, \
    SurveyDetailsView

urlpatterns = [
    #path('', IndexView.as_view(), name='index'),
    path('', index_view, name='index'),
    path('account/register/', UserRegistrationView.as_view(), name='register'),
    path('job-application/<uuid:pk>/', JobApplicationView.as_view(), name='application_create'),

    path('app/dashboard/', HomeView.as_view(), name='app_dashboard'),
    path('app/notifications/', NotificationListView.as_view(), name='app_notifications'),
    path('app/profile/', ProfileView.as_view(), name='app_profile'),
    path('app/applications/', ApplicationListView.as_view(), name='app_application_list'),

    path('app/job-offerings/', JobOfferingListView.as_view(), name='app_job_offerings_list'),
    path('app/job-offerings/new/', NewJobOfferingView.as_view(), name='app_job_offerings_new'),
    path('app/job-offerings/<uuid:pk>/', JobOfferingDetailsView.as_view(), name='app_job_offerings_details'),

    path('app/employees/', EmployeeListView.as_view(), name='app_employees_list'),
    path('app/employees/new/', NewEmployeeView.as_view(), name='app_employees_new'),
    path('app/employees/<uuid:pk>/', EmployeeDetailsView.as_view(), name='app_employees_details'),

    path('app/personal-tasks/', PersonalTaskListView.as_view(), name='app_tasks_personal_list'),
    path('app/personal-tasks/<uuid:pk>/', PersonalTaskDetailsView.as_view(), name='app_tasks_personal_details'),

    path('app/tasks/', TaskListView.as_view(), name='app_tasks_list'),
    path('app/tasks/<uuid:pk>/', TaskDetailsView.as_view(), name='app_tasks_details'),

    path('app/personal-surveys/', PersonalSurveyListView.as_view(), name='app_personal_surveys_list'),
    path('app/personal-surveys/new/', NewSurveyView.as_view(), name='app_personal_surveys_new'),
    path('app/personal-surveys/<uuid:pk>/', PersonalSurveyDetailsView.as_view(), name='app_personal_surveys_details'),

path('app/surveys/', SurveyListView.as_view(), name='app_surveys_list'),
    path('app/surveys/<uuid:pk>/', SurveyDetailsView.as_view(), name='app_surveys_details'),

    # path('^inbox/notifications/', include(notifications.urls, namespace='notifications')),
]
