"""Centralized unit/conversion system for Dinner Spinner V1.

This is the single authoritative location for unit definitions and conversion
logic. All domain entities reference this module for unit validation and
conversion. There must not be multiple competing conversion systems.

V1 recognizes these unit categories:

  MASS    g, kg, oz, lb
  VOLUME  ml, l, cup, tbsp, tsp
  COUNT   each, piece, pieces, count

Same-category conversions are directly supported. Cross-category conversions
(e.g. mass → volume) are rejected because they require density information
that V1 does not invent.

The stored Ingredient.quantity must NOT be silently normalized into a
universal base unit. The conversion system exists to perform valid
calculations between compatible units.
"""

from decimal import Decimal
from typing import Union

#: Canonical unit definitions keyed by category name.
#: Each inner dict maps a canonical unit name to its relative value
#: with respect to a base unit within its category.
_UNIT_DEFS: dict[str, dict[str, Decimal]] = {}

#: Canonical unit names keyed by category name.
_UNIT_NAMES: dict[str, list[str]] = {}

#: Mapping from lowercased unit name → category.
_UNIT_TO_CAT: dict[str, str] = {}

#: Mapping from lowercased unit name → relative value (base = 1.0).
_UNIT_TO_VALUE: dict[str, Decimal] = {}

_IS_INITIALIZED = False


def is_initialized() -> bool:
    return _IS_INITIALIZED


def initialize() -> None:
    """Populate the unit definitions. Call once during app initialization."""
    global _UNIT_DEFS, _UNIT_NAMES, _UNIT_TO_CAT, _UNIT_TO_VALUE, _IS_INITIALIZED

    # --- Mass ---
    mass: dict[str, Decimal] = {
        "g": Decimal("1.0"),
        "kg": Decimal("1000.0"),
        "oz": Decimal("28.3495"),
        "lb": Decimal("453.592"),
    }
    # --- Volume ---
    volume: dict[str, Decimal] = {
        "ml": Decimal("1.0"),
        "l": Decimal("1000.0"),
        "cup": Decimal("236.588"),
        "tbsp": Decimal("15.0"),
        "tsp": Decimal("5.0"),
    }
    # --- Count ---
    count: dict[str, Decimal] = {
        "each": Decimal("1.0"),
        "piece": Decimal("1.0"),
        "pieces": Decimal("1.0"),
        "count": Decimal("1.0"),
    }

    _UNIT_DEFS = {
        "MASS": mass,
        "VOLUME": volume,
        "COUNT": count,
    }

    _UNIT_NAMES = {
        "MASS": list(mass.keys()),
        "VOLUME": list(volume.keys()),
        "COUNT": list(count.keys()),
    }

    _UNIT_TO_CAT = {
        unit.lower(): cat
        for cat, units in _UNIT_NAMES.items()
        for unit in units
    }
    _UNIT_TO_VALUE = {}
    for cat, units in _UNIT_NAMES.items():
        for unit in units:
            _UNIT_TO_VALUE[unit.lower()] = _UNIT_DEFS[cat][unit]

    _IS_INITIALIZED = True


def is_initialized() -> bool:
    return _IS_INITIALIZED


def validate_unit(unit: str) -> bool:
    """Return True if *unit* is a recognized canonical unit."""
    if not _IS_INITIALIZED:
        raise RuntimeError("UnitSystem not initialized; call initialize() first")
    return unit.strip().lower() in _UNIT_TO_VALUE


def convert(value: Decimal, from_unit: str, to_unit: str) -> Decimal:
    """Convert *value* from *from_unit* to *to_unit*.

    Only same-category conversions are supported.
    Cross-category conversions raise ValueError.
    Invalid units raise ValueError.
    """
    if not _IS_INITIALIZED:
        raise RuntimeError("Unit system not initialized; cannot convert")

    from_key = from_unit.strip().lower()
    to_key = to_unit.strip().lower()

    if from_key == to_key:
        return value

    if from_key not in _UNIT_TO_VALUE or to_key not in _UNIT_TO_VALUE:
        raise ValueError(f"Unrecognized unit in conversion")

    from_cat = _UNIT_TO_CAT[from_key]
    to_cat = _UNIT_TO_CAT[to_key]

    if from_cat != to_cat:
        raise ValueError(
            f"Cannot convert between '{from_unit}' and '{to_unit}'"
            " (different measurement categories)"
        )

    from_value = _UNIT_TO_VALUE[from_key]
    to_value = _UNIT_TO_VALUE[to_key]

    # Convert to base then to target
    result = value * from_value / to_value
    return result


def get_units_by_category(category: str) -> list[str]:
    """Return all canonical units for *category* (MASS, VOLUME, COUNT)."""
    if not _IS_INITIALIZED:
        return []
    return _UNIT_NAMES.get(category, [])


def category_of(unit: str) -> str | None:
    """Return the category name (MASS, VOLUME, COUNT) for *unit*, or None."""
    if not _IS_INITIALIZED:
        return None
    return _UNIT_TO_CAT.get(unit.strip().lower())


def reset() -> None:
    """Reset the unit system to uninitialized state. For testing only."""
    global _UNIT_DEFS, _UNIT_NAMES, _UNIT_TO_CAT, _UNIT_TO_VALUE, _IS_INITIALIZED
    _UNIT_DEFS = {}
    _UNIT_NAMES = {}
    _UNIT_TO_CAT = {}
    _UNIT_TO_VALUE = {}
    _IS_INITIALIZED = False