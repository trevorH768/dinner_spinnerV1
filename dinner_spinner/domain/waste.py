"""Waste: A historical record of an Ingredient lost without being consumed."""

from datetime import datetime
from dinner_spinner.domain.unit_system import validate_unit, is_initialized


class Waste:
    """A historical record of an event in which a quantity of an Ingredient
    leaves household inventory without being consumed, reducing the current quantity.

    Waste is a historical fact. Once recorded, it is immutable in V1.
    It cannot be edited or deleted. Errors are corrected with compensating events.
    """

    def __init__(self, id: int, ingredient_id: int, quantity: float, unit: str,
                 wasted_at: datetime | None = None):
        if quantity <= 0:
            raise ValueError("Waste quantity must be greater than zero")
        if not unit or not unit.strip():
            raise ValueError("Waste unit is required")

        self.id = id
        self.ingredient_id = ingredient_id
        self.quantity = quantity
        self.unit = unit.strip()
        self.wasted_at = wasted_at or datetime.utcnow()

        if is_initialized() and not validate_unit(self.unit):
            raise ValueError(f"Unit '{self.unit}' is not a recognized unit")

    def __eq__(self, other):
        if not isinstance(other, Waste):
            return NotImplemented
        return (self.id == other.id and self.ingredient_id == other.ingredient_id
                and self.quantity == other.quantity and self.unit == other.unit
                and self.wasted_at == other.wasted_at)

    def __repr__(self):
        return (f"<Waste id={self.id} ingredient_id={self.ingredient_id}"
                f" qty={self.quantity} {self.unit} at={self.wasted_at}>")

    def __hash__(self):
        return hash((self.id, self.ingredient_id, self.quantity, self.unit,
                     self.wasted_at))