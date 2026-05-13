from django.db import models
from django.contrib.auth.models import User


class TaskStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    IN_PROGRESS = "in_progress", "In Progress"
    REVIEW = "review", "Review"
    DONE = "done", "Done"


class TaskPriority(models.TextChoices):
    LOW = "low", "Low"
    MEDIUM = "medium", "Medium"
    HIGH = "high", "High"
    VERY_HIGH = "very_high", "Very High"

# Valid next states for each current state
VALID_TRANSITIONS = {
    TaskStatus.DRAFT.value: {TaskStatus.IN_PROGRESS.value},
    TaskStatus.IN_PROGRESS.value: {TaskStatus.REVIEW.value},
    TaskStatus.REVIEW.value: {TaskStatus.DONE.value, TaskStatus.IN_PROGRESS.value},
    TaskStatus.DONE.value: set(),
}


class Task(models.Model):
    id = int
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    status = models.CharField(
        max_length=20,
        choices=TaskStatus.choices,
        default=TaskStatus.DRAFT,
        db_index=True,  # Speeds up status filtering
    )
    priority = models.CharField(
        max_length=10,
        choices=TaskPriority.choices,
        default=TaskPriority.MEDIUM,
        db_index=True,  # Speeds up priority filtering
    )
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="created_tasks"
    )
    
    updated_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name="updated_tasks"
    )

    review_comments = models.TextField(blank=True, default="")

    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tasks",
    )
    due_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Task"
        verbose_name_plural = "Tasks"

    def __str__(self):
        return f"[{self.status.upper()}] {self.title}"
