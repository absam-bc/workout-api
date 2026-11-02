# Workout API

## Project Description

Workout API is a RESTful API built with Python and Flask. It helps users manage exercises and workouts.

Users can create, view, update, and delete exercises and workouts. They can also connect exercises to workouts and record details such as sets, repetitions, and exercise duration.

## Technologies Used

- Python 3.8
- Flask
- Flask-SQLAlchemy
- Flask-Migrate
- SQLite
- Marshmallow
- Pytest

## Project Structure

```text
workout-api/
│
├── instance/
│   └── workout.db
│
├── migrations/
│
├── server/
│   ├── __init__.py
│   ├── app.py
│   ├── models.py
│   ├── schemas.py
│   └── seed.py
│
├── test/
│   └── test_app.py
│
├── .git