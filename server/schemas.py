
from marshmallow import Schema, fields, validates, ValidationError


class ExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    category = fields.Str(required=True)
    equipment_needed = fields.Bool(required=True)

    @validates("name")
    def validate_name(self, value):
        if not value.strip():
            raise ValidationError("Exercise name cannot be empty")

    @validates("category")
    def validate_category(self, value):
        if not value.strip():
            raise ValidationError("Exercise category cannot be empty")


class WorkoutSchema(Schema):
    id = fields.Int(dump_only=True)
    date = fields.Date(required=True)
    duration_minutes = fields.Int(required=True)
    notes = fields.Str(allow_none=True)


class WorkoutExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    workout_id = fields.Int(dump_only=True)
    exercise_id = fields.Int(dump_only=True)
    reps = fields.Int(allow_none=True)
    sets = fields.Int(allow_none=True)
    duration_seconds = fields.Int(allow_none=True)

    exercise = fields.Nested(ExerciseSchema, dump_only=True)

    @validates("reps")
    def validate_reps(self, value):
        if value is not None and value <= 0:
            raise ValidationError("Reps must be greater than zero")

    @validates("sets")
    def validate_sets(self, value):
        if value is not None and value <= 0:
            raise ValidationError("Sets must be greater than zero")

    @validates("duration_seconds")
    def validate_duration(self, value):
        if value is not None and value <= 0:
            raise ValidationError("Duration must be greater than zero")
