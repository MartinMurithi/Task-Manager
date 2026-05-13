from django.urls import path
from ninja_extra import NinjaExtraAPI
from ninja_jwt.authentication import JWTAuth
from ninja_jwt.controller import NinjaJWTDefaultController
from users.api import router as users_router
from tasks.api import router as tasks_router

# Initialize NinjaExtraAPI
api = NinjaExtraAPI(
    title="Task Manager API",
    description="Internal task workflow system with JWT auth & Celery notifications",
    version="1.0.0",
    docs_url="/docs",
)

# Register the JWT Authentication routes (Login, Refresh, Verify)
# This adds: /api/v1/token/pair, /api/v1/token/refresh, etc.
api.register_controllers(NinjaJWTDefaultController)


api.add_router("/users", users_router)
api.add_router("/tasks", tasks_router)


# Public Endpoint (Health Check)
@api.get("/health", tags=["System"])
def health_check(request):
    """System health check."""
    return {"status": "healthy", "service": "task-manager-api"}


# Example Protected Endpoint (Only logged-in users can see this)
@api.get("/me", auth=JWTAuth(), tags=["User"])
def get_me(request):
    """Returns the current user's username."""
    return {"username": request.user.username}


urlpatterns = [
    path("api/v1/", api.urls),
]
