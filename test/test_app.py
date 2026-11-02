
import pytest
from datetime import date

from server.app import app
from server.models import db, Exercise, Workout


@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"

    with app.app_context():
        db.drop_all()
        db.create_all()

        exercise = Exercise(
            name="Push-ups",
            category="Strength",
            equipment_needed=False
        )

        workout = Workout(
            date=date(2026, 11, 2),
            duration_minutes=30,
            notes="Morning workout"
        )

        db.session.add_all([exercise, workout])
        db.session.commit()

    yield app.test_client()

    with app.app_context():
        db.session.remove()
        db.drop_all()


def test_home(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json["message"] == "Workout API is running"


def test_get_all_exercises(client):
    response = client.get("/exercises")
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]["name"] == "Push-ups"


def test_get_single_exercise(client):
    response = client.get("/exercises/1")
    assert response.status_code == 200
    assert response.json["name"] == "Push-ups"


def test_get_missing_exercise(client):
    response = client.get("/exercises/999")
    assert response.status_code == 404


def test_create_exercise(client):
    response = client.post("/exercises", json={
        "name": "Squats",
        "category": "Strength",
        "equipment_needed": False
    })

    assert response.status_code == 201
    assert response.json["name"] == "Squats"


def test_create_exercise_without_name(client):
    response = client.post("/exercises", json={
        "category": "Strength",
        "equipment_needed": False
    })

    assert response.status_code == 400


def test_update_exercise(client):
    response = client.patch("/exercises/1", json={
        "name": "Modified Push-ups"
    })

    assert response.status_code == 200
    assert response.json["name"] == "Modified Push-ups"


def test_delete_exercise(client):
    response = client.delete("/exercises/1")
    assert response.status_code == 204


def test_get_all_workouts(client):
    response = client.get("/workouts")
    assert response.status_code == 200
    assert len(response.json) == 1


def test_get_single_workout(client):
    response = client.get("/workouts/1")
    assert response.status_code == 200
    assert response.json["duration_minutes"] == 30


def test_get_missing_workout(client):
    response = client.get("/workouts/999")
    assert response.status_code == 404


def test_create_workout(client):
    response = client.post("/workouts", json={
        "date": "2026-11-02",
        "duration_minutes": 45,
        "notes": "Evening workout"
    })

    assert response.status_code == 201
    assert response.json["duration_minutes"] == 45


def test_create_workout_with_negative_duration(client):
    response = client.post("/workouts", json={
        "date": "2026-11-02",
        "duration_minutes": -10,
        "notes": "Invalid workout"
    })

    assert response.status_code == 400


def test_update_workout(client):
    response = client.patch("/workouts/1", json={
        "duration_minutes": 60
    })

    assert response.status_code == 200
    assert response.json["duration_minutes"] == 60


def test_delete_workout(client):
    response = client.delete("/workouts/1")
    assert response.status_code == 204


def test_add_exercise_to_workout(client):
    response = client.post(
        "/workouts/1/exercises/1/workout_exercises",
        json={
            "sets": 3,
            "reps": 15
        }
    )

    assert response.status_code == 201
    assert response.json["sets"] == 3
    assert response.json["reps"] == 15


def test_add_exercise_with_invalid_reps(client):
    response = client.post(
        "/workouts/1/exercises/1/workout_exercises",
        json={
            "sets": 3,
            "reps": -5
        }
    )

    assert response.status_code == 400


def test_prevent_duplicate_exercise_in_workout(client):
    url = "/workouts/1/exercises/1/workout_exercises"

    first_response = client.post(url, json={
        "sets": 3,
        "reps": 15
    })

    second_response = client.post(url, json={
        "sets": 2,
        "reps": 10
    })

    assert first_response.status_code == 201
    assert second_response.status_code == 400
