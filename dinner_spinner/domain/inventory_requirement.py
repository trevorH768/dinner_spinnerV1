"""Inventory Requirement: A calculated projection of ingredient requirements after
accounting for available inventory.

This module provides the domain-level calculation for determining what additional
ingredients are needed to satisfy demand, given current inventory levels.

This is a derived projection, not an authoritative database entity.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from dinner_spinner.domain.unit_system import convert, category_of, is_initialized, validate_unit
from dinner_spinner.domain.demand import IngredientDemand


@dataclass(frozen=True)
class IngredientRequirement:
    """A calculated inventory requirement for a specific Ingredient.

    This is a derived projection representing the net requirement after
    accounting for current inventory against demand.

    This is NOT an authoritative database entity - it's a calculated projection.

    Attributes:
        ingredient_id: The ID of the required Ingredient
        ingredient_name: The name of the required Ingredient (for display)
        demand_quantity: The total required quantity from meal plan demand
        demand_unit: The unit of the demand quantity
        available_quantity: The currently available quantity in inventory
        available_unit: The unit of the available quantity
        net_requirement_quantity: The net quantity required (max(0, demand - available))
        net_requirement_unit: The unit of the net requirement quantity
    """
    ingredient_id: int
    ingredient_name: str
    demand_quantity: Decimal
    demand_unit: str
    available_quantity: Decimal
    available_unit: str
    net_requirement_quantity: Decimal
    net_requirement_unit: str

    def __post_init__(self):
        if self.demand_quantity < 0:
            raise ValueError("Demand quantity cannot be negative")
        if self.available_quantity < 0:
            raise ValueError("Available quantity cannot be negative")
        if self.net_requirement_quantity < 0:
            raise ValueError("Net requirement quantity cannot be negative")
        if not self.demand_unit or not self.demand_unit.strip():
            raise ValueError("Demand unit is required")
        if not self.available_unit or not self.available_unit.strip():
            raise ValueError("Available unit is required")
        if not self.net_requirement_unit or not self.net_requirement_unit.strip():
            raise ValueError("Net requirement unit is required")

    def __eq__(self, other):
        if not isinstance(other, IngredientRequirement):
            return NotImplemented
        return (self.ingredient_id == other.ingredient_id
                and self.demand_quantity == other.demand_quantity
                and self.demand_unit == other.demand_unit
                and self.available_quantity == other.available_quantity
                and self.available_unit == other.available_unit
                and self.net_requirement_quantity == other.net_requirement_quantity
                and self.net_requirement_unit == other.net_requirement_unit)

    def __repr__(self):
        return (f"<IngredientRequirement ingredient_id={self.ingredient_id}"
                f" name={self.ingredient_name!r} "
                f"demand={self.demand_quantity} {self.demand_unit} "
                f"available={self.available_quantity} {self.available_unit} "
                f"net={self.net_requirement_quantity} {self.net_requirement_unit}>")


def _convert_quantity_to_unit(quantity: Decimal, from_unit: str, to_unit: str) -> Decimal:
    """Convert a quantity from one unit to another using the UnitSystem.
    
    Args:
        quantity: The quantity to convert
        from_unit: The source unit
        to_unit: The target unit
        
    Returns:
        The converted quantity in the target unit
        
    Raises:
        ValueError: If units are incompatible or not recognized
        RuntimeError: If UnitSystem not initialized
    """
    if not is_initialized():
        raise RuntimeError("UnitSystem not initialized; call initialize() first")
    
    if not validate_unit(from_unit):
        raise ValueError(f"Unit '{from_unit}' is not a recognized unit")
    if not validate_unit(to_unit):
        raise ValueError(f"Unit '{to_unit}' is not a recognized unit")
    
    if from_unit == to_unit:
        return quantity
    
    from_cat = category_of(from_unit)
    to_cat = category_of(to_unit)
    if from_cat != to_cat:
        raise ValueError(
            f"Cannot convert '{from_unit}' to '{to_unit}': "
            "different measurement categories (requires density information)"
        )
    
    return convert(quantity, from_unit, to_unit)


def _aggregate_compatible_quantities(qty1: Decimal, unit1: str, qty2: Decimal, unit2: str) -> tuple[Decimal, str]:
    """Aggregate two quantities with potentially different but compatible units.
    
    Returns the combined quantity in the unit of the first quantity.
    Raises ValueError if units are incompatible.
    
    Returns:
        tuple of (aggregated_quantity, unit)
    """
    if unit1 == unit2:
        return qty1 + qty2, unit1
    
    # Convert qty2 to unit1
    qty2_converted = _convert_quantity_to_unit(qty2, unit2, unit1)
    return qty1 + qty2_converted, unit1


def calculate_inventory_requirements(
    demands: list,
    ingredients: dict,
) -> list:
    """Calculate inventory requirements by comparing demand against current inventory.
    
    This is the core calculation function for Slice 4. It:
    1. Takes the demand projections from Slice 3
    2. Gets current inventory levels from Ingredient records
    3. Matches by ingredient_id
    4. Converts units where necessary using UnitSystem
    4. Calculates net requirement = max(demand - available, 0)
    
    Args:
        demands: List of IngredientDemand objects from Slice 3
        ingredients: Dict mapping ingredient_id -> Ingredient domain object (current inventory)
    
    Returns:
        List of IngredientRequirement objects, one per unique ingredient in demand
        
    Raises:
        ValueError: If unit conversion fails or units are incompatible
        RuntimeError: If UnitSystem not initialized
    """
    if not is_initialized():
        raise RuntimeError("UnitSystem not initialized; call initialize() first")
    
    # Build inventory map by ingredient_id
    inventory_map = {}
    for ing in ingredients.values():
        inventory_map[ing.id] = (Decimal(str(ing.quantity)), ing.unit)
    
    requirements = []
    
    for demand in demands:
        ingredient_id = demand.ingredient_id
        demand_qty = demand.quantity
        demand_unit = demand.unit
        
        # Get current inventory for this ingredient
        if ingredient_id in inventory_map:
            avail_qty, avail_unit = inventory_map[ingredient_id]
        else:
            # No inventory record - available is zero
            avail_qty = Decimal('0')
            avail_unit = demand_unit  # Use demand unit for zero
        
        # Aggregate demand with inventory (convert units if necessary)
        try:
            if demand_unit != avail_unit and avail_qty > 0:
                # Convert available to demand's unit for comparison
                avail_in_demand_unit = _convert_quantity_to_unit(avail_qty, avail_unit, demand_unit)
            else:
                avail_in_demand_unit = avail_qty
        except ValueError as e:
            # Incompatible units - cannot compare
            raise ValueError(
                f"Cannot compare demand ({demand_unit}) with inventory ({avail_unit}) "
                f"for ingredient {demand.ingredient_name}: {e}"
            )
        
        # Calculate net requirement: max(demand - available, 0)
        net_qty = demand_qty - avail_in_demand_unit
        if net_qty < 0:
            net_qty = Decimal('0')
        
        # Use demand's unit as the net requirement unit (consistent with demand)
        net_unit = demand_unit
        
        requirement = IngredientRequirement(
            ingredient_id=ingredient_id,
            ingredient_name=demand.ingredient_name,
            demand_quantity=demand_qty,
            demand_unit=demand_unit,
            available_quantity=avail_qty,
            available_unit=avail_unit,
            net_requirement_quantity=net_qty,
            net_requirement_unit=net_unit,
        )
        requirements.append(requirement)
    
    # Sort by ingredient_id for deterministic ordering
    requirements.sort(key=lambda r: r.ingredient_id)
    
    return requirements


if __name__ == "__main__":
    # For manual testing
    from dinner_spinner.domain.unit_system import initialize, reset
    from dinner_spinner.domain.ingredient import Ingredient
    from dinner_spinner.domain.demand import IngredientDemand
    from decimal import Decimal
    
    reset()
    initialize()
    
    # Test 1: Demand > inventory
    print("Test 1: Demand > Inventory")
    demands = [IngredientDemand(1, "Flour", Decimal("2000"), "g")]
    ingredients = {1: Ingredient(1, "Flour", None, 1200, "g")}
    reqs = calculate_inventory_requirements(demands, {1: Ingredient(1, "Flour", None, 1200, "g")})
    print(f"Demand: 2000g, Available: 1200g -> Net: {reqs[0].net_requirement_quantity} {reqs[0].net_requirement_unit}")
    assert reqs[0].net_requirement_quantity == Decimal("800")
    
    # Test 2: Demand == inventory
    print("Test 2: Demand == Inventory")
    demands = [IngredientDemand(1, "Flour", Decimal("1000"), "g")]
    ingredients = {1: Ingredient(1, "Flour", None, 1000, "g")}
    reqs = calculate_inventory_requirements(demands, {1: Ingredient(1, "Flour", None, 1000, "g")})
    print(f"Demand: 1000g, Available: 1000g -> Net: {reqs[0].net_requirement_quantity} {reqs[0].net_requirement_unit}")
    assert reqs[0].net_requirement_quantity == Decimal("0")
    
    # Test 3: Inventory > Demand (surplus)
    print("Test 3: Inventory > Demand")
    demands = [IngredientDemand(1, "Flour", Decimal("1000"), "g")]
    ingredients = {1: Ingredient(1, "Flour", None, 1500, "g")}
    reqs = calculate_inventory_requirements(demands, {1: Ingredient(1, "Flour", None, 1500, "g")})
    print(f"Demand: 1000g, Available: 1500g -> Net: {reqs[0].net_requirement_quantity} {reqs[0].net_requirement_unit}")
    assert reqs[0].net_requirement_quantity == Decimal("0")
    
    # Test 4: Zero inventory
    print("Test 4: Zero inventory")
    demands = [IngredientDemand(1, "Flour", Decimal("1000"), "g")]
    ingredients = {1: Ingredient(1, "Flour", None, 0, "g")}
    reqs = calculate_inventory_requirements(demands, {1: Ingredient(1, "Flour", None, 0, "g")})
    print(f"Demand: 1000g, Available: 0g -> Net: {reqs[0].net_requirement_quantity} {reqs[0].net_requirement_unit}")
    assert reqs[0].net_requirement_quantity == Decimal("1000")
    
    # Test 5: Cross-unit conversion
    print("Test 5: Cross-unit (kg vs g)")
    demands = [IngredientDemand(1, "Flour", Decimal("2"), "kg")]
    ingredients = {1: Ingredient(1, "Flour", None, 1500, "g")}
    reqs = calculate_inventory_requirements(demands, {1: Ingredient(1, "Flour", None, 1500, "g")})
    print(f"Demand: 2kg, Available: 1500g -> Net: {reqs[0].net_requirement_quantity} {reqs[0].net_requirement_unit}")
    # 2kg = 2000g, available = 1500g, net = 500g = 0.5kg
    assert reqs[0].net_requirement_quantity == Decimal("0.5")
    
    print("\nAll tests passed!")