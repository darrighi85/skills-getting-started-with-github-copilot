"""Tests for GET /activities endpoint."""

import pytest


class TestGetActivities:
    """Test the /activities endpoint for retrieving all activities."""

    def test_get_activities_returns_all_activities(self, client, clean_activities):
        """
        Arrange: Request all activities
        Act: GET /activities
        Assert: Returns 200 with all 9 activities
        """
        response = client.get("/activities")
        
        assert response.status_code == 200
        activities_data = response.json()
        assert len(activities_data) == 9
        assert "Chess Club" in activities_data
        assert "Programming Class" in activities_data
        assert "Gym Class" in activities_data

    def test_get_activities_response_structure(self, client, clean_activities):
        """
        Arrange: Request activities
        Act: GET /activities
        Assert: Each activity has required fields
        """
        response = client.get("/activities")
        activities_data = response.json()
        
        for activity_name, activity_data in activities_data.items():
            assert isinstance(activity_name, str)
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)

    def test_get_activities_contains_participants(self, client, clean_activities):
        """
        Arrange: Request activities
        Act: GET /activities
        Assert: Activities contain expected initial participants
        """
        response = client.get("/activities")
        activities_data = response.json()
        
        # Verify initial state from app.py
        assert "michael@mergington.edu" in activities_data["Chess Club"]["participants"]
        assert "daniel@mergington.edu" in activities_data["Chess Club"]["participants"]
        assert "emma@mergington.edu" in activities_data["Programming Class"]["participants"]

    @pytest.mark.parametrize("activity_name", [
        "Chess Club",
        "Programming Class",
        "Gym Class",
        "Basketball Team",
        "Soccer Club"
    ])
    def test_get_activities_contains_expected_activity(self, client, clean_activities, activity_name):
        """
        Arrange: Request activities with various activity names
        Act: GET /activities
        Assert: Each specified activity is present in response
        """
        response = client.get("/activities")
        activities_data = response.json()
        
        assert activity_name in activities_data
        assert "description" in activities_data[activity_name]
        assert len(activities_data[activity_name]["description"]) > 0
