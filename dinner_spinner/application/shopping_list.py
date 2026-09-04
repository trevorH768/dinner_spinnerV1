"""Application services for shopping list calculation (Slice 5).

This module provides the application-layer function for calculating
the shopping list from inventory requirements for a specific week.
"""

from dinner_spinner.application.inventory_requirements import get_inventory_requirements_for_week
from dinner_spinner.domain.shopping_list import calculate_shopping_list, ShoppingListItem


class ShoppingListError(Exception):
    """Base exception for shopping list calculation errors."""
    pass


class UnitSystemNotInitializedError(Exception):
    """Raised when UnitSystem is not initialized."""
    pass


def get_shopping_list_for_week(
    db_session,
    week_start: int,
) -> list:
    """Calculate and return shopping list for a specific week.

    This is a convenience wrapper that ensures UnitSystem is initialized.

    Args:
        db_session: SQLAlchemy database session
        week_start: The week start date (YYYYMMDD format)

    Returns:
        List of ShoppingListItem objects
    """
    from dinner_spinner.application.inventory_requirements import get_inventory_requirements_for_week
    from dinner_spinner.domain.shopping_list import calculate_shopping_list

    # Delegate to Slice 4 for inventory requirements
    requirements = get_inventory_requirements_for_week(db_session, week_start)
    
    # Calculate shopping list from requirements (pure domain function)
    return calculate_shopping_list(requirements)


if __name__ == "__main__":
    # For manual testing
    from dinner_spinner import create_app
    app = create_app()
    with app.app_context():
        from flask import current_app
        db = current_app.extensions['sqlalchemy']
        initialize()
        shopping_list = get_shopping_list_for_week(db.session, 20260101)
        for item in shopping_list:
            print(f"{item.ingredient_name}: {item.quantity} {item.unit}")