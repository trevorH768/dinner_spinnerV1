"""Shopping List: A calculated projection of the Net Requirements for the
selected calendar month, presented as a user-facing list of Ingredients
and quantities that need to be acquired.

The shopping list is a projection.
The user generates the shopping list for the calendar month corresponding
to when the action is performed.
If the Meal Plan or inventory changes, the calculated Shopping List changes accordingly.
There are no stale stored shopping lists.
"""

from dataclasses import dataclass
from decimal import Decimal

from dinner_spinner.domain.inventory_requirement import IngredientRequirement
from dinner_spinner.domain.unit_system import is_initialized


@dataclass(frozen=True)
class ShoppingListItem:
    """A calculated shopping list item representing a net requirement.

    This is a derived projection, not an authoritative database entity.
    It represents an Ingredient and the net quantity that needs to be acquired.

    Attributes:
        ingredient_id: The ID of the required Ingredient
        ingredient_name: The name of the required Ingredient (for display)
        quantity: The net quantity required (net_requirement_quantity)
        unit: The unit of the net requirement (net_requirement_unit)
    """
    ingredient_id: int
    ingredient_name: str
    quantity: Decimal
    unit: str

    def __post_init__(self):
        if self.quantity < 0:
            raise ValueError("Shopping list quantity cannot be negative")
        if not self.unit or not self.unit.strip():
            raise ValueError("Shopping list unit is required")

    def __eq__(self, other):
        if not isinstance(other, ShoppingListItem):
            return NotImplemented
        return (self.ingredient_id == other.ingredient_id
                and self.quantity == other.quantity
                and self.unit == other.unit)

    def __repr__(self):
        return (f"<ShoppingListItem ingredient_id={self.ingredient_id}"
                f" name={self.ingredient_name!r} qty={self.quantity} {self.unit}>")


def calculate_shopping_list(requirements: list) -> list:
    """Calculate the shopping list from inventory requirements.

    The shopping list is a projection of InventoryRequirements where
    net_requirement_quantity > 0. Items with net_requirement_quantity == 0
    are excluded (no need to purchase).

    Args:
        requirements: List of IngredientRequirement objects from Slice 4

    Returns:
        List of ShoppingListItem objects, sorted by ingredient_name then ingredient_id
        for deterministic ordering.
    """
    if not is_initialized():
        raise RuntimeError("UnitSystem not initialized; call initialize() first")

    items = []
    for req in requirements:
        if req.net_requirement_quantity > 0:
            item = ShoppingListItem(
                ingredient_id=req.ingredient_id,
                ingredient_name=req.ingredient_name,
                quantity=req.net_requirement_quantity,
                unit=req.net_requirement_unit,
            )
            items.append(item)

    # Deterministic ordering: ingredient_name then ingredient_id
    items.sort(key=lambda item: (item.ingredient_name.lower(), item.ingredient_id))
    return items


if __name__ == "__main__":
    # For manual testing
    from dinner_spinner.domain.unit_system import initialize, reset
    from dinner_spinner.domain.ingredient import Ingredient
    from dinner_spinner.domain.demand import IngredientDemand
    from dinner_spinner.domain.inventory_requirement import (
        calculate_inventory_requirements, IngredientRequirement
    )
    from decimal import Decimal

    reset()
    initialize()

    # Test 1: Basic shopping list
    print("Test 1: Basic shopping list")
    requirements = [
        IngredientRequirement(
            ingredient_id=1, ingredient_name="Flour",
            demand_quantity=2000, demand_unit="g",
            available_quantity=1000, available_unit="g",
            net_requirement_quantity=800, net_requirement_unit="g"
        ),
        IngredientRequirement(
            ingredient_id=2, ingredient_name="Milk",
            demand_quantity=250, demand_unit="ml",
            available_quantity=2000, available_unit="ml",
            net_requirement_quantity=0, net_requirement_unit="ml"
        ),
        IngredientRequirement(
            ingredient_id=3, ingredient_name="Eggs",
            demand_quantity=2, demand_unit="each",
            available_quantity=12, available_unit="each",
            net_requirement_quantity=0, net_requirement_unit="each"
        ),
        IngredientRequirement(
            ingredient_id=4, ingredient_name="Flour",
            demand_quantity=500, demand_unit="g",
            available_quantity=0, available_unit="g",
            net_requirement_quantity=500, net_requirement_unit="g"
        ),
    ]
    shopping_list = calculate_shopping_list(requirements)
    for item in shopping_list:
        print(f"  {item.ingredient_name}: {item.quantity} {item.unit}")
    # Should have Flour (800g) only
    assert len(shoppng_list) == 1
    assert shopping_list[0].ingredient_name == "Flour"
    assert shopping_list[0].quantity == 800
    assert shopping_list[0].unit == "g"

    # Test 2: Empty shopping list
    print("Test 2: Empty shopping list")
    requirements = [
        IngredientRequirement(
            ingredient_id=1, ingredient_name="Flour",
            demand_quantity=1000, demand_unit="g",
            available_quantity=1000, available_unit="g",
            net_requirement_quantity=0, net_requirement_unit="g"
        ),
    ]
    shopping_list = calculate_shopping_list(requirements)
    assert len(shopping_list) == 0
    print("  Empty list OK")

    # Test 3: Multiple items with positive net requirements
    print("Test 3: Multiple items")
    from dinner_spinner.domain.inventory_requirement import IngredientRequirement
    from decimal import Decimal
    requirements = [
        IngredientRequirement(
            ingredient_id=1, ingredient_name="Flour",
            demand_quantity=Decimal("2000"), demand_unit="g",
            available_quantity=Decimal("1000"), available_unit="g",
            net_requirement_quantity=Decimal("800"), net_requirement_unit="g"
        ),
        IngredientRequirement(
            ingredient_id=2, ingredient_name="Sugar",
            demand_quantity=Decimal("1000"), demand_unit="g",
            available_quantity=Decimal("0"), available_unit="g",
            net_requirement_quantity=Decimal("1000"), net_requirement_unit="g"
        ),
    ]
    shopping_list = calculate_shopping_list(requirements)
    assert len(shopping_list) == 2
    # Deterministic ordering: ingredient_name then ingredient_id
    assert shopping_list[0].ingredient_name == "Flour"
    assert shopping_list[1].ingredient_name == "Sugar"
    assert shopping_list[0].quantity == 800
    assert shopping_list[1].quantity == 1000

    print("\nAll tests passed!")