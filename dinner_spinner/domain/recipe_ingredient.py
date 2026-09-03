"""A Recipe-specific requirement that identifies an Ingredient and specifies
the positive quantity and unit of that Ingredient required to produce the
Recipe's defined serving yield.

A Recipe may reference a given Ingredient only once.
Database/application integrity must enforce:
    UNIQUE(recipe_id, ingredient_id)
"""

from dinner_spinner.domain.unit_system import validate_unit, is_initialized


class RecipeIngredient:
    """A Recipe-specific requirement that identifies an Ingredient and specifies
    the positive quantity and unit of that Ingredient required to produce the
    Recipe's defined serving yield.

    A Recipe may reference a given Ingredient only once.
    """

    def __init__(self, id: int, recipe_id: int, ingredient_id: int,
                 quantity: float, unit: str):
        if quantity is None or quantity <= 0:
            raise ValueError("RecipeIngredient quantity must be greater than zero")
        self.id = id
        self.recipe_id = recipe_id
        self.ingredient_id = ingredient_id
        self.quantity = quantity
        if not unit or not unit.strip():
            raise ValueError("RecipeIngredient unit is required")
        self.unit = unit.strip()
        if is_initialized() and not validate_unit(self.unit):
            raise ValueError(f"Unit '{self.unit}' is not a recognized unit")

    def __eq__(self, other):
        if not isinstance(other, RecipeIngredient):
            return NotImplemented
        return (self.id == other.id and self.recipe_id == other.recipe_id
                and self.ingredient_id == other.ingredient_id
                and self.quantity == other.quantity
                and self.unit == other.unit)

    def __repr__(self):
        return (f"<RecipeIngredient id={self.id} recipe_id={self.recipe_id}"
                f" ingredient_id={self.ingredient_id} qty={self.quantity} {self.unit}>")

    def __hash__(self):
        return hash((self.id, self.recipe_id, self.ingredient_id,
                     self.quantity, self.unit))