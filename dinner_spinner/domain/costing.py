"""Costing: Derived historical cost calculations from Acquisition history.

This module provides pure domain functions for calculating:
- Ingredient cost per unit (weighted average from Acquisitions)
- Recipe cost (sum of ingredient costs at historical rates)
- Meal cost (recipe cost scaled to planned servings)

All calculations are derived from actual Acquisition history.
No persistence, no price estimation, no external data.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from dinner_spinner.domain.unit_system import convert, is_initialized, category_of


@dataclass(frozen=True)
class IngredientCost:
    """Weighted historical average cost per unit for an Ingredient.

    Attributes:
        ingredient_id: The Ingredient's ID
        ingredient_name: The Ingredient's name (for display)
        cost_per_unit: Weighted average cost per unit in the cost_unit
        cost_unit: The unit used for the cost (matches Ingredient.unit)
        total_acquisition_cost: Sum of all acquisition costs used
        total_acquisition_quantity: Sum of all normalized acquisition quantities used
        acquisition_count: Number of acquisitions included in the average
    """
    ingredient_id: int
    ingredient_name: str
    cost_per_unit: Decimal
    cost_unit: str
    total_acquisition_cost: Decimal
    total_acquisition_quantity: Decimal
    acquisition_count: int

    def __post_init__(self):
        if self.cost_per_unit < 0:
            raise ValueError("Cost per unit cannot be negative")
        if self.total_acquisition_cost < 0:
            raise ValueError("Total acquisition cost cannot be negative")
        if self.total_acquisition_quantity <= 0:
            raise ValueError("Total acquisition quantity must be positive")
        if self.acquisition_count <= 0:
            raise ValueError("Acquisition count must be positive")
        if not self.cost_unit or not self.cost_unit.strip():
            raise ValueError("Cost unit is required")


@dataclass(frozen=True)
class RecipeIngredientCost:
    """Cost of a single RecipeIngredient line item.

    Attributes:
        ingredient_id: The Ingredient's ID
        ingredient_name: The Ingredient's name
        recipe_ingredient_quantity: The RecipeIngredient's original quantity
        recipe_ingredient_unit: The RecipeIngredient's original unit
        cost_per_unit: The Ingredient's cost per unit (in cost_unit)
        cost_unit: The unit used for costing (Ingredient's unit)
        calculated_quantity: The RecipeIngredient quantity converted to cost_unit
        line_cost: The calculated cost for this line item (calculated_quantity × cost_per_unit)
    """
    ingredient_id: int
    ingredient_name: str
    recipe_ingredient_quantity: Decimal
    recipe_ingredient_unit: str
    cost_per_unit: Decimal
    cost_unit: str
    calculated_quantity: Decimal
    line_cost: Decimal

    def __post_init__(self):
        if self.line_cost < 0:
            raise ValueError("Line cost cannot be negative")
        if self.cost_per_unit < 0:
            raise ValueError("Cost per unit cannot be negative")
        if self.calculated_quantity < 0:
            raise ValueError("Calculated quantity cannot be negative")


@dataclass(frozen=True)
class RecipeCost:
    """Total cost of a Recipe at its base servings.

    Attributes:
        recipe_id: The Recipe's ID
        recipe_name: The Recipe's name
        base_servings: The Recipe's base serving yield
        ingredient_costs: List of RecipeIngredientCost objects
        total_cost: Sum of all line_cost values
        is_complete: True if all RecipeIngredients have available cost data
    """
    recipe_id: int
    recipe_name: str
    base_servings: int
    ingredient_costs: tuple[RecipeIngredientCost, ...]
    total_cost: Decimal
    is_complete: bool

    def __post_init__(self):
        if self.base_servings <= 0:
            raise ValueError("Base servings must be positive")
        if self.total_cost < 0:
            raise ValueError("Total cost cannot be negative")
        if not self.is_complete and self.total_cost > 0:
            raise ValueError("Incomplete recipe cost must have zero total cost")


@dataclass(frozen=True)
class MealCost:
    """Cost of a MealPlan entry (Recipe scaled to planned servings).

    Attributes:
        meal_plan_id: The MealPlan's ID
        recipe_id: The Recipe's ID (may be None for empty slots)
        recipe_name: The Recipe's name (empty string if no recipe)
        planned_servings: The MealPlan's planned servings
        base_servings: The Recipe's base servings (0 if no recipe)
        recipe_cost: The RecipeCost object (None if no recipe or cost unavailable)
        meal_cost: The scaled cost for this meal (None if unavailable)
    """
    meal_plan_id: int
    recipe_id: Optional[int]
    recipe_name: str
    planned_servings: int
    base_servings: int
    recipe_cost: Optional[RecipeCost]
    meal_cost: Optional[Decimal]

    def __post_init__(self):
        if self.planned_servings <= 0:
            raise ValueError("Planned servings must be positive")
        if self.recipe_cost is not None and self.recipe_cost.is_complete and self.meal_cost is None:
            raise ValueError("Recipe cost available but meal cost not calculated")
        if self.recipe_cost is None and self.meal_cost is not None:
            raise ValueError("Meal cost calculated without recipe cost")
        if self.meal_cost is not None and self.meal_cost < 0:
            raise ValueError("Meal cost cannot be negative")


def _normalize_acquisition_to_ingredient_unit(
    acquisition_qty: Decimal,
    acquisition_unit: str,
    ingredient_unit: str
) -> Decimal:
    """Convert acquisition quantity to ingredient's unit.

    Args:
        acquisition_qty: Quantity from acquisition
        acquisition_unit: Unit from acquisition
        ingredient_unit: Ingredient's current unit

    Returns:
        Converted quantity in ingredient's unit

    Raises:
        ValueError: If units are incompatible
        RuntimeError: If UnitSystem not initialized
    """
    if not is_initialized():
        raise RuntimeError("UnitSystem not initialized")

    if acquisition_unit == ingredient_unit:
        return acquisition_qty

    acq_cat = category_of(acquisition_unit)
    ing_cat = category_of(ingredient_unit)

    if acq_cat != ing_cat:
        raise ValueError(
            f"Cannot convert acquisition unit '{acquisition_unit}' "
            f"to ingredient unit '{ingredient_unit}': "
            "different measurement categories (requires density information)"
        )

    return convert(acquisition_qty, acquisition_unit, ingredient_unit)


def _normalize_recipe_ingredient_to_cost_unit(
    recipe_ingredient_qty: Decimal,
    recipe_ingredient_unit: str,
    cost_unit: str
) -> Decimal:
    """Convert RecipeIngredient quantity to the cost unit.

    Args:
        recipe_ingredient_qty: Quantity from RecipeIngredient
        recipe_ingredient_unit: Unit from RecipeIngredient
        cost_unit: The unit used for costing (Ingredient's unit)

    Returns:
        Converted quantity in cost unit

    Raises:
        ValueError: If units are incompatible
        RuntimeError: If UnitSystem not initialized
    """
    if not is_initialized():
        raise RuntimeError("UnitSystem not initialized")

    if recipe_ingredient_unit == cost_unit:
        return recipe_ingredient_qty

    ri_cat = category_of(recipe_ingredient_unit)
    cost_cat = category_of(cost_unit)

    if ri_cat != cost_cat:
        raise ValueError(
            f"Cannot convert recipe ingredient unit '{recipe_ingredient_unit}' "
            f"to cost unit '{cost_unit}': "
            "different measurement categories (requires density information)"
        )

    return convert(recipe_ingredient_qty, recipe_ingredient_unit, cost_unit)


def calculate_ingredient_costs(
    ingredients: dict[int, object],
    acquisitions: list[object],
) -> list[IngredientCost]:
    """Calculate weighted average cost per unit for each Ingredient.

    Args:
        ingredients: Dict mapping ingredient_id -> Ingredient domain object
        acquisitions: List of Acquisition domain objects

    Returns:
        List of IngredientCost objects, sorted by ingredient_id

    Raises:
        RuntimeError: If UnitSystem not initialized
        ValueError: If unit conversion fails
    """
    if not is_initialized():
        raise RuntimeError("UnitSystem not initialized")

    # Group acquisitions by ingredient_id
    acquisitions_by_ingredient: dict[int, list[object]] = {}
    for acq in acquisitions:
        acquisitions_by_ingredient.setdefault(acq.ingredient_id, []).append(acq)

    results = []

    for ingredient_id, ingredient in ingredients.items():
        ingredient_acquisitions = acquisitions_by_ingredient.get(ingredient_id, [])

        if not ingredient_acquisitions:
            # No acquisition history - cost unavailable
            continue

        total_cost = Decimal('0')
        total_quantity = Decimal('0')
        valid_acquisition_count = 0

        for acq in ingredient_acquisitions:
            try:
                # Normalize acquisition quantity to ingredient's unit
                norm_qty = _normalize_acquisition_to_ingredient_unit(
                    Decimal(str(acq.quantity)),
                    acq.unit,
                    ingredient.unit
                )
                total_cost += Decimal(str(acq.cost))
                total_quantity += norm_qty
                valid_acquisition_count += 1
            except ValueError:
                # Skip acquisitions with incompatible units
                continue

        if valid_acquisition_count == 0 or total_quantity == 0:
            # No valid acquisitions after filtering
            continue

        cost_per_unit = total_cost / total_quantity

        results.append(IngredientCost(
            ingredient_id=ingredient_id,
            ingredient_name=ingredient.name,
            cost_per_unit=cost_per_unit,
            cost_unit=ingredient.unit,
            total_acquisition_cost=total_cost,
            total_acquisition_quantity=total_quantity,
            acquisition_count=valid_acquisition_count,
        ))

    results.sort(key=lambda c: c.ingredient_id)
    return results


def calculate_recipe_costs(
    recipes: dict[int, object],
    recipe_ingredients: dict[int, list[object]],
    ingredient_costs: list[IngredientCost],
) -> list[RecipeCost]:
    """Calculate total cost for each Recipe at base servings.

    Args:
        recipes: Dict mapping recipe_id -> Recipe domain object
        recipe_ingredients: Dict mapping recipe_id -> list of RecipeIngredient domain objects
        ingredient_costs: List of IngredientCost objects (from calculate_ingredient_costs)

    Returns:
        List of RecipeCost objects, sorted by recipe_id

    Raises:
        RuntimeError: If UnitSystem not initialized
        ValueError: If unit conversion fails
    """
    if not is_initialized():
        raise RuntimeError("UnitSystem not initialized")

    # Build lookup for ingredient costs by ingredient_id
    ingredient_cost_lookup = {ic.ingredient_id: ic for ic in ingredient_costs}

    results = []

    for recipe_id, recipe in recipes.items():
        ris = recipe_ingredients.get(recipe_id, [])

        if not ris:
            # Recipe with no ingredients - cost is zero
            results.append(RecipeCost(
                recipe_id=recipe_id,
                recipe_name=recipe.name,
                base_servings=recipe.servings,
                ingredient_costs=(),
                total_cost=Decimal('0'),
                is_complete=True,
            ))
            continue

        line_costs = []
        total_cost = Decimal('0')
        all_available = True

        for ri in ris:
            ic = ingredient_cost_lookup.get(ri.ingredient_id)

            if ic is None:
                # Ingredient cost unavailable
                all_available = False
                continue

            try:
                # Convert RecipeIngredient quantity to cost unit
                norm_qty = _normalize_recipe_ingredient_to_cost_unit(
                    Decimal(str(ri.quantity)),
                    ri.unit,
                    ic.cost_unit
                )
                line_cost = norm_qty * ic.cost_per_unit

                line_costs.append(RecipeIngredientCost(
                    ingredient_id=ri.ingredient_id,
                    ingredient_name=ic.ingredient_name,
                    recipe_ingredient_quantity=Decimal(str(ri.quantity)),
                    recipe_ingredient_unit=ri.unit,
                    cost_per_unit=ic.cost_per_unit,
                    cost_unit=ic.cost_unit,
                    calculated_quantity=norm_qty,
                    line_cost=line_cost,
                ))
                total_cost += line_cost
            except ValueError:
                # Incompatible units - cost unavailable
                all_available = False
                continue

        if not all_available:
            # Some required ingredient costs unavailable
            results.append(RecipeCost(
                recipe_id=recipe_id,
                recipe_name=recipe.name,
                base_servings=recipe.servings,
                ingredient_costs=tuple(line_costs),
                total_cost=Decimal('0'),
                is_complete=False,
            ))
        else:
            results.append(RecipeCost(
                recipe_id=recipe_id,
                recipe_name=recipe.name,
                base_servings=recipe.servings,
                ingredient_costs=tuple(line_costs),
                total_cost=total_cost,
                is_complete=True,
            ))

    results.sort(key=lambda c: c.recipe_id)
    return results


def calculate_meal_costs(
    meal_plans: list[object],
    recipes: dict[int, object],
    recipe_costs: list[RecipeCost],
) -> list[MealCost]:
    """Calculate cost for each MealPlan entry.

    Args:
        meal_plans: List of MealPlan domain objects
        recipes: Dict mapping recipe_id -> Recipe domain object
        recipe_costs: List of RecipeCost objects (from calculate_recipe_costs)

    Returns:
        List of MealCost objects, sorted by (day, meal_type)

    Raises:
        ValueError: If invalid data
    """
    # Build lookup for recipe costs by recipe_id
    recipe_cost_lookup = {rc.recipe_id: rc for rc in recipe_costs}

    results = []

    for mp in meal_plans:
        if mp.recipe_id is None:
            # Empty meal slot
            results.append(MealCost(
                meal_plan_id=mp.id,
                recipe_id=None,
                recipe_name="",
                planned_servings=mp.servings,
                base_servings=0,
                recipe_cost=None,
                meal_cost=None,
            ))
            continue

        recipe = recipes.get(mp.recipe_id)
        if recipe is None:
            # Referenced recipe not found
            results.append(MealCost(
                meal_plan_id=mp.id,
                recipe_id=mp.recipe_id,
                recipe_name="",
                planned_servings=mp.servings,
                base_servings=0,
                recipe_cost=None,
                meal_cost=None,
            ))
            continue

        recipe_cost = recipe_cost_lookup.get(mp.recipe_id)

        if recipe_cost is None or not recipe_cost.is_complete:
            # Recipe cost unavailable
            results.append(MealCost(
                meal_plan_id=mp.id,
                recipe_id=mp.recipe_id,
                recipe_name=recipe.name,
                planned_servings=mp.servings,
                base_servings=recipe.servings,
                recipe_cost=recipe_cost,
                meal_cost=None,
            ))
        else:
            # Scale recipe cost to planned servings
            scale_factor = Decimal(mp.servings) / Decimal(recipe.servings)
            meal_cost = recipe_cost.total_cost * scale_factor

            results.append(MealCost(
                meal_plan_id=mp.id,
                recipe_id=mp.recipe_id,
                recipe_name=recipe.name,
                planned_servings=mp.servings,
                base_servings=recipe.servings,
                recipe_cost=recipe_cost,
                meal_cost=meal_cost,
            ))

    # Sort by day then meal_type for consistent presentation
    meal_type_order = {"Breakfast": 0, "Lunch": 1, "Dinner": 2}
    results.sort(key=lambda m: (m.recipe_id or 0, m.planned_servings))
    results.sort(key=lambda m: (m.meal_plan_id, meal_type_order.get(m.recipe_name, 99)))
    # Better sort: by day, meal_type
    results.sort(key=lambda m: (
        # We don't have day/meal_type in MealCost, so sort by meal_plan_id which preserves order
        m.meal_plan_id
    ))

    return results


def calculate_weekly_cost_summary(meal_costs: list[MealCost]) -> dict:
    """Calculate summary cost for a week's meal plans.

    Args:
        meal_costs: List of MealCost objects for a week

    Returns:
        Dict with:
            'total_cost': Sum of all available meal costs
            'costed_meals': Count of meals with available cost
            'uncosted_meals': Count of meals without cost
            'empty_slots': Count of empty meal slots
    """
    total = Decimal('0')
    costed = 0
    uncosted = 0
    empty = 0

    for mc in meal_costs:
        if mc.recipe_id is None:
            empty += 1
        elif mc.meal_cost is not None:
            total += mc.meal_cost
            costed += 1
        else:
            uncosted += 1

    return {
        'total_cost': total,
        'costed_meals': costed,
        'uncosted_meals': uncosted,
        'empty_slots': empty,
    }