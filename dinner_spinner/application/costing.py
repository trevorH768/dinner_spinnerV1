"""Application services for costing calculations (Slice 6).

This module provides the application-layer functions that orchestrate
retrieval of data and delegate to domain costing functions.
"""

from typing import Optional
from sqlalchemy.orm import Session

from dinner_spinner.domain.costing import (
    IngredientCost,
    RecipeCost,
    MealCost,
    calculate_ingredient_costs,
    calculate_recipe_costs,
    calculate_meal_costs,
    calculate_weekly_cost_summary,
)
from dinner_spinner.domain.unit_system import is_initialized, initialize


class CostingError(Exception):
    """Base exception for costing calculation errors."""
    pass


class UnitSystemNotInitializedError(CostingError):
    """Raised when UnitSystem is not initialized."""
    pass


def get_ingredient_costs(db_session) -> list[IngredientCost]:
    """Calculate ingredient costs from acquisition history.

    Args:
        db_session: SQLAlchemy database session

    Returns:
        List of IngredientCost objects with available cost data

    Raises:
        UnitSystemNotInitializedError: If UnitSystem not initialized
        CostingError: If calculation fails
    """
    if not is_initialized():
        raise UnitSystemNotInitializedError("UnitSystem not initialized; call initialize() first")

    from dinner_persistence.models import Ingredient, Acquisition

    # Get all ingredients
    ingredients_db = db_session.query(Ingredient).all()
    ingredients = {i.id: i.to_domain() for i in ingredients_db}

    # Get all acquisitions
    acquisitions_db = db_session.query(Acquisition).all()
    acquisitions = [a.to_domain() for a in acquisitions_db]

    try:
        return calculate_ingredient_costs(ingredients, acquisitions)
    except (ValueError, RuntimeError) as e:
        raise CostingError(str(e)) from e


def get_recipe_costs(db_session, recipe_ids: Optional[list[int]] = None) -> list[RecipeCost]:
    """Calculate recipe costs for given or all recipes.

    Args:
        db_session: SQLAlchemy database session
        recipe_ids: Optional list of recipe IDs to cost (default: all)

    Returns:
        List of RecipeCost objects

    Raises:
        UnitSystemNotInitializedError: If UnitSystem not initialized
        CostingError: If calculation fails
    """
    if not is_initialized():
        raise UnitSystemNotInitializedError("UnitSystem not initialized; call initialize() first")

    from dinner_persistence.models import Recipe, RecipeIngredient, Ingredient, Acquisition

    # Get recipes
    if recipe_ids:
        recipes_db = db_session.query(Recipe).filter(Recipe.id.in_(recipe_ids)).all()
    else:
        recipes_db = db_session.query(Recipe).all()
    recipes = {r.id: r.to_domain() for r in recipes_db}

    # Get recipe ingredients
    recipe_ingredients_map = {}
    if recipes:
        if recipe_ids:
            ris = db_session.query(RecipeIngredient).filter(
                RecipeIngredient.recipe_id.in_(recipe_ids)
            ).all()
        else:
            ris = db_session.query(RecipeIngredient).all()
        for ri in ris:
            if ri.recipe_id not in recipe_ingredients_map:
                recipe_ingredients_map[ri.recipe_id] = []
            recipe_ingredients_map[ri.recipe_id].append(ri.to_domain())

    # Get ingredient costs (need all ingredients for cost lookup)
    ingredients_db = db_session.query(Ingredient).all()
    ingredients = {i.id: i.to_domain() for i in ingredients_db}
    acquisitions_db = db_session.query(Acquisition).all()
    acquisitions = [a.to_domain() for a in acquisitions_db]

    try:
        ingredient_costs = calculate_ingredient_costs(ingredients, acquisitions)
        return calculate_recipe_costs(recipes, recipe_ingredients_map, ingredient_costs)
    except (ValueError, RuntimeError) as e:
        raise CostingError(str(e)) from e


def get_meal_costs_for_week(db_session, week_start: int) -> list[MealCost]:
    """Calculate meal costs for a specific week.

    Args:
        db_session: SQLAlchemy database session
        week_start: The week start date (YYYYMMDD format)

    Returns:
        List of MealCost objects for the week

    Raises:
        UnitSystemNotInitializedError: If UnitSystem not initialized
        CostingError: If calculation fails
    """
    if not is_initialized():
        raise UnitSystemNotInitializedError("UnitSystem not initialized; call initialize() first")

    from dinner_persistence.models import MealPlan, Recipe, RecipeIngredient, Ingredient, Acquisition

    # Get meal plans for the week
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

    # Get all ingredients and acquisitions for cost calculation
    ingredients_db = db_session.query(Ingredient).all()
    ingredients = {i.id: i.to_domain() for i in ingredients_db}
    acquisitions_db = db_session.query(Acquisition).all()
    acquisitions = [a.to_domain() for a in acquisitions_db]

    try:
        # Calculate ingredient costs
        ingredient_costs = calculate_ingredient_costs(ingredients, acquisitions)

        # Calculate recipe costs
        recipe_costs = calculate_recipe_costs(recipes, recipe_ingredients_map, ingredient_costs)

        # Calculate meal costs
        meal_plans_domain = [mp.to_domain() for mp in meal_plans]
        return calculate_meal_costs(meal_plans_domain, recipes, recipe_costs)
    except (ValueError, RuntimeError) as e:
        raise CostingError(str(e)) from e


def get_weekly_cost_summary(db_session, week_start: int) -> dict:
    """Get cost summary for a week's meal plans.

    Args:
        db_session: SQLAlchemy database session
        week_start: The week start date (YYYYMMDD format)

    Returns:
        Dict with total_cost, costed_meals, uncosted_meals, empty_slots
    """
    meal_costs = get_meal_costs_for_week(db_session, week_start)
    return calculate_weekly_cost_summary(meal_costs)


if __name__ == "__main__":
    # For manual testing
    from dinner_spinner import create_app
    app = create_app()
    with app.app_context():
        from flask import current_app
        db = current_app.extensions['sqlalchemy']
        initialize()
        costs = get_ingredient_costs(db.session)
        for c in costs:
            print(f"{c.ingredient_name}: {c.cost_per_unit} / {c.cost_unit}")