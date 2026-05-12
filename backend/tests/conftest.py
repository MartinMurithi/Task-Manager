import pytest
from django.core.management import (
    call_command,
)


# scope="session" means: "Run ONCE for the entire test suite, not before every single test"
@pytest.fixture(scope="session")
def django_db_setup(django_db_blocker):
    """Ensure DB is ready before tests."""

    # pytest-django blocks DB access by default to prevent accidental data corruption.
    # .unblock() temporarily lifts this restriction inside the `with` block.
    with django_db_blocker.unblock():
        call_command("migrate", verbosity=0)
