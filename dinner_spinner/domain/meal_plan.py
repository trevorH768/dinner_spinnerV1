class MealPlan:
    """A user-defined planning record that schedules a Recipe, or an intentionally
    empty meal slot, for a specific day and meal type within a defined planning
    week, and specifies the number of servings planned.

    A MealPlan must have a unique combination of:
        week_start + day + meal_type

    recipe_id is nullable. An empty meal slot is valid.
    A MealPlan may therefore represent: recipe_id = NULL, servings = positive value.
    """

    def __init__(self, id: int, week_start: int, day: int, meal_type: str,
                 recipe_id: int | None, servings: int):
        if week_start is None or day is None or not meal_type or not meal_type.strip():
            raise ValueError("MealPlan week_start, day, and meal_type are required")
        self.id = id
        self.week_start = week_start
        self.day = day
        self.meal_type = meal_type.strip()
        self.recipe_id = recipe_id
        if servings is None or servings <= 0:
            raise ValueError("MealPlan servings must be greater than zero")
        self.servings = servings

    def __eq__(self, other):
        if not isinstance(other, MealPlan):
            return NotImplemented
        return (self.id == other.id and self.week_start == other.week_start
                and self.day == other.day and self.meal_type == other.meal_type
                and self.recipe_id == other.recipe_id
                and self.servings == other.servings)

    def __repr__(self):
        recipe_ref = self.recipe_id if self.recipe_id else "None"
        return (f"<MealPlan id={self.id} week={self.week_start} day={self.day}"
                f" meal={self.meal_type!r} recipe_id={recipe_ref} servings={self.servings}>")

    def __hash__(self):
        return hash((self.id, self.week_start, self.day, self.meal_type,
                     self.recipe_id, self.servings))