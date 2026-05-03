import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

# Create a copy of the original activities for resetting
original_activities = activities.copy()

@pytest.fixture
def client():
    # Reset activities before each test
    activities.clear()
    activities.update(original_activities)
    return TestClient(app)

def test_get_activities(client):
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data
    # Check structure of one activity
    chess = data["Chess Club"]
    assert "description" in chess
    assert "schedule" in chess
    assert "max_participants" in chess
    assert "participants" in chess
    assert isinstance(chess["participants"], list)

def test_signup_success(client):
    response = client.post("/activities/Chess Club/signup", json={"email": "newstudent@mergington.edu"})
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "newstudent@mergington.edu" in data["message"]
    # Check that participant was added
    activities_response = client.get("/activities")
    chess_participants = activities_response.json()["Chess Club"]["participants"]
    assert "newstudent@mergington.edu" in chess_participants

def test_signup_already_signed_up(client):
    response = client.post("/activities/Chess Club/signup", json={"email": "michael@mergington.edu"})
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "already signed up" in data["detail"]

def test_signup_activity_full(client):
    # First, fill up the activity
    activity_name = "Chess Club"
    max_part = activities[activity_name]["max_participants"]
    current_part = len(activities[activity_name]["participants"])
    for i in range(max_part - current_part):
        email = f"extra{i}@mergington.edu"
        client.post(f"/activities/{activity_name}/signup", json={"email": email})
    # Now try to add one more
    response = client.post(f"/activities/{activity_name}/signup", json={"email": "overflow@mergington.edu"})
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "maximum capacity" in data["detail"]

def test_signup_activity_not_found(client):
    response = client.post("/activities/NonExistent Activity/signup", json={"email": "test@mergington.edu"})
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]