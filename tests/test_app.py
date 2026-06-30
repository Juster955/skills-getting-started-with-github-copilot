from copy import deepcopy

from src.app import activities


def test_root_redirects_to_static_index(client):
    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_seed_data(client):
    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200

    body = response.json()
    assert "Chess Club" in body
    assert body["Chess Club"]["description"]
    assert body["Chess Club"]["schedule"]
    assert body["Chess Club"]["max_participants"] == 12
    assert body["Chess Club"]["participants"] == ["michael@mergington.edu", "daniel@mergington.edu"]


def test_signup_adds_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "new.student@mergington.edu"
    starting_participants = deepcopy(activities[activity_name]["participants"])

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert activities[activity_name]["participants"] == starting_participants + [email]


def test_signup_rejects_duplicate_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    starting_participants = deepcopy(activities[activity_name]["participants"])

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Student already signed up for this activity"}
    assert activities[activity_name]["participants"] == starting_participants


def test_signup_rejects_unknown_activity(client):
    # Act
    response = client.post("/activities/Unknown Club/signup", params={"email": "student@mergington.edu"})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_remove_participant_succeeds(client):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    starting_participants = deepcopy(activities[activity_name]["participants"])

    # Act
    response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from {activity_name}"}
    assert email not in activities[activity_name]["participants"]
    assert len(activities[activity_name]["participants"]) == len(starting_participants) - 1


def test_remove_participant_rejects_unknown_activity(client):
    # Act
    response = client.delete("/activities/Unknown Club/signup", params={"email": "student@mergington.edu"})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_remove_participant_rejects_missing_signup(client):
    # Act
    response = client.delete("/activities/Chess Club/signup", params={"email": "not-enrolled@mergington.edu"})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Student is not signed up for this activity"}