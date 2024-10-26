# tasks.py
from background_task import background

from core.helpers.task_reminder import remind_tasks


@background(schedule=60)  # Run every hour
def remind_tasks_background():
    remind_tasks()

# To schedule the task to run every hour
remind_tasks_background(repeat=Task.HOURLY)
