# Task Manager API

A backend system for managing internal task workflows, featuring secure authentication, role-based permissions, and automated background notifications.

## System Components

- **API Framework**: Django Ninja
- **Database**: PostgreSQL 16
- **Authentication**: JWT (JSON Web Tokens)
- **Task Queue**: Celery with Redis
- **Containerization**: Docker and Docker Compose
- **Testing**: Pytest

## Workflow Rules

The system follows a strict accountability loop:
- **Assigners (Creators)**: Can create tasks and assign them to other users. They have the final authority to mark a task as "Done" or reject it with a reason.
- **Assignees**: Can view tasks assigned to them and move them to a "Review" state. They cannot bypass the review process or edit core task details.
- **Visibility**: Users only see tasks they created or those assigned specifically to them.

## Setup Instructions

### 1. Environment Configuration
Create a .env file in the root directory:
```text
DEBUG=1
SECRET_KEY=your_secret_key
DB_NAME=taskmanager
DB_USER=tm_user
DB_PASSWORD=supersecret
REDIS_URL=redis://tm_redis:6379/0
```

### 2. Launching with Docker
Build and start all services (API, Worker, Database, Redis):
```bash
docker compose up --build
```

### 3. Database Initialisation
Apply migrations to create the database schema:
```bash
docker compose exec api python manage.py migrate
```

## API Documentation

Once the services are running, the interactive documentation is available at:
`http://localhost:8000/api/v1/docs`

### Authentication Flow
1. Register a new account at `/api/v1/users/register`.
2. Obtain a token at `/api/v1/token/pair` using your credentials.
3. Use the access token in the Authorization header: `Bearer <token>`.

## Testing

Run the automated test suite to verify system integrity:
```bash
docker compose exec api pytest
```

The test suite covers:
- User registration and authorization.
- Task visibility and privacy rules.
- Permission enforcement for assigners and assignees.
- State transition validation.
