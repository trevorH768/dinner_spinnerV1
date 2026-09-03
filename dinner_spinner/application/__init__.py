"""Dinner Spinner V1 — Application services."""

from dinner_spinner.application.inventory_events import (
    record_acquisition,
    record_consumption,
    record_waste,
    get_ingredient_history,
    get_global_event_history,
    InventoryEventError,
    InvalidQuantityError,
    InvalidUnitError,
    InsufficientInventoryError,
    IngredientNotFoundError,
    UnitSystemNotInitializedError,
)
from dinner_spinner.application.demand import (
    calculate_weekly_demand,
    get_demand_for_week,
    DemandCalculationError,
    MissingRecipeError,
    IncompatibleUnitsError,
    IngredientNotFoundError as DemandIngredientNotFoundError,
    UnitSystemNotInitializedError as DemandUnitSystemNotInitializedError,
)
from dinner_spinner.application.inventory_requirements import (
    calculate_weekly_inventory_requirements,
    get_inventory_requirements_for_week,
    InventoryRequirementError,
    UnitSystemNotInitializedError as IRUnitSystemNotInitializedError,
    MissingIngredientError,
    IncompatibleUnitsError as IRIncompatibleUnitsError,
)

__all__ = [
    "record_acquisition",
    "record_consumption",
    "record_waste",
    "get_ingredient_history",
    "get_global_event_history",
    "InventoryEventError",
    "InvalidQuantityError",
    "InvalidUnitError",
    "InsufficientInventoryError",
    "IngredientNotFoundError",
    "UnitSystemNotInitializedError",
    "calculate_weekly_demand",
    "get_demand_for_week",
    "DemandCalculationError",
    "MissingRecipeError",
    "IncompatibleUnitsError",
    "DemandIngredientNotFoundError",
    "DemandUnitSystemNotInitializedError",
    "calculate_weekly_inventory_requirements",
    "get_inventory_requirements_for_week",
    "InventoryRequirementError",
    "IRUnitSystemNotInitializedError",
    "MissingIngredientError",
    "IRIncompatibleUnitsError",
]