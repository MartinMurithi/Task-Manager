import pytest
from tasks.models import Task, TaskStatus
from ninja_jwt.tokens import RefreshToken


@pytest.mark.django_db
class TestTaskAPI:

    def test_create_task(self, auth_client):
        """Verify assigner can create a task."""
        payload = {"title": "Build API", "priority": "high"}
        response = auth_client.post(
            "/api/v1/tasks/", data=payload, content_type="application/json"
        )
        assert response.status_code == 200
        assert response.json()["title"] == "Build API"

    def test_task_visibility_privacy(self, client, test_user, user_two):
        """Verify users ONLY see tasks they are involved in."""
        # Create a private task for User 1
        Task.objects.create(title="User 1 Secret", created_by=test_user)

        # Log in as User 2
        token = str(RefreshToken.for_user(user_two).token)
        client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {token}"

        response = client.get("/api/v1/tasks/")
        # User 2 should see 0 tasks because they aren't the creator or assignee
        assert len(response.json()) == 0

    def test_assignee_restricted_update(self, client, test_user, user_two):
        """Verify assignee can ONLY change status to 'review'."""
        task = Task.objects.create(
            id = 1, title="Work", created_by=test_user, assigned_to=user_two
        )

        token = str(RefreshToken.for_user(user_two).token)
        client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {token}"

        # Try to change title (Should be blocked/ignored by assignee logic)
        res_fail = client.patch(
            f"/api/v1/tasks/{task.id}",
            data={"title": "Hacked"},
            content_type="application/json",
        )
        assert res_fail.status_code == 403

        # Change status to review (Should work)
        res_success = client.patch(
            f"/api/v1/tasks/{task.id}",
            data={"status": "review"},
            content_type="application/json",
        )
        assert res_success.status_code == 200
        assert res_success.json()["status"] == "review"

    def test_denial_loop_with_comments(self, client, test_user, user_two):
        """Test the full denial flow: Assigner rejects with a reason."""
        task = Task.objects.create(
            title="Logo",
            created_by=test_user,
            assigned_to=user_two,
            status=TaskStatus.REVIEW,
        )

        # Login as Assigner (Creator)
        token = str(RefreshToken.for_user(test_user).token)
        client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {token}"

        # Deny and add comment
        payload = {"status": "in_progress", "review_comments": "Too blue."}
        response = client.patch(
            f"/api/v1/tasks/{task.id}", data=payload, content_type="application/json"
        )

        assert response.status_code == 200
        assert response.json()["status"] == "in_progress"
        assert response.json()["review_comments"] == "Too blue."

    def test_delete_permissions(self, client, test_user, user_two):
        """Verify ONLY the creator can delete a task."""
        task = Task.objects.create(
            title="Delete Me", created_by=test_user, assigned_to=user_two
        )

        # Assignee tries to delete
        token_assignee = str(RefreshToken.for_user(user_two).token)
        client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {token_assignee}"

        res = client.delete(f"/api/v1/tasks/{task.id}")
        assert res.status_code == 404  # Our API uses 404 for 'not found or not yours'
