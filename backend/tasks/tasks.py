from celery import shared_task
from django.core.mail import send_mail
from .models import Task


@shared_task
def notify_review_task(task_id):
    try:
        # select_related avoids extra database hits for user emails
        task = Task.objects.select_related("created_by", "assigned_to").get(id=task_id)

        subject = f"Action Required: Task '{task.title}' is ready for review"
        message = (
            f"Hello {task.created_by.username},\n\n"
            f"User {task.assigned_to} has submitted the task "
            f"'{task.title}' for your approval.\n\n"
            f"View it here: http://localhost:8000/api/v1/tasks/{task.id}"
        )

        send_mail(
            subject,
            message,
            "noreply@taskmanager.com",
            [task.created_by.email],
            fail_silently=False,
        )
        return f"Notification sent for Task {task_id}"
    except Task.DoesNotExist:
        return f"Task {task_id} not found"
