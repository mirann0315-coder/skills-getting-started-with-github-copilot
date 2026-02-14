"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


class TestActivitiesEndpoint:
    """Tests for the /activities GET endpoint"""

    def test_get_activities_returns_200(self):
        """Test that GET /activities returns 200 OK"""
        response = client.get("/activities")
        assert response.status_code == 200

    def test_get_activities_returns_dict(self):
        """Test that GET /activities returns a dictionary of activities"""
        response = client.get("/activities")
        data = response.json()
        assert isinstance(data, dict)

    def test_get_activities_has_expected_activities(self):
        """Test that response contains all expected activities"""
        response = client.get("/activities")
        data = response.json()
        expected_activities = [
            "Tennis Club",
            "Basketball Team",
            "Drama Club",
            "Art Studio",
            "Debate Team",
            "Robotics Club",
            "Chess Club",
            "Programming Class",
            "Gym Class"
        ]
        for activity in expected_activities:
            assert activity in data

    def test_activity_has_required_fields(self):
        """Test that each activity has all required fields"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)


class TestSignupEndpoint:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""

    def test_signup_returns_200_for_valid_request(self):
        """Test that signup returns 200 OK for valid request"""
        response = client.post(
            "/activities/Tennis%20Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        assert response.status_code == 200

    def test_signup_returns_success_message(self):
        """Test that signup returns a success message"""
        response = client.post(
            "/activities/Tennis%20Club/signup",
            params={"email": "newstudent2@mergington.edu"}
        )
        data = response.json()
        assert "message" in data
        assert "newstudent2@mergington.edu" in data["message"]

    def test_signup_returns_404_for_nonexistent_activity(self):
        """Test that signup returns 404 for non-existent activity"""
        response = client.post(
            "/activities/Nonexistent%20Activity/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_signup_prevents_duplicate_registration(self):
        """Test that a student cannot register twice for the same activity"""
        email = "duplicate_test@mergington.edu"
        
        # First signup should succeed
        response1 = client.post(
            "/activities/Basketball%20Team/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Second signup with same email should fail
        response2 = client.post(
            "/activities/Basketball%20Team/signup",
            params={"email": email}
        )
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]


class TestUnregisterEndpoint:
    """Tests for the DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_returns_200_for_valid_request(self):
        """Test that unregister returns 200 OK for valid request"""
        email = "unregister_test@mergington.edu"
        
        # First signup
        client.post(
            "/activities/Drama%20Club/signup",
            params={"email": email}
        )
        
        # Then unregister
        response = client.delete(
            "/activities/Drama%20Club/unregister",
            params={"email": email}
        )
        assert response.status_code == 200

    def test_unregister_returns_success_message(self):
        """Test that unregister returns a success message"""
        email = "unregister_test2@mergington.edu"
        
        # First signup
        client.post(
            "/activities/Drama%20Club/signup",
            params={"email": email}
        )
        
        # Then unregister
        response = client.delete(
            "/activities/Drama%20Club/unregister",
            params={"email": email}
        )
        data = response.json()
        assert "message" in data
        assert email in data["message"]

    def test_unregister_returns_404_for_nonexistent_activity(self):
        """Test that unregister returns 404 for non-existent activity"""
        response = client.delete(
            "/activities/Nonexistent%20Activity/unregister",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404

    def test_unregister_returns_400_for_unregistered_student(self):
        """Test that unregister returns 400 if student is not registered"""
        response = client.delete(
            "/activities/Chess%20Club/unregister",
            params={"email": "notregistered@mergington.edu"}
        )
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"]

    def test_unregister_removes_participant(self):
        """Test that unregister actually removes the participant"""
        email = "unregister_test3@mergington.edu"
        
        # Signup
        client.post(
            "/activities/Art%20Studio/signup",
            params={"email": email}
        )
        
        # Check that participant is in the list
        response = client.get("/activities")
        assert email in response.json()["Art Studio"]["participants"]
        
        # Unregister
        client.delete(
            "/activities/Art%20Studio/unregister",
            params={"email": email}
        )
        
        # Check that participant is removed
        response = client.get("/activities")
        assert email not in response.json()["Art Studio"]["participants"]


class TestRootEndpoint:
    """Tests for the root endpoint redirect"""

    def test_root_redirects_to_static(self):
        """Test that root endpoint redirects to static page"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
