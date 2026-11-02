
from flask import Flask, request, jsonify
from flask_migrate import Migrate
from sqlalchemy.exc import IntegrityError
from marshmallow import ValidationError

from server.models import db, Exercise, Workout, WorkoutExercise
from server.schemas import (
    ExerciseSchema,
    WorkoutSchema,
    WorkoutExerciseSchema
)

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///workout.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
migrate = Migrate(app, db)

exercise_schema = ExerciseSchema()
exercises_schema = ExerciseSchema(many=True)

workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True)

workout_exercise_schema = WorkoutExerciseSchema()
workout_exercises_schema = WorkoutExerciseSchema(many=True)


@app.route("/")
def home():
    return jsonify({"message": "Workout API is running"})


# WORKOUT ROUTES

@app.route("/workouts", methods=["GET"])
def get_workouts():
    workouts = Workout.query.all()
    return jsonify(workouts_schema.dump(workouts)), 200


@app.route("/workouts/<int:workout_id>", methods=["GET"])
def get_workout(workout_id):
    workout = db.session.get(Workout, workout_id)

    if workout is None:
        return jsonify({"error": "Workout not found"}), 404

    result = workout_schema.dump(workout)
    result["exercises"] = workout_exercises_schema.dump(
        workout.workout_exercises
    )

    return jsonify(result), 200


@app.route("/workouts", methods=["POST"])
def create_workout():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body is required"}), 400

    try:
        valid_data = workout_schema.load(data)
        workout = Workout(**valid_data)

        db.session.add(workout)
        db.session.commit()

        return jsonify(workout_schema.dump(workout)), 201

    except ValidationError as error:
        db.session.rollback()
        return jsonify({"errors": error.messages}), 400

    except ValueError as error:
        db.session.rollback()
        return jsonify({"error": str(error)}), 400


@app.route("/workouts/<int:workout_id>", methods=["PATCH"])
def update_workout(workout_id):
    workout = db.session.get(Workout, workout_id)

    if workout is None:
        return jsonify({"error": "Workout not found"}), 404

    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body is required"}), 400

    try:
        valid_data = workout_schema.load(data, partial=True)

        for key, value in valid_data.items():
            setattr(workout, key, value)

        db.session.commit()

        return jsonify(workout_schema.dump(workout)), 200

    except ValidationError as error:
        db.session.rollback()
        return jsonify({"errors": error.messages}), 400

    except ValueError as error:
        db.session.rollback()
        return jsonify({"error": str(error)}), 400


@app.route("/workouts/<int:workout_id>", methods=["DELETE"])
def delete_workout(workout_id):
    workout = db.session.get(Workout, workout_id)

    if workout is None:
        return jsonify({"error": "Workout not found"}), 404

    db.session.delete(workout)
    db.session.commit()

    return "", 204


# EXERCISE ROUTES

@app.route("/exercises", methods=["GET"])
def get_exercises():
    exercises = Exercise.query.all()
    return jsonify(exercises_schema.dump(exercises)), 200


@app.route("/exercises/<int:exercise_id>", methods=["GET"])
def get_exercise(exercise_id):
    exercise = db.session.get(Exercise, exercise_id)

    if exercise is None:
        return jsonify({"error": "Exercise not found"}), 404

    result = exercise_schema.dump(exercise)

    result["workouts"] = [
        {
            "id": workout.id,
            "date": workout.date.isoformat(),
            "duration_minutes": workout.duration_minutes,
            "notes": workout.notes
        }
        for workout in exercise.workouts
    ]

    return jsonify(result), 200


@app.route("/exercises", methods=["POST"])
def create_exercise():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body is required"}), 400

    try:
        valid_data = exercise_schema.load(data)
        exercise = Exercise(**valid_data)

        db.session.add(exercise)
        db.session.commit()

        return jsonify(exercise_schema.dump(exercise)), 201

    except ValidationError as error:
        db.session.rollback()
        return jsonify({"errors": error.messages}), 400

    except ValueError as error:
        db.session.rollback()
        return jsonify({"error": str(error)}), 400


@app.route("/exercises/<int:exercise_id>", methods=["PATCH"])
def update_exercise(exercise_id):
    exercise = db.session.get(Exercise, exercise_id)

    if exercise is None:
        return jsonify({"error": "Exercise not found"}), 404

    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body is required"}), 400

    try:
        valid_data = exercise_schema.load(data, partial=True)

        for key, value in valid_data.items():
            setattr(exercise, key, value)

        db.session.commit()

        return jsonify(exercise_schema.dump(exercise)), 200

    except ValidationError as error:
        db.session.rollback()
        return jsonify({"errors": error.messages}), 400

    except ValueError as error:
        db.session.rollback()
        return jsonify({"error": str(error)}), 400


@app.route("/exercises/<int:exercise_id>", methods=["DELETE"])
def delete_exercise(exercise_id):
    exercise = db.session.get(Exercise, exercise_id)

    if exercise is None:
        return jsonify({"error": "Exercise not found"}), 404

    db.session.delete(exercise)
    db.session.commit()

    return "", 204


# ADD EXERCISE TO WORKOUT

@app.route(
    "/workouts/<int:workout_id>/exercises/<int:exercise_id>/workout_exercises",
    methods=["POST"]
)
def add_exercise_to_workout(workout_id, exercise_id):
    workout = db.session.get(Workout, workout_id)
    exercise = db.session.get(Exercise, exercise_id)

    if workout is None:
        return jsonify({"error": "Workout not found"}), 404

    if exercise is None:
        return jsonify({"error": "Exercise not found"}), 404

    data = request.get_json() or {}

    try:
        valid_data = workout_exercise_schema.load(data)

        association = WorkoutExercise(
            workout=workout,
            exercise=exercise,
            reps=valid_data.get("reps"),
            sets=valid_data.get("sets"),
            duration_seconds=valid_data.get("duration_seconds")
        )

        db.session.add(association)
        db.session.commit()

        result = workout_exercise_schema.dump(association)

        return jsonify(result), 201

    except ValidationError as error:
        db.session.rollback()
        return jsonify({"errors": error.messages}), 400

    except ValueError as error:
        db.session.rollback()
        return jsonify({"error": str(error)}), 400

    except IntegrityError:
        db.session.rollback()
        return jsonify({
            "error": "This exercise may already exist in this workout"
        }), 400


if __name__ == "__main__":
    app.run(port=5555, debug=True)
