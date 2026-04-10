"""Tests for POST /activities/{activity_name}/signup endpoint."""

import pytest


class TestSignup:
    """Test the signup endpoint for registering students in activities."""

    def test_signup_success_valid_email(self, client, clean_activities):
        """
        Arrange: Prepare a new student email
        Act: POST /activities/Chess Club/signup with valid email
        Assert: Returns 200 and confirmation message
        """
        email = "newstudent@mergington.edu"
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        assert email in response.json()["message"]

    def test_signup_adds_participant(self, client, clean_activities):
        """
        Arrange: Verify initial participant count
        Act: POST /activities/Programming Class/signup
        Assert: Student appears in participants list
        """
        email = "newemail@mergington.edu"
        client.post("/activities/Programming Class/signup", params={"email": email})
        
        # Verify by getting activities
        response = client.get("/activities")
        activities = response.json()
        assert email in activities["Programming Class"]["participants"]

    def test_signup_duplicate_email_same_activity_fails(self, client, clean_activities):
        """
        Arrange: Student already signed up (michael@mergington.edu in Chess Club)
        Act: POST same email to signup for same activity again
        Assert: Returns 400 with duplicate error message
        """
        email = "michael@mergington.edu"  # Already in Chess Club
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()

    def test_signup_activity_at_capacity_fails(self, client, clean_activities):
        """
        Arrange: Activity has only 1 spot remaining (Debate Team has max 14)
        Act: Fill activity to capacity, then try to add one more
        Assert: Returns 400 with full activity error message
        """
        # Find an activity and fill it
        emails = [f"student{i}@test.edu" for i in range(20)]
        
        for email in emails[:13]:
            client.post("/activities/Debate Team/signup", params={"email": email})
        
        # Now one more should fail
        response = client.post(
            "/activities/Debate Team/signup",
            params={"email": "overflow@test.edu"}
        )
        
        assert response.status_code == 400
        assert "full" in response.json()["detail"].lower()

    def test_signup_invalid_activity_name_fails(self, client, clean_activities):
        """
        Arrange: Non-existent activity name
        Act: POST /activities/Nonexistent Activity/signup
        Assert: Returns 404 not found
        """
        response = client.post(
            "/activities/Nonexistent Activity/signup",
            params={"email": "student@test.edu"}
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @pytest.mark.parametrize("invalid_email", [
        "notanemail",
        "missing-at-sign.com",
        "nodomain",
        "test",
        "emailwithoutat"
    ])
    def test_signup_invalid_email_fails(self, client, clean_activities, invalid_email):
        """
        Arrange: Invalid email addresses (missing '@' character)
        Act: POST with various invalid email formats
        Assert: All return 400 with invalid email error
        """
        response = client.post(
            "/activities/Art Studio/signup",
            params={"email": invalid_email}
        )
        
        assert response.status_code == 400
        assert "invalid" in response.json()["detail"].lower()

    def test_signup_missing_email_parameter_fails(self, client, clean_activities):
        """
        Arrange: No email parameter provided
        Act: POST /activities/Art Studio/signup without email
        Assert: Returns 422 validation error
        """
        response = client.post("/activities/Art Studio/signup")
        
        assert response.status_code == 422  # Validation error

    @pytest.mark.parametrize("activity_name", [
        "Chess Club",
        "Programming Class",
        "Art Studio",
        "Science Club"
    ])
    def test_signup_valid_email_different_activities(self, client, clean_activities, activity_name):
        """
        Arrange: Same student email, different activities
        Act: POST signup to multiple activities
        Assert: Student successfully signs up for all activities
        """
        email = "versatile@mergington.edu"
        
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        assert response.status_code == 200
        
        # Verify in current activity
        activities_resp = client.get("/activities")
        activities = activities_resp.json()
        assert email in activities[activity_name]["participants"]

    def test_signup_case_sensitive_duplicate_check(self, client, clean_activities):
        """
        Arrange: Student with lowercase email
        Act: Try to signup with different case (e.g., uppercase)
        Assert: Depending on implementation, different cases may or may not be treated as duplicates
               (This tests current behavior: email check is case-sensitive by string equality)
        """
        email1 = "student@mergington.edu"
        email2 = "Student@mergington.edu"
        
        # First signup
        response1 = client.post(
            "/activities/Music Band/signup",
            params={"email": email1}
        )
        assert response1.status_code == 200
        
        # Second signup with different case
        response2 = client.post(
            "/activities/Music Band/signup",
            params={"email": email2}
        )
        # Should succeed because strings don't match exactly (case-sensitive)
        assert response2.status_code == 200
