"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to known state before each test"""
    # Store original state
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Debate Club": {
            "description": "Develop critical thinking and public speaking skills through competitive debate",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["alex@mergington.edu", "jordan@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball training and games",
            "schedule": "Mondays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["marcus@mergington.edu", "tyler@mergington.edu"]
        },
        "Track and Field": {
            "description": "Sprint, distance running, and field events training",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 25,
            "participants": ["sarah@mergington.edu", "alex@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore painting, drawing, and mixed media techniques",
            "schedule": "Mondays and Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["isabella@mergington.edu", "grace@mergington.edu"]
        },
        "Music Band": {
            "description": "Play in the school band and perform at concerts and events",
            "schedule": "Mondays, Wednesdays, Fridays, 3:30 PM - 4:30 PM",
            "max_participants": 40,
            "participants": ["lucas@mergington.edu", "zoe@mergington.edu"]
        },
        "Drama Club": {
            "description": "Act in theatrical productions and develop performance skills",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["noah@mergington.edu", "ava@mergington.edu"]
        }
    }
    
    # Clear and reset
    activities.clear()
    activities.update(original_activities)
    yield
    
    # Reset after test
    activities.clear()
    activities.update(original_activities)


def test_get_activities():
    """Test that GET /activities returns all activities"""
    client = TestClient(app)
    response = client.get("/activities")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert len(data) == 9  # 9 activities total
    
    # Verify activity structure
    assert "description" in data["Chess Club"]
    assert "schedule" in data["Chess Club"]
    assert "max_participants" in data["Chess Club"]
    assert "participants" in data["Chess Club"]


def test_signup_success():
    """Test successful signup for an activity"""
    client = TestClient(app)
    
    response = client.post(
        "/activities/Chess Club/signup?email=newstudent@mergington.edu"
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "Signed up" in data["message"]
    assert "newstudent@mergington.edu" in data["message"]
    
    # Verify participant was added
    assert "newstudent@mergington.edu" in activities["Chess Club"]["participants"]


def test_signup_duplicate_registration():
    """Test that signup fails when student is already registered"""
    client = TestClient(app)
    
    # Try to sign up a student who is already registered
    response = client.post(
        "/activities/Chess Club/signup?email=michael@mergington.edu"
    )
    
    assert response.status_code == 400
    data = response.json()
    assert "already signed up" in data["detail"].lower()


def test_signup_activity_not_found():
    """Test that signup fails for non-existent activity"""
    client = TestClient(app)
    
    response = client.post(
        "/activities/Nonexistent Club/signup?email=newstudent@mergington.edu"
    )
    
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower()


def test_unregister_success():
    """Test successful unregistration from an activity"""
    client = TestClient(app)
    
    # Verify student is registered
    assert "michael@mergington.edu" in activities["Chess Club"]["participants"]
    
    response = client.delete(
        "/activities/Chess Club/unregister?email=michael@mergington.edu"
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "Unregistered" in data["message"]
    
    # Verify participant was removed
    assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]


def test_unregister_student_not_registered():
    """Test that unregister fails when student is not registered"""
    client = TestClient(app)
    
    response = client.delete(
        "/activities/Chess Club/unregister?email=notregistered@mergington.edu"
    )
    
    assert response.status_code == 404
    data = response.json()
    assert "not registered" in data["detail"].lower()


def test_unregister_activity_not_found():
    """Test that unregister fails for non-existent activity"""
    client = TestClient(app)
    
    response = client.delete(
        "/activities/Nonexistent Club/unregister?email=michael@mergington.edu"
    )
    
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower()


def test_signup_at_capacity():
    """Test signup when activity is at max capacity"""
    client = TestClient(app)
    
    # Create a activity with only 1 spot, already filled
    test_activity = {
        "description": "Test activity",
        "schedule": "Test time",
        "max_participants": 1,
        "participants": ["existing@mergington.edu"]
    }
    activities["Test Activity"] = test_activity
    
    # Try to sign up when at capacity (should succeed - no capacity check yet)
    response = client.post(
        "/activities/Test Activity/signup?email=newstudent@mergington.edu"
    )
    
    # Signup should succeed since we don't have capacity validation yet
    assert response.status_code == 200


def test_multiple_unregister_operations():
    """Test multiple unregister operations in sequence"""
    client = TestClient(app)
    
    initial_count = len(activities["Programming Class"]["participants"])
    
    # Unregister first student
    response1 = client.delete(
        "/activities/Programming Class/unregister?email=emma@mergington.edu"
    )
    assert response1.status_code == 200
    assert len(activities["Programming Class"]["participants"]) == initial_count - 1
    
    # Unregister second student
    response2 = client.delete(
        "/activities/Programming Class/unregister?email=sophia@mergington.edu"
    )
    assert response2.status_code == 200
    assert len(activities["Programming Class"]["participants"]) == initial_count - 2
    
    # Try to unregister again (should fail)
    response3 = client.delete(
        "/activities/Programming Class/unregister?email=emma@mergington.edu"
    )
    assert response3.status_code == 404
