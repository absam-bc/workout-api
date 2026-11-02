
from datetime import date

from server.app import app
from server.models import db, Exercise, Workout, WorkoutExercise


with app.app_context():

    # Clear existing records so the seed can be run again
    WorkoutExercise.query.delete()
    Workout.query.delete()
    Exercise.query.delete()

    db.session.commit()

    # Create exercises
    pushups = Exercise(
        name="Push-ups",
        category="Strength",
        equipment_needed=False
    )

    squats = Exercise(
        name="Squats",
        category="Strength",
        equipment_needed=False
    )

    running = Exercise(
        name="Running",
        category="Cardio",
        equipment_needed=False
    )

    bench_press = Exercise(
        name="Bench Press",
        category="Strength",
        equipment_needed=True
    )

    db.session.add_all([
        pushups,
        squats,
        running,
        bench_press
    ])

    db.session.flush()

    # Create workouts
    workout1 = Workout(
        date=date(2026, 10, 28),
        duration_minutes=45,
        notes="Morning strength training"
    )

    workout2 = Workout(
        date=date(2026, 10, 29),
        duration_minutes=30,
        notes="Cardio training"
    )

    db.session.add_all([workout1, workout2])

    db.session.flush()

    # Connect exercises to workouts
    db.session.add_all([
        WorkoutExercise(
            workout=workout1,
            exercise=pushups,
            reps=15,
            sets=3
        ),
        WorkoutExercise(
            workout=workout1,
            exercise=squats,
            reps=20,
            sets=3
        ),
        WorkoutExercise(
            workout=workout1,
            exercise=bench_press,
            reps=10,
            sets=3
        ),
        WorkoutExercise(
            workout=workout2,
            exercise=running,
            duration_seconds=1800
        )
    ])

    db.session.commit()

    print("Database seeded successfully!")
