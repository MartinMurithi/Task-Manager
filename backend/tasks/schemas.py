from typing import Optional
from datetime import datetime
from ninja import Schema
from pydantic import ConfigDict
from tasks.models import TaskStatus, TaskPriority


class UserListSchema(Schema):
    id: int
    username: str


class TaskCreateSchema(Schema):
    title: str
    description: Optional[str] = ""
    status: TaskStatus = TaskStatus.DRAFT
    priority: TaskPriority = TaskPriority.MEDIUM
    assigned_to_id: Optional[int] = None
    due_date: Optional[datetime] = None


class TaskUpdateSchema(Schema):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    assigned_to_id: Optional[int] = None
    due_date: Optional[datetime] = None
    review_comments: Optional[str] = None


class TaskOutSchema(Schema):
    id: int
    title: str
    description: str
    status: str
    priority: str
    created_by_id: int
    assigned_to_id: Optional[int] = None
    due_date: Optional[datetime] = None
    review_comments: str
    created_at: datetime
    updated_at: datetime

    # Pydantic v2: enables ORM-to-JSON conversion
    model_config = ConfigDict(from_attributes=True)


class TaskFilterSchema(Schema):
    status: Optional[str] = None
    priority: Optional[str] = None
    assigned_to_id: Optional[int] = None
