"""Consumption: A historical record of using an Ingredient."""

from datetime import datetime
from dinner_spinner.domain.unit_system import validate_unit, is_initialized


class Consumption:
    """A historical record of an event in which the household uses a positive
    quantity of an Ingredient, reducing the current quantity.

    Consumption is a historical fact. Once recorded, it is immutable in V1.
    It cannot be edited or deleted. Errors are corrected with compensating events.
    """

    def __init__(self, id: int, ingredient_id: int, quantity: float, unit: str,
                 consumed_at: datetime | None = None):
        if quantity <= 0:
            raise ValueError("Consumption quantity must be greater than zero")
        if not unit or not unit.strip():
            raise ValueError("Consumption unit is required")

        self.id = id
        self.ingredient_id = ingredient_id
        self.quantity = quantity
        self.unit = unit.strip()
        self.consumed_at = consumed_at or datetime.utcnow()

        if is_initialized() and not validate_unit(self.unit):
            raise ValueError(f"Unit '{self.unit}' is not a recognized unit")

    def __eq__(self, other):
        if not isinstance(other, Consumption):
            return NotImplemented
        return (self.id == other.id and self.ingredient_id == other.ingredient_id
                and self.quantity == other.quantity and self.unit == other.unit
                and self.consumed_at == other.consumed_at)

    def __repr__(self):
        return (f"<Consumption id={self.id} ingredient_id={self.ingredient_id}"
                f" qty={self.quantity} {self.unit} at={self.consumed_at}>")

    def __hash__(self):
        return hash((self.id, self.ingredient_id, self.quantity, self.unit,
                     self.consumed_at))