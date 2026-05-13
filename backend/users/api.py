from typing import List
from django.contrib.auth.models import User
from ninja import Router
from ninja_jwt.authentication import JWTAuth
from users.schemas import RegisterSchema, UserOutSchema

router = Router(tags=["Users & Auth"])


# PUBLIC: Anyone can create an account
@router.post("/register", response=UserOutSchema)
def register(request, data: RegisterSchema):
    # Creates the user in the built-in Django User table
    user = User.objects.create_user(
        username=data.username, email=data.email, password=data.password
    )
    return user


# PROTECTED: Only logged-in users can see other users to assign tasks
@router.get("/list", response=List[UserOutSchema], auth=JWTAuth())
def list_users(request):
    """Returns all users except the one currently logged in."""
    return User.objects.exclude(id=request.user.id)
