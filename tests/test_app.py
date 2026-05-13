import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


class TestRootEndpoint:
    def test_get_root_redirects_to_static_index(self):
        # Arrange: No special setup needed

        # Act: Make GET request to root without following redirects
        response = client.get("/", follow_redirects=False)

        # Assert: Should redirect to /static/index.html
        assert response.status_code == 307  # Temporary redirect
        assert response.headers["location"] == "/static/index.html"


class TestActivitiesEndpoint:
    def test_get_activities_returns_all_activities(self):
        # Arrange: No special setup needed

        # Act: Make GET request to /activities
        response = client.get("/activities")

        # Assert: Should return 200 and activities dict
        assert response.status_code == 200
        activities = response.json()
        assert isinstance(activities, dict)
        assert len(activities) == 9  # We have 9 activities

        # Check structure of first activity
        first_activity = next(iter(activities.values()))
        assert "description" in first_activity
        assert "schedule" in first_activity
        assert "max_participants" in first_activity
        assert "participants" in first_activity
        assert isinstance(first_activity["participants"], list)


class TestSignupEndpoint:
    def test_signup_successful_for_new_student(self):
        # Arrange: Use an activity that exists and a new email
        activity_name = "Chess Club"
        new_email = "newstudent@mergington.edu"

        # Act: Make POST request to signup
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_email}
        )

        # Assert: Should return 200 and success message
        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        assert f"Signed up {new_email} for {activity_name}" in result["message"]

        # Verify the student was added to the activity
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert new_email in activities[activity_name]["participants"]

    def test_signup_fails_for_nonexistent_activity(self):
        # Arrange: Use a non-existent activity
        invalid_activity = "NonExistent Activity"
        email = "student@mergington.edu"

        # Act: Make POST request to signup
        response = client.post(
            f"/activities/{invalid_activity}/signup",
            params={"email": email}
        )

        # Assert: Should return 404 with error message
        assert response.status_code == 404
        result = response.json()
        assert "detail" in result
        assert "Activity not found" in result["detail"]

    def test_signup_fails_for_duplicate_registration(self):
        # Arrange: Use an existing participant
        activity_name = "Chess Club"
        existing_email = "michael@mergington.edu"  # Already in Chess Club

        # Act: Make POST request to signup with existing email
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": existing_email}
        )

        # Assert: Should return 400 with error message
        assert response.status_code == 400
        result = response.json()
        assert "detail" in result
        assert "already signed up" in result["detail"].lower()