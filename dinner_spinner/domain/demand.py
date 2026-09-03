"""Demand: A calculated projection of ingredient requirements for a meal plan.

Demand is a derived projection, not an authoritative database entity.
It represents the calculated quantity of an Ingredient required to fulfill
the meals represented by a defined Meal Plan for its planning period.

Demand is calculated from:
- MealPlan (which recipe, how many servings)
- Recipe (base serving yield)
- RecipeIngredient (quantity and unit per base serving)
"""

from dataclasses import dataclass
from typing import Optional
from decimal import Decimal

from dinner_spinner.domain.unit_system import convert, category_of, is_initialized, validate_unit


@dataclass(frozen=True)
class IngredientDemand:
    """A calculated demand for a specific Ingredient.

    This is a derived projection, not an authoritative database entity.
    It represents the total required quantity of an Ingredient to fulfill
    the meals represented by a defined Meal Plan.

    Attributes:
        ingredient_id: The ID of the required Ingredient
        ingredient_name: The name of the required Ingredient (for display)
        quantity: The total required quantity (after unit normalization)
        unit: The normalized unit used for the aggregated quantity
    """
    ingredient_id: int
    ingredient_name: str
    quantity: Decimal
    unit: str

    def __post_init__(self):
        if self.quantity < 0:
            raise ValueError("Demand quantity cannot be negative")
        if not self.unit or not self.unit.strip():
            raise ValueError("Demand unit is required")

    def __eq__(self, other):
        if not isinstance(other, IngredientDemand):
            return NotImplemented
        return (self.ingredient_id == other.ingredient_id
                and self.quantity == other.quantity
                and self.unit == other.unit)

    def __repr__(self):
        return (f"<IngredientDemand ingredient_id={self.ingredient_id}"
                f" name={self.ingredient_name!r} qty={self.quantity} {self.unit}>")


def calculate_demand(
    meal_plans: list,
    recipes: dict,
    recipe_ingredients: dict,
) -> list:
    """Calculate ingredient demand for a list of meal plans.

    This is the core demand calculation function. It:
    1. Iterates through meal plans with recipes
    2. Scales recipe ingredient quantities by serving ratio
    3. Normalizes units for aggregation using UnitSystem
    4. Aggregates by ingredient_id

    Args:
        meal_plans: List of MealPlan domain objects
        recipes: Dict mapping recipe_id -> Recipe domain object
        recipe_ingredients: Dict mapping recipe_id -> list of RecipeIngredient domain objects

    Returns:
        List of IngredientDemand objects, one per unique ingredient_id

    Raises:
        ValueError: If unit conversion fails or invalid data
        RuntimeError: If UnitSystem not initialized
    """
    if not is_initialized():
        raise RuntimeError("UnitSystem not initialized; call initialize() first")

    # Accumulator: ingredient_id -> (quantity, unit, ingredient_name)
    demands: dict[int, tuple[Decimal, str, str]] = {}

    for mp in meal_plans:
        # Empty meal slot produces no demand
        if mp.recipe_id is None:
            continue

        recipe = recipes.get(mp.recipe_id)
        if recipe is None:
            continue

        recipe_ing_list = recipe_ingredients.get(recipe.id, [])
        if not recipe_ing_list:
            continue

        # Serving scaling factor
        if recipe.servings <= 0:
            raise ValueError(f"Recipe {recipe.id} has invalid servings: {recipe.servings}")

        scale_factor = Decimal(mp.servings) / Decimal(recipe.servings)

        for ri in recipe_ing_list:
            # Scale the quantity by serving ratio
            scaled_qty = Decimal(str(ri.quantity)) * Decimal(str(mp.servings)) / Decimal(str(recipe.servings))

            # Aggregate by ingredient_id
            if ri.ingredient_id in demands:
                existing_qty, existing_unit, ingredient_name = demands[ri.ingredient_id]

                # Try to normalize units for aggregation
                try:
                    normalized_qty = Decimal(str(convert(
                        float(scaled_qty), ri.unit, existing_unit
                    )))
                    demands[ri.ingredient_id] = (
                        existing_qty + normalized_qty,
                        existing_unit,
                        ingredient_name
                    )
                except ValueError:
                    # Incompatible units - cannot aggregate
                    raise ValueError(
                        f"Cannot aggregate demand for ingredient {ri.ingredient_id}: "
                        f"incompatible units '{ri.unit}' and '{existing_unit}' "
                        f"(requires density information)"
                    )
            else:
                # First occurrence of this ingredient
                demands[ri.ingredient_id] = (
                    Decimal(str(scaled_qty)),
                    ri.unit,
                    ""  # Will be filled in later
                )

    # Convert to IngredientDemand objects
    result = []
    for ingredient_id, (quantity, unit, _) in demands.items():
        # For now we don't have the ingredient name in the accumulator
        # The application layer will fill this in
        result.append(IngredientDemand(
            ingredient_id=ingredient_id,
            ingredient_name="",  # Will be populated by application layer
            quantity=quantity,
            unit=unit
        ))

    # Sort by ingredient_id for deterministic ordering
    result.sort(key=lambda d: d.ingredient_id)

    return result


def calculate_demand_for_week(
    meal_plans: list,
    recipes: dict,
    recipe_ingredients: dict,
    ingredients: dict,
) -> list:
    """Calculate demand for a week, with ingredient names populated.

    This is a convenience function that includes ingredient names in the result.

    Args:
        meal_plans: List of MealPlan domain objects
        recipes: Dict mapping recipe_id -> Recipe domain object
        recipe_ingredients: Dict mapping recipe_id -> list of RecipeIngredient domain objects
        ingredients: Dict mapping ingredient_id -> Ingredient domain object

    Returns:
        List of IngredientDemand objects with ingredient_name populated
    """
    demands = calculate_demand(meal_plans, recipes, recipe_ingredients)

    # Populate ingredient names
    for demand in demands:
        ingredient = ingredients.get(demand.ingredient_id)
        if ingredient:
            # Create new instance with name (frozen dataclass, so create new)
            # Using object.__setattr__ to bypass frozen restriction
            object.__setattr__(demand, 'ingredient_name', ingredient.name)

    return demands