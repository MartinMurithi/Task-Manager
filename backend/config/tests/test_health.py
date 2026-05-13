import pytest
from django.test import Client


@pytest.mark.django_db
class TestHealthEndpoint:
    def test_health_returns_200(self):
        """Use the Client to simulate a real web request."""
        client = Client()
        # Use the full URL path defined in your urls.py
        response = client.get("/api/v1/health")

        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_swagger_docs_available(self):
        client = Client()
        response = client.get("/api/v1/docs")
        assert response.status_code == 200
