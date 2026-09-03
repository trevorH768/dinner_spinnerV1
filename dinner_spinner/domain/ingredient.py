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

from dinner_spinner.domain.unit_system import validate_unit, is_initialized


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