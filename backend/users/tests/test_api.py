import pytest


@pytest.mark.django_db
class TestUserAuth:
    def test_registration_creates_user(self, client):
        payload = {
            "username": "tester",
            "email": "t@test.com",
            "password": "password123",
        }
        response = client.post(
            "/api/v1/users/register", data=payload, content_type="application/json"
        )
        assert response.status_code == 200
        assert response.json()["username"] == "tester"

    def test_user_list_requires_auth(self, client):
        response = client.get("/api/v1/users/list")
        assert response.status_code == 401  # Should fail without token
