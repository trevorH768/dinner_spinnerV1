"""Dinner Spinner V1 domain entities."""

from dinner_spinner.domain.ingredient import Ingredient
from dinner_spinner.domain.inventory_category import InventoryCategory
from dinner_spinner.domain.recipe import Recipe
from dinner_spinner.domain.recipe_ingredient import RecipeIngredient
from dinner_spinner.domain.meal_plan import MealPlan
from dinner_spinner.domain.acquisition import Acquisition
from dinner_spinner.domain.consumption import Consumption
from dinner_spinner.domain.waste import Waste
from dinner_spinner.domain.demand import IngredientDemand, calculate_demand, calculate_demand_for_week

# UnitSystem is a module, not a class - import the module
import dinner_spinner.domain.unit_system as UnitSystem

__all__ = [
    "Ingredient",
    "InventoryCategory",
    "Recipe",
    "RecipeIngredient",
    "MealPlan",
    "Acquisition",
    "Consumption",
    "Waste",
    "IngredientDemand",
    "calculate_demand",
    "calculate_demand_for_week",
    "UnitSystem",
]