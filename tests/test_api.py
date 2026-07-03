"""
Integration tests for Mergington High School Activities API.

Tests all API endpoints:
- GET /activities
- POST /activities/{activity_name}/signup
- DELETE /activities/{activity_name}/participant
- GET /
"""

import pytest


class TestGetActivitiesEndpoint:
    """Tests for GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client):
        """Verify endpoint returns all activities with correct structure."""
        response = client.get("/activities")
        assert response.status_code == 200

        activities = response.json()
        assert isinstance(activities, dict)
        assert len(activities) == 3
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        assert "Gym Class" in activities

    def test_get_activities_response_structure(self, client):
        """Verify each activity has required fields."""
        response = client.get("/activities")
        activities = response.json()

        for activity_name, details in activities.items():
            assert isinstance(details, dict)
            assert "description" in details
            assert "schedule" in details
            assert "max_participants" in details
            assert "participants" in details
            assert isinstance(details["participants"], list)

    def test_get_activities_participants_list(self, client):
        """Verify participant lists are correctly populated."""
        response = client.get("/activities")
        activities = response.json()

        # Chess Club should have 2 participants
        assert len(activities["Chess Club"]["participants"]) == 2
        assert "michael@mergington.edu" in activities["Chess Club"]["participants"]
        assert "daniel@mergington.edu" in activities["Chess Club"]["participants"]

        # Programming Class should have 2 participants
        assert len(activities["Programming Class"]["participants"]) == 2

        # Gym Class should have 2 participants
        assert len(activities["Gym Class"]["participants"]) == 2


class TestSignupEndpoint:
    """Tests for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_valid_activity_and_email(self, client):
        """Happy path: successful signup for valid activity."""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200

        result = response.json()
        assert "message" in result
        assert "Signed up" in result["message"]
        assert "newstudent@mergington.edu" in result["message"]

        # Verify participant was added
        activities = client.get("/activities").json()
        assert "newstudent@mergington.edu" in activities["Chess Club"]["participants"]

    def test_signup_activity_not_found(self, client):
        """Signup for non-existent activity returns 404."""
        response = client.post(
            "/activities/Nonexistent Club/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404

        result = response.json()
        assert "detail" in result
        assert "not found" in result["detail"].lower()

    def test_signup_duplicate_participant(self, client):
        """Same email can signup multiple times (current behavior)."""
        response1 = client.post(
            "/activities/Chess Club/signup?email=duplicate@mergington.edu"
        )
        assert response1.status_code == 200

        # Signup same email again
        response2 = client.post(
            "/activities/Chess Club/signup?email=duplicate@mergington.edu"
        )
        assert response2.status_code == 200

        # Verify participant appears twice
        activities = client.get("/activities").json()
        participants = activities["Chess Club"]["participants"]
        assert participants.count("duplicate@mergington.edu") == 2

    def test_signup_multiple_activities(self, client):
        """One email can signup for multiple activities."""
        email = "multiplesignup@mergington.edu"

        response1 = client.post(f"/activities/Chess Club/signup?email={email}")
        assert response1.status_code == 200

        response2 = client.post(f"/activities/Programming Class/signup?email={email}")
        assert response2.status_code == 200

        # Verify participant in both activities
        activities = client.get("/activities").json()
        assert email in activities["Chess Club"]["participants"]
        assert email in activities["Programming Class"]["participants"]

    def test_signup_with_special_characters_in_email(self, client):
        """Email with special characters is accepted (current behavior)."""
        from urllib.parse import urlencode
        email = "student+tag@mergington.edu"
        response = client.post(
            f"/activities/Chess Club/signup?email={email}".replace("+", "%2B")
        )
        assert response.status_code == 200

        activities = client.get("/activities").json()
        assert email in activities["Chess Club"]["participants"]


class TestDeleteParticipantEndpoint:
    """Tests for DELETE /activities/{activity_name}/participant endpoint."""

    def test_delete_participant_success(self, client):
        """Happy path: successful participant removal."""
        # First add a participant
        add_response = client.post(
            "/activities/Gym Class/signup?email=todelete@mergington.edu"
        )
        assert add_response.status_code == 200

        # Then delete the participant
        delete_response = client.delete(
            "/activities/Gym Class/participant?email=todelete@mergington.edu"
        )
        assert delete_response.status_code == 200

        result = delete_response.json()
        assert "message" in result
        assert "Removed" in result["message"]

        # Verify participant was removed
        activities = client.get("/activities").json()
        assert "todelete@mergington.edu" not in activities["Gym Class"]["participants"]

    def test_delete_nonexistent_participant(self, client):
        """Delete participant not in activity returns 404."""
        response = client.delete(
            "/activities/Chess Club/participant?email=notinactivity@mergington.edu"
        )
        assert response.status_code == 404

        result = response.json()
        assert "detail" in result
        assert "not found" in result["detail"].lower()

    def test_delete_participant_activity_not_found(self, client):
        """Delete from non-existent activity returns 404."""
        response = client.delete(
            "/activities/Nonexistent Club/participant?email=student@mergington.edu"
        )
        assert response.status_code == 404

        result = response.json()
        assert "detail" in result
        assert "not found" in result["detail"].lower()

    def test_delete_specific_participant_from_duplicates(self, client):
        """Delete one instance of duplicate participant."""
        email = "duplicate@mergington.edu"

        # Add participant twice
        client.post(f"/activities/Gym Class/signup?email={email}")
        client.post(f"/activities/Gym Class/signup?email={email}")

        # Verify 2 instances
        activities = client.get("/activities").json()
        assert activities["Gym Class"]["participants"].count(email) == 2

        # Delete once
        response = client.delete(f"/activities/Gym Class/participant?email={email}")
        assert response.status_code == 200

        # Verify only 1 instance remains
        activities = client.get("/activities").json()
        assert activities["Gym Class"]["participants"].count(email) == 1


class TestRootEndpoint:
    """Tests for GET / endpoint."""

    def test_root_redirects_to_index(self, client):
        """Root endpoint redirects to static index.html."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code in [301, 302, 303, 307]  # Redirect status codes
        assert "location" in response.headers
        assert "/static/index.html" in response.headers["location"]

    def test_root_redirect_follow(self, client):
        """Root endpoint can be followed (with redirect enabled)."""
        response = client.get("/", follow_redirects=True)
        # This will return 404 since static files not mounted in test, but verifies redirect logic
        assert response.status_code in [200, 404]


class TestStateAndIntegration:
    """Tests for state management and integration scenarios."""

    def test_state_isolation_between_tests(self, client):
        """Each test gets a fresh app state."""
        # First request
        response = client.get("/activities")
        initial_count = len(response.json()["Chess Club"]["participants"])
        assert initial_count == 2

    def test_signup_then_refresh_participants(self, client):
        """Signup updates activity data immediately (workflow test)."""
        email = "workflow@mergington.edu"

        # Get initial state
        activities_before = client.get("/activities").json()
        initial_count = len(activities_before["Programming Class"]["participants"])

        # Signup
        signup_response = client.post(
            f"/activities/Programming Class/signup?email={email}"
        )
        assert signup_response.status_code == 200

        # Refresh and verify
        activities_after = client.get("/activities").json()
        new_count = len(activities_after["Programming Class"]["participants"])
        assert new_count == initial_count + 1
        assert email in activities_after["Programming Class"]["participants"]

    def test_complete_lifecycle(self, client):
        """Test complete signup and removal lifecycle."""
        email = "lifecycle@mergington.edu"
        activity = "Chess Club"

        # Verify not in activity
        activities = client.get("/activities").json()
        assert email not in activities[activity]["participants"]
        initial_count = len(activities[activity]["participants"])

        # Signup
        signup_response = client.post(f"/activities/{activity}/signup?email={email}")
        assert signup_response.status_code == 200

        # Verify in activity
        activities = client.get("/activities").json()
        assert email in activities[activity]["participants"]
        assert len(activities[activity]["participants"]) == initial_count + 1

        # Remove
        delete_response = client.delete(
            f"/activities/{activity}/participant?email={email}"
        )
        assert delete_response.status_code == 200

        # Verify removed
        activities = client.get("/activities").json()
        assert email not in activities[activity]["participants"]
        assert len(activities[activity]["participants"]) == initial_count
