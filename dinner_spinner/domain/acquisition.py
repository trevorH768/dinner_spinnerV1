"""Acquisition: A historical record of obtaining an Ingredient."""

from datetime import datetime
from decimal import Decimal
from dinner_spinner.domain.unit_system import validate_unit, is_initialized


class Acquisition:
    """A historical record of an event in which the household obtains a positive
    quantity of an Ingredient, optionally recording the actual amount paid.

    Acquisition is a historical fact. Once recorded, it is immutable in V1.
    It cannot be edited or deleted. Errors are corrected with compensating events.
    """

    def __init__(self, id: int, ingredient_id: int, quantity: float, unit: str,
                 cost: Decimal | float, acquired_at: datetime | None = None):
        if quantity <= 0:
            raise ValueError("Acquisition quantity must be greater than zero")
        if cost < 0:
            raise ValueError("Acquisition cost cannot be negative")
        if not unit or not unit.strip():
            raise ValueError("Acquisition unit is required")

        self.id = id
        self.ingredient_id = ingredient_id
        self.quantity = quantity
        self.unit = unit.strip()
        self.cost = Decimal(str(cost))
        self.acquired_at = acquired_at or datetime.utcnow()

        if is_initialized() and not validate_unit(self.unit):
            raise ValueError(f"Unit '{self.unit}' is not a recognized unit")

    def __eq__(self, other):
        if not isinstance(other, Acquisition):
            return NotImplemented
        return (self.id == other.id and self.ingredient_id == other.ingredient_id
                and self.quantity == other.quantity and self.unit == other.unit
                and self.cost == other.cost and self.acquired_at == other.acquired_at)

    def __repr__(self):
        return (f"<Acquisition id={self.id} ingredient_id={self.ingredient_id}"
                f" qty={self.quantity} {self.unit} cost={self.cost} at={self.acquired_at}>")

    def __hash__(self):
        return hash((self.id, self.ingredient_id, self.quantity, self.unit,
                     self.cost, self.acquired_at))