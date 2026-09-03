"""An ingredient, identified by its own record.

An Ingredient has a name, current non-negative quantity, unit, and optional
user-assigned Inventory Category.  An Ingredient may be referenced by many
Recipes but may appear only once within any individual Recipe.  Zero quantity
is valid.  Ingredients are never automatically deleted, merged, categorized,
or recreated.  An Ingredient cannot be deleted while referenced by a
RecipeIngredient.

Ingredient represents the household's current inventory state.  The Ingredient
itself is the inventory holding.  There is no separate Container entity in V1.
"""

from dinner_spinner.domain.unit_system import validate_unit, is_initialized, convert, category_of


class Ingredient:
    """A user-defined, user-managed physical inventory holding identified by
    its own record.  It has a name, current non-negative quantity, unit, and
    optional user-assigned Inventory Category.
    """

    def __init__(self, id: int, name: str, inventory_category_id: int | None,
                 quantity: float, unit: str):
        if not name or not name.strip():
            raise ValueError("Ingredient name is required")
        self.id = id
        self.name = name.strip()
        self.inventory_category_id = inventory_category_id
        if quantity < 0:
            raise ValueError("Ingredient quantity must be non-negative")
        self.quantity = quantity
        if not unit or not unit.strip():
            raise ValueError("Ingredient unit is required")
        self.unit = unit.strip()
        if is_initialized() and not validate_unit(self.unit):
            raise ValueError(f"Unit '{self.unit}' is not a recognized unit")

    @property
    def inventory_category(self):
        """Return the associated InventoryCategory or None."""
        if self.inventory_category_id is None:
            return None
        from dinner_spinner.domain.inventory_category import (
            InventoryCategory as DC)
        # In a fully wired app the repo would fetch this; keep it simple.
        return None

    def __eq__(self, other):
        if not isinstance(other, Ingredient):
            return NotImplemented
        return (self.id == other.id and self.name == other.name
                and self.inventory_category_id == other.inventory_category_id
                and self.quantity == other.quantity
                and self.unit == other.unit)

    def __repr__(self):
        cat = self.inventory_category_id if self.inventory_category_id is not None else "None"
        return (f"<Ingredient id={self.id} name={self.name!r}"
                f" qty={self.quantity} {self.unit} cat={cat}>")

    def __hash__(self):
        return hash((self.id, self.name, self.inventory_category_id,
                     self.quantity, self.unit))

    def increase_quantity(self, quantity: float, unit: str) -> None:
        """Increase the ingredient's quantity by the given amount in the specified unit.

        The quantity is converted to the ingredient's current unit using the UnitSystem
        before being added to the current quantity.

        Args:
            quantity: The amount to add (must be > 0)
            unit: The unit of the quantity to add

        Raises:
            ValueError: If quantity <= 0, unit invalid, or unit incompatible
            RuntimeError: If UnitSystem not initialized
        """
        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero")
        if not unit or not unit.strip():
            raise ValueError("Unit is required")
        unit = unit.strip()

        if not is_initialized():
            raise RuntimeError("UnitSystem not initialized; call initialize() first")

        if not validate_unit(unit):
            raise ValueError(f"Unit '{unit}' is not a recognized unit")

        # Check category compatibility
        from_cat = category_of(unit)
        to_cat = category_of(self.unit)
        if from_cat != to_cat:
            raise ValueError(
                f"Cannot convert '{unit}' to '{self.unit}': "
                "different measurement categories (requires density information)"
            )

        # Convert the incoming quantity to the ingredient's unit
        converted_qty = convert(quantity, unit, self.unit)
        self.quantity += converted_qty

    def decrease_quantity(self, quantity: float, unit: str) -> None:
        """Decrease the ingredient's quantity by the given amount in the specified unit.

        The quantity is converted to the ingredient's current unit using the UnitSystem
        before being subtracted from the current quantity.

        Args:
            quantity: The amount to subtract (must be > 0)
            unit: The unit of the quantity to subtract

        Raises:
            ValueError: If quantity <= 0, unit invalid, unit incompatible,
                       or resulting quantity would be negative
            RuntimeError: If UnitSystem not initialized
        """
        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero")
        if not unit or not unit.strip():
            raise ValueError("Unit is required")
        unit = unit.strip()

        if not is_initialized():
            raise RuntimeError("UnitSystem not initialized; call initialize() first")

        if not validate_unit(unit):
            raise ValueError(f"Unit '{unit}' is not a recognized unit")

        # Check category compatibility
        from_cat = category_of(unit)
        to_cat = category_of(self.unit)
        if from_cat != to_cat:
            raise ValueError(
                f"Cannot convert '{unit}' to '{self.unit}': "
                "different measurement categories (requires density information)"
            )

        # Convert the incoming quantity to the ingredient's unit
        converted_qty = convert(quantity, unit, self.unit)

        if converted_qty > self.quantity:
            raise ValueError(
                f"Cannot decrease by {quantity} {unit} (={converted_qty} {self.unit}): "
                f"would result in negative inventory (current: {self.quantity} {self.unit})"
            )

        self.quantity -= converted_qty

    def change_unit(self, target_unit: str) -> None:
        """Change the unit of this ingredient, preserving the physical quantity.

        Uses the centralized UnitSystem for conversion. Validates that the
        target unit is recognized and compatible with the current unit.
        Rejects incompatible conversions (cross-category without density).
        Leaves the ingredient unchanged if conversion fails.

        Args:
            target_unit: The new unit to convert to (e.g., "kg", "ml", "each")

        Raises:
            ValueError: If target_unit is invalid, not recognized, or incompatible
                       with current unit (different measurement category).
        """
        if not target_unit or not target_unit.strip():
            raise ValueError("Target unit is required")

        target_unit = target_unit.strip()

        if target_unit == self.unit:
            return  # no change needed

        if not is_initialized():
            raise RuntimeError("UnitSystem not initialized; call initialize() first")

        if not validate_unit(target_unit):
            raise ValueError(f"Unit '{target_unit}' is not a recognized unit")

        # Check category compatibility
        from_cat = category_of(self.unit)
        to_cat = category_of(target_unit)
        if from_cat != to_cat:
            raise ValueError(
                f"Cannot convert '{self.unit}' to '{target_unit}': "
                "different measurement categories (requires density information)"
            )

        # Perform conversion: new_quantity = old_quantity * conversion_factor
        new_quantity = convert(self.quantity, self.unit, target_unit)

        # Update in place - preserve represented physical quantity
        self.quantity = new_quantity
        self.unit = target_unit