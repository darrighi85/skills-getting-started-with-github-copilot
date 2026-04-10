"""Tests for POST /activities/{activity_name}/unregister endpoint."""

import pytest


class TestUnregister:
    """Test the unregister endpoint for removing students from activities."""

    def test_unregister_success(self, client, clean_activities):
        """
        Arrange: Student already signed up for an activity
        Act: POST to unregister that student
        Assert: Returns 200 with unregister confirmation
        """
        email = "michael@mergington.edu"  # Already in Chess Club
        response = client.post(
            "/activities/Chess Club/unregister",
            params={"email": email}
        )
        
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]
        assert email in response.json()["message"]

    def test_unregister_removes_participant(self, client, clean_activities):
        """
        Arrange: Student signed up for an activity
        Act: Unregister the student
        Assert: Student no longer appears in participants
        """
        # First signup
        email = "newstudent@mergington.edu"
        client.post("/activities/Art Studio/signup", params={"email": email})
        
        # Verify signup succeeded
        response = client.get("/activities")
        assert email in response.json()["Art Studio"]["participants"]
        
        # Now unregister
        client.post("/activities/Art Studio/unregister", params={"email": email})
        
        # Verify removed
        response = client.get("/activities")
        assert email not in response.json()["Art Studio"]["participants"]

    def test_unregister_student_not_registered_fails(self, client, clean_activities):
        """
        Arrange: Student not signed up for activity
        Act: POST unregister for a student not in the activity
        Assert: Returns 400 with not registered error
        """
        email = "notregistered@test.edu"
        response = client.post(
            "/activities/Soccer Club/unregister",
            params={"email": email}
        )
        
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"].lower()

    def test_unregister_invalid_activity_fails(self, client, clean_activities):
        """
        Arrange: Non-existent activity name
        Act: POST /activities/Fake Activity/unregister
        Assert: Returns 404 not found
        """
        response = client.post(
            "/activities/Fake Activity/unregister",
            params={"email": "student@test.edu"}
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_unregister_missing_email_parameter_fails(self, client, clean_activities):
        """
        Arrange: No email parameter provided
        Act: POST /activities/Basketball Team/unregister without email
        Assert: Returns 422 validation error
        """
        response = client.post("/activities/Basketball Team/unregister")
        
        assert response.status_code == 422  # Validation error

    def test_unregister_then_signup_again_succeeds(self, client, clean_activities):
        """
        Arrange: Student is registered, then unregisters
        Act: Try to signup again for the same activity
        Assert: Can successfully re-signup
        """
        email = "recycled@test.edu"
        
        # First signup
        response1 = client.post(
            "/activities/Science Club/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Unregister
        response2 = client.post(
            "/activities/Science Club/unregister",
            params={"email": email}
        )
        assert response2.status_code == 200
        
        # Re-signup should succeed
        response3 = client.post(
            "/activities/Science Club/signup",
            params={"email": email}
        )
        assert response3.status_code == 200

    @pytest.mark.parametrize("activity_name", [
        "Chess Club",
        "Basketball Team",
        "Music Band",
        "Debate Team"
    ])
    def test_unregister_from_multiple_activities(self, client, clean_activities, activity_name):
        """
        Arrange: Student signed up for multiple activities
        Act: Unregister from each activity
        Assert: Student successfully removed from all activities
        """
        email = "multiactivity@test.edu"
        
        # Signup for multiple
        for activity in [activity_name, "Gym Class", "Programming Class"]:
            client.post(f"/activities/{activity}/signup", params={"email": email})
        
        # Unregister from specific activity
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        assert response.status_code == 200
        
        # Verify removed from that activity but still in others
        activities_resp = client.get("/activities")
        activities = activities_resp.json()
        assert email not in activities[activity_name]["participants"]
        assert email in activities["Gym Class"]["participants"]
        assert email in activities["Programming Class"]["participants"]

    def test_unregister_original_participant(self, client, clean_activities):
        """
        Arrange: Student originally in activities (from app.py initial state)
        Act: Unregister an original participant
        Assert: Successfully removed from participants list
        """
        email = "daniel@mergington.edu"  # Original Chess Club participant
        
        # Verify participant is there initially
        response = client.get("/activities")
        assert email in response.json()["Chess Club"]["participants"]
        
        # Unregister
        response = client.post(
            "/activities/Chess Club/unregister",
            params={"email": email}
        )
        assert response.status_code == 200
        
        # Verify removed
        response = client.get("/activities")
        assert email not in response.json()["Chess Club"]["participants"]
