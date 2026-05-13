import pytest
import pytest

from datetime import timedelta
from django.contrib.auth.models import User
from ninja_jwt.tokens import RefreshToken
from django.core.management import (
    call_command,
)


@pytest.fixture(autouse=True)
def force_settings(settings):
    settings.SECRET_KEY = "elqmat&3@f3$72zmpvjuoj6$gmwq8_u)8n-b+mw2lqlou4@1_"
    settings.NINJA_JWT = {
        "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
        "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
        "AUTH_HEADER_TYPES": ("Bearer",),
        "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    }


# scope="session" means: "Run ONCE for the entire test suite, not before every single test"
@pytest.fixture(scope="session")
def django_db_setup(django_db_blocker):
    """Ensure DB is ready before tests."""

    # pytest-django blocks DB access by default to prevent accidental data corruption.
    # .unblock() temporarily lifts this restriction inside the `with` block.
    with django_db_blocker.unblock():
        call_command("migrate", verbosity=0)


@pytest.fixture
def test_user(db):
    """The Assigner/Creator."""
    return User.objects.create_user(username="assigner", password="password123")


@pytest.fixture
def user_two(db):
    """The Assignee."""
    return User.objects.create_user(username="assignee", password="password123")


@pytest.fixture
def auth_client(client, test_user):
    """Client authenticated as the Assigner."""
    token = str(RefreshToken.for_user(test_user).token)
    client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {token}"
    return client
