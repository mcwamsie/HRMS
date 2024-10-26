# tasks.py
from django.utils import timezone
from notifications.signals import notify
from datetime import timedelta
from core.models import Assignment


def remind_tasks():
    now = timezone.now()

    # Check for tasks due a day before and notify if not already reminded
    day_before = now + timedelta(days=1)
    tasks_day_before = Assignment.objects.filter(due_date__date=day_before.date(), completed=False,
                                                   reminded_day_before=False)

    for task in tasks_day_before:
        notify.send(task, recipient=task.user, verb='Reminder: Your task is due tomorrow',
                    description=f'Task: {task.name} is due on {task.due_date}')
        task.reminded_day_before = True
        task.save()

    # Check for tasks due an hour before and notify if not already reminded
    hour_before = now + timedelta(hours=1)
    tasks_hour_before = Assignment.objects.filter(due_date__hour=hour_before.hour, completed=False,
                                                    reminded_hour_before=False)

    for task in tasks_hour_before:
        notify.send(task, recipient=task.user, verb='Reminder: Your task is due in an hour',
                    description=f'Task: {task.name} is due on {task.due_date}')
        task.reminded_hour_before = True
        task.save()

    # Check for overdue tasks and notify if not already reminded
    overdue_tasks = Assignment.objects.filter(due_date__lt=now, completed=False, overdue_notified=False)

    for task in overdue_tasks:
        notify.send(task, recipient=task.user, verb='Your task is overdue',
                    description=f'Task: {task.name} was due on {task.due_date}')
        task.overdue_notified = True
        task.save()
