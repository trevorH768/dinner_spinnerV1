"""Application services for inventory requirement calculation.

This module provides the application-layer function for calculating
inventory requirements (Available Inventory & Net Requirement) from
meal plans and current inventory.
"""

from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session

from dinner_spinner.domain.demand import calculate_demand_for_week, IngredientDemand
from dinner_spinner.domain.inventory_requirement import calculate_inventory_requirements, IngredientRequirement
from dinner_spinner.domain.unit_system import is_initialized, initialize


class InventoryRequirementError(Exception):
    """Base exception for inventory requirement calculation errors."""
    pass


class UnitSystemNotInitializedError(InventoryRequirementError):
    """Raised when UnitSystem is not initialized."""
    pass


class MissingIngredientError(InventoryRequirementError):
    """Raised when an ingredient is not found."""
    pass


class IncompatibleUnitsError(InventoryRequirementError):
    """Raised when demand and inventory units are incompatible."""
    pass


def calculate_weekly_inventory_requirements(
    db_session,
    week_start: int,
) -> list:
    """Calculate inventory requirements for a specific week.

    This function orchestrates the retrieval of demand and inventory,
    then calculates the net requirements.

    Args:
        db_session: SQLAlchemy database session
        week_start: The week start date (YYYYMMDD format)

    Returns:
        List of IngredientRequirement objects with ingredient names populated

    Raises:
        UnitSystemNotInitializedError: If UnitSystem not initialized
        InventoryRequirementError: If calculation fails (e.g., incompatible units)
    """
    if not is_initialized():
        raise UnitSystemNotInitializedError("UnitSystem not initialized; call initialize() first")

    from dinner_persistence.models import MealPlan, Recipe, RecipeIngredient, Ingredient

    # Retrieve meal plans for the week
    meal_plans = db_session.query(MealPlan).filter(
        MealPlan.week_start == week_start
    ).order_by(MealPlan.day, MealPlan.meal_type).all()

    if not meal_plans:
        return []

    # Get all referenced recipes
    recipe_ids = {mp.recipe_id for mp in meal_plans if mp.recipe_id is not None}
    recipes = {}
    if recipe_ids:
        recipes_db = db_session.query(Recipe).filter(Recipe.id.in_(recipe_ids)).all()
        recipes = {r.id: r.to_domain() for r in recipes_db}

    # Get all recipe ingredients
    recipe_ingredients_map = {}
    if recipe_ids:
        ris = db_session.query(RecipeIngredient).filter(
            RecipeIngredient.recipe_id.in_(recipe_ids)
        ).all()
        for ri in ris:
            if ri.recipe_id not in recipe_ingredients_map:
                recipe_ingredients_map[ri.recipe_id] = []
            recipe_ingredients_map[ri.recipe_id].append(ri.to_domain())

    # Get all ingredients (for names and current quantities)
    ingredient_ids = set()
    for ri_list in recipe_ingredients_map.values():
        for ri in ri_list:
            ingredient_ids.add(ri.ingredient_id)

    ingredients = {}
    if ingredient_ids:
        ingredients_db = db_session.query(Ingredient).filter(
            Ingredient.id.in_(ingredient_ids)
        ).all()
        ingredients = {i.id: i.to_domain() for i in ingredients_db}

    # Also include ingredients that might be in inventory but not in recipes
    # (for the case where we have inventory but no demand - though we won't include those in requirements)
    all_ingredients_db = db_session.query(Ingredient).all()
    all_ingredients = {i.id: i.to_domain() for i in all_ingredients_db}

    # Convert meal plans to domain
    meal_plans_domain = [mp.to_domain() for mp in meal_plans]

    # First calculate demand
    try:
        demands = calculate_demand_for_week(
            meal_plans=meal_plans_domain,
            recipes=recipes,
            recipe_ingredients=recipe_ingredients_map,
            ingredients=ingredients,
        )
    except ValueError as e:
        # Wrap domain calculation errors
        raise InventoryRequirementError(str(e)) from e

    # Calculate inventory requirements
    try:
        requirements = calculate_inventory_requirements(
            demands=demands,
            ingredients=all_ingredients,
        )
        return requirements
    except ValueError as e:
        # Wrap domain calculation errors
        raise IncompatibleUnitsError(str(e)) from e


def get_inventory_requirements_for_week(
    db_session,
    week_start: int,
) -> list:
    """Calculate and return inventory requirements for a specific week.

    This is a convenience wrapper that ensures UnitSystem is initialized.

    Args:
        db_session: SQLAlchemy database session
        week_start: The week start date (YYYYMMDD format)

    Returns:
        List of IngredientRequirement objects
    """
    if not is_initialized():
        initialize()
    return calculate_weekly_inventory_requirements(db_session, week_start)


if __name__ == "__main__":
    # For manual testing
    from dinner_spinner import create_app
    app = create_app()
    with app.app_context():
        from flask import current_app
        db = current_app.extensions['sqlalchemy']
        initialize()
        reqs = get_inventory_requirements_for_week(db.session, 20260101)
        for r in reqs:
            print(f"{r.ingredient_name}: demand={r.demand_quantity} {r.demand_unit} available={r.available_quantity} {r.available_unit} net={r.net_requirement_quantity} {r.net_requirement_unit}")