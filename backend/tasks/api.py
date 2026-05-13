from typing import List
from django.contrib.auth.models import User
from ninja import Router, Query as NinjaQuery
from ninja_jwt.authentication import JWTAuth
from ninja.errors import HttpError
from django.shortcuts import get_object_or_404
from django.db.models import Q
from tasks.models import VALID_TRANSITIONS, Task, TaskStatus
from tasks.schemas import (
    TaskCreateSchema,
    TaskUpdateSchema,
    TaskOutSchema,
    TaskFilterSchema,
    UserListSchema,
)

router = Router(tags=["Tasks"])


# --- USER DISCOVERY ---
@router.get("/users", response=List[UserListSchema], auth=JWTAuth())
def list_assignable_users(request):
    """Allows Assigners to see a list of names to assign tasks to."""
    return User.objects.exclude(id=request.user.id)


@router.get("/", response=List[TaskOutSchema], auth=JWTAuth())
def list_tasks(request, filters: NinjaQuery[TaskFilterSchema]):
    # Apply "Privacy" wall (Only mine or assigned to me)
    tasks_query = Task.objects.filter(
        Q(created_by=request.user) | Q(assigned_to=request.user)
    )

    # Add dynamic filters from the Schema
    if filters.status:
        tasks_query = tasks_query.filter(status=filters.status)

    if filters.priority:  # NEW
        tasks_query = tasks_query.filter(priority=filters.priority)

    if filters.assigned_to_id:  # NEW
        tasks_query = tasks_query.filter(assigned_to_id=filters.assigned_to_id)

    return tasks_query.order_by("-created_at")


@router.patch("/{task_id}", response=TaskOutSchema, auth=JWTAuth())
def update_task(request, task_id: int, payload: TaskUpdateSchema):
    from tasks.tasks import notify_review_task

    task = get_object_or_404(Task, id=task_id)
    user = request.user
    update_data = payload.model_dump(exclude_unset=True)

    # Permission & Role Checks
    is_creator = task.created_by == user.id
    is_assignee = task.assigned_to == user.id

    if not is_creator and not is_assignee:
        raise HttpError(
            403,
            "Unauthorized: You can only update tasks you created or are assigned to.",
        )

    if is_assignee and not is_creator:
        # Assignees can ONLY submit for review
        if (
            set(update_data.keys()) != {"status"}
            or update_data.get("status") != TaskStatus.REVIEW
        ):
            raise HttpError(403, "Assignees can only change status to 'review'.")

    # Validate Status Transition
    new_status = update_data.get("status")
    if new_status and new_status != task.status:
        status_val = new_status.value if hasattr(new_status, "value") else new_status
        allowed = VALID_TRANSITIONS.get(task.status, set())
        if status_val not in allowed:
            raise HttpError(400, f"Invalid transition: {task.status} → {status_val}")

    # Apply Updates
    fields_to_update = set(update_data.keys())

    for field, value in update_data.items():
        setattr(task, field, value)

    # Auto-set review comments on approval
    if new_status == TaskStatus.DONE:
        task.review_comments = "Approved"
        fields_to_update.add("review_comments")

    # Track who updated it
    task.updated_by = user
    fields_to_update.add("updated_by")
    fields_to_update.add("updated_at")

    task.save(update_fields=list(fields_to_update))

    # Trigger async notification if moved to REVIEW
    if new_status == TaskStatus.REVIEW:
        notify_review_task(task.id)

    return task


@router.post("/", response=TaskOutSchema, auth=JWTAuth())
def create_task(request, payload: TaskCreateSchema):
    return Task.objects.create(**payload.model_dump(), created_by=request.user)


@router.delete("/{task_id}", auth=JWTAuth())
def delete_task(request, task_id: int):
    # Only creator can delete
    task = get_object_or_404(Task, id=task_id, created_by=request.user)
    task.delete()
    return {"success": True}
