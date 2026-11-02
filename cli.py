
import json
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


BASE_URL = "http://127.0.0.1:5555"


# SEND REQUESTS TO THE FLASK API

def api_request(method, endpoint, data=None):
    url = BASE_URL + endpoint

    headers = {
        "Content-Type": "application/json"
    }

    body = None

    if data is not None:
        body = json.dumps(data).encode("utf-8")

    request = Request(
        url,
        data=body,
        headers=headers,
        method=method
    )

    try:
        with urlopen(request, timeout=10) as response:
            response_data = response.read()

            if response_data:
                return json.loads(response_data.decode("utf-8"))

            return None

    except HTTPError as error:
        response_data = error.read().decode("utf-8")

        try:
            error_data = json.loads(response_data)
            print("\nAPI Error:")
            print(json.dumps(error_data, indent=4))
        except json.JSONDecodeError:
            print("\nAPI Error:", error.code, response_data)

    except URLError:
        print("\nCould not connect to the API.")
        print("Make sure the Flask server is running on port 5555.")

    except TimeoutError:
        print("\nThe API request timed out.")

    return None


# HELPER FUNCTIONS

def print_data(data):
    if data is None:
        return

    print(json.dumps(data, indent=4))


def get_integer(prompt, optional=False):
    while True:
        value = input(prompt).strip()

        if optional and value == "":
            return None

        try:
            return int(value)
        except ValueError:
            print("Please enter a valid whole number.")


def get_boolean(prompt):
    while True:
        value = input(prompt).strip().lower()

        if value in ["yes", "y"]:
            return True

        if value in ["no", "n"]:
            return False

        print("Please enter yes or no.")


def confirm_action():
    answer = input("Are you sure? (yes/no): ").strip().lower()
    return answer in ["yes", "y"]


# EXERCISE MANAGEMENT

def view_exercises():
    print("\n--- ALL EXERCISES ---")

    exercises = api_request("GET", "/exercises")

    if exercises is not None:
        if not exercises:
            print("No exercises found.")
        else:
            print_data(exercises)


def add_exercise():
    print("\n--- ADD EXERCISE ---")

    name = input("Exercise name: ").strip()
    category = input("Category: ").strip()
    equipment = get_boolean("Does it require equipment? (yes/no): ")

    data = {
        "name": name,
        "category": category,
        "equipment_needed": equipment
    }

    result = api_request("POST", "/exercises", data)

    if result is not None:
        print("\nExercise added successfully!")
        print_data(result)


def update_exercise():
    print("\n--- UPDATE EXERCISE ---")

    exercise_id = get_integer("Enter exercise ID: ")

    print("Leave a field empty to keep its current value.")

    data = {}

    name = input("New name: ").strip()
    category = input("New category: ").strip()
    equipment = input("Requires equipment? (yes/no, or Enter to skip): ").strip().lower()

    if name:
        data["name"] = name

    if category:
        data["category"] = category

    if equipment in ["yes", "y"]:
        data["equipment_needed"] = True
    elif equipment in ["no", "n"]:
        data["equipment_needed"] = False

    if not data:
        print("No changes provided.")
        return

    result = api_request(
        "PATCH",
        f"/exercises/{exercise_id}",
        data
    )

    if result is not None:
        print("\nExercise updated successfully!")
        print_data(result)


def delete_exercise():
    print("\n--- DELETE EXERCISE ---")

    exercise_id = get_integer("Enter exercise ID: ")

    if not confirm_action():
        print("Deletion cancelled.")
        return

    result = api_request(
        "DELETE",
        f"/exercises/{exercise_id}"
    )

    if result is None:
        print("Exercise deletion request completed.")


# WORKOUT MANAGEMENT

def view_workouts():
    print("\n--- ALL WORKOUTS ---")

    workouts = api_request("GET", "/workouts")

    if workouts is not None:
        if not workouts:
            print("No workouts found.")
        else:
            print_data(workouts)


def view_workout_details():
    print("\n--- WORKOUT DETAILS ---")

    workout_id = get_integer("Enter workout ID: ")

    result = api_request(
        "GET",
        f"/workouts/{workout_id}"
    )

    if result is not None:
        print_data(result)


def create_workout():
    print("\n--- CREATE WORKOUT ---")

    workout_date = input("Date (YYYY-MM-DD): ").strip()
    duration = get_integer("Duration in minutes: ")
    notes = input("Notes: ").strip()

    data = {
        "date": workout_date,
        "duration_minutes": duration,
        "notes": notes
    }

    result = api_request("POST", "/workouts", data)

    if result is not None:
        print("\nWorkout created successfully!")
        print_data(result)


def update_workout():
    print("\n--- UPDATE WORKOUT ---")

    workout_id = get_integer("Enter workout ID: ")

    print("Leave a field empty to keep its current value.")

    data = {}

    workout_date = input("New date (YYYY-MM-DD): ").strip()
    duration = input("New duration in minutes: ").strip()
    notes = input("New notes: ").strip()

    if workout_date:
        data["date"] = workout_date

    if duration:
        try:
            data["duration_minutes"] = int(duration)
        except ValueError:
            print("Duration must be a whole number.")
            return

    if notes:
        data["notes"] = notes

    if not data:
        print("No changes provided.")
        return

    result = api_request(
        "PATCH",
        f"/workouts/{workout_id}",
        data
    )

    if result is not None:
        print("\nWorkout updated successfully!")
        print_data(result)


def delete_workout():
    print("\n--- DELETE WORKOUT ---")

    workout_id = get_integer("Enter workout ID: ")

    if not confirm_action():
        print("Deletion cancelled.")
        return

    result = api_request(
        "DELETE",
        f"/workouts/{workout_id}"
    )

    if result is None:
        print("Workout deletion request completed.")


# ADD EXERCISE TO WORKOUT

def add_exercise_to_workout():
    print("\n--- ADD EXERCISE TO WORKOUT ---")

    workout_id = get_integer("Enter workout ID: ")
    exercise_id = get_integer("Enter exercise ID: ")

    print("Enter the exercise details.")

    sets = get_integer("Number of sets (Enter to skip): ", optional=True)
    reps = get_integer("Number of repetitions (Enter to skip): ", optional=True)
    duration = get_integer("Duration in seconds (Enter to skip): ", optional=True)

    data = {}

    if sets is not None:
        data["sets"] = sets

    if reps is not None:
        data["reps"] = reps

    if duration is not None:
        data["duration_seconds"] = duration

    endpoint = (
        f"/workouts/{workout_id}/exercises/"
        f"{exercise_id}/workout_exercises"
    )

    result = api_request("POST", endpoint, data)

    if result is not None:
        print("\nExercise added to workout successfully!")
        print_data(result)


# MAIN MENU

def show_menu():
    print("\n")
    print("=" * 40)
    print("       WORKOUT MANAGEMENT SYSTEM")
    print("=" * 40)
    print("1.  View all exercises")
    print("2.  Add an exercise")
    print("3.  Update an exercise")
    print("4.  Delete an exercise")
    print("5.  View all workouts")
    print("6.  View workout details")
    print("7.  Create a workout")
    print("8.  Update a workout")
    print("9.  Delete a workout")
    print("10. Add exercise to workout")
    print("11. Exit")
    print("=" * 40)


def main():
    print("\nWelcome to Workout Management System!")

    while True:
        show_menu()

        choice = input("Choose an option (1-11): ").strip()

        if choice == "1":
            view_exercises()

        elif choice == "2":
            add_exercise()

        elif choice == "3":
            update_exercise()

        elif choice == "4":
            delete_exercise()

        elif choice == "5":
            view_workouts()

        elif choice == "6":
            view_workout_details()

        elif choice == "7":
            create_workout()

        elif choice == "8":
            update_workout()

        elif choice == "9":
            delete_workout()

        elif choice == "10":
            add_exercise_to_workout()

        elif choice == "11":
            print("\nThank you for using Workout Management System!")
            break

        else:
            print("\nInvalid choice. Please select 1-11.")

        input("\nPress Enter to return to the menu...")


if __name__ == "__main__":
    main()
