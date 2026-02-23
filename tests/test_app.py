"""
FastAPI Backend Tests - AAA Pattern
Activities management API tests with Arrange-Act-Assert structure
"""
import copy
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    """Arrange: Reset activities to original state before each test"""
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
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball practice and games",
            "schedule": "Monday and Wednesday, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Learn and practice tennis skills",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["sarah@mergington.edu", "james@mergington.edu"]
        },
        "Art Studio": {
            "description": "Painting, drawing, and mixed media art",
            "schedule": "Mondays and Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["isabella@mergington.edu"]
        },
        "Drama Club": {
            "description": "Theater performances and acting workshops",
            "schedule": "Wednesdays, 4:00 PM - 6:00 PM",
            "max_participants": 25,
            "participants": ["lucas@mergington.edu", "mia@mergington.edu"]
        },
        "Debate Team": {
            "description": "Competitive debate and public speaking",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["grace@mergington.edu"]
        },
        "Science Club": {
            "description": "Hands-on experiments and STEM projects",
            "schedule": "Wednesdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["noah@mergington.edu", "ava@mergington.edu"]
        }
    }
    
    # Clear and repopulate activities dict
    activities.clear()
    activities.update(copy.deepcopy(original_activities))
    yield
    # Cleanup after test
    activities.clear()
    activities.update(copy.deepcopy(original_activities))


@pytest.fixture
def client():
    """Create a TestClient for the FastAPI app"""
    return TestClient(app)


class TestGetActivities:
    """Test suite for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client):
        # Arrange: No setup needed, activities already initialized
        
        # Act: Make GET request to activities endpoint
        response = client.get("/activities")
        
        # Assert: Verify response status and data
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert data["Chess Club"]["max_participants"] == 12
        assert "michael@mergington.edu" in data["Chess Club"]["participants"]


class TestSignup:
    """Test suite for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_success(self, client):
        # Arrange: Prepare activity and new student email
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        
        # Act: Submit signup request
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert: Verify response and that participant was added
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity_name}"
        assert email in activities[activity_name]["participants"]
    
    def test_signup_already_registered(self, client):
        # Arrange: Use existing participant email
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already in Chess Club
        
        # Act: Try to signup with existing email
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert: Verify 400 error is returned
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_activity_not_found(self, client):
        # Arrange: Use non-existent activity name
        activity_name = "Non-Existent Activity"
        email = "student@mergington.edu"
        
        # Act: Try to signup for non-existent activity
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert: Verify 404 error is returned
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]


class TestUnregister:
    """Test suite for DELETE /activities/{activity_name}/signup endpoint"""
    
    def test_unregister_success(self, client):
        # Arrange: Setup with existing participant
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        initial_count = len(activities[activity_name]["participants"])
        
        # Act: Submit unregister request
        response = client.delete(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert: Verify response and that participant was removed
        assert response.status_code == 200
        assert response.json()["message"] == f"Removed {email} from {activity_name}"
        assert email not in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == initial_count - 1
    
    def test_unregister_student_not_in_activity(self, client):
        # Arrange: Use student not registered for activity
        activity_name = "Chess Club"
        email = "notregistered@mergington.edu"
        
        # Act: Try to unregister non-existent student
        response = client.delete(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert: Verify 404 error is returned
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    def test_unregister_activity_not_found(self, client):
        # Arrange: Use non-existent activity
        activity_name = "Non-Existent Activity"
        email = "student@mergington.edu"
        
        # Act: Try to unregister from non-existent activity
        response = client.delete(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert: Verify 404 error is returned
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]


class TestRootRedirect:
    """Test suite for GET / endpoint"""
    
    def test_root_redirect_to_index(self, client):
        # Arrange: No setup needed
        
        # Act: Make request to root path with follow_redirects=False to see redirect
        response = client.get("/", follow_redirects=False)
        
        # Assert: Verify redirect response
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
