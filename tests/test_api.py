from src.app import activities


def test_root_redirects_to_static_index(client):
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_catalog(client):
    response = client.get("/activities")

    assert response.status_code == 200
    payload = response.json()
    assert "Chess Club" in payload
    assert payload["Chess Club"]["description"]
    assert payload["Chess Club"]["participants"]


def test_signup_for_activity_success(client):
    email = "student@mergington.edu"

    response = client.post("/activities/Chess Club/signup", params={"email": email})

    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for Chess Club"
    assert email in activities["Chess Club"]["participants"]


def test_signup_for_activity_already_signed_up(client):
    email = "michael@mergington.edu"

    response = client.post("/activities/Chess Club/signup", params={"email": email})

    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_signup_for_same_student_in_different_activity_is_allowed(client):
    email = "michael@mergington.edu"

    response = client.post("/activities/Programming Class/signup", params={"email": email})

    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for Programming Class"
    assert email in activities["Programming Class"]["participants"]
    assert email in activities["Chess Club"]["participants"]


def test_signup_for_missing_activity_returns_404(client):
    response = client.post("/activities/Unknown Club/signup", params={"email": "student@mergington.edu"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_for_full_activity_returns_400(client):
    activity_name = "Basketball Team"
    activities[activity_name]["participants"] = [
        f"student{i}@mergington.edu" for i in range(activities[activity_name]["max_participants"])
    ]

    response = client.post(f"/activities/{activity_name}/signup", params={"email": "new@mergington.edu"})

    assert response.status_code == 400
    assert response.json()["detail"] == "Activity is full"


def test_unregister_participant_success(client):
    email = "alex@mergington.edu"

    response = client.delete(f"/activities/Basketball Team/participants/{email}")

    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from Basketball Team"
    assert email not in activities["Basketball Team"]["participants"]
    assert len(activities["Basketball Team"]["participants"]) == 0


def test_unregister_missing_participant_returns_404(client):
    response = client.delete("/activities/Basketball Team/participants/missing@mergington.edu")

    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"


def test_unregister_missing_activity_returns_404(client):
    response = client.delete("/activities/Unknown Club/participants/student@mergington.edu")

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
