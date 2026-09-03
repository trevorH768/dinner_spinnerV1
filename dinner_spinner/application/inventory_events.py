"""Application services for inventory event orchestration.

This module provides the application-layer functions that coordinate
domain operations for recording inventory events (Acquisition, Consumption, Waste).
Each function performs a complete atomic transaction: validate, convert units,
update Ingredient quantity, and persist the event.
"""

from decimal import Decimal
from typing import Optional
from datetime import datetime
from sqlalchemy.exc import IntegrityError

from dinner_spinner.domain.ingredient import Ingredient as DIIngredient
from dinner_spinner.domain.acquisition import Acquisition as DIAcquisition
from dinner_spinner.domain.consumption import Consumption as DIConsumption
from dinner_spinner.domain.waste import Waste as DIWaste
from dinner_spinner.domain.unit_system import validate_unit, is_initialized, convert, category_of


class InventoryEventError(Exception):
    """Base exception for inventory event errors."""
    pass


class InvalidQuantityError(InventoryEventError):
    """Raised when quantity is invalid."""
    pass


class InvalidUnitError(InventoryEventError):
    """Raised when unit is invalid or incompatible."""
    pass


class InsufficientInventoryError(InventoryEventError):
    """Raised when consumption/waste would make inventory negative."""
    pass


class IngredientNotFoundError(InventoryEventError):
    """Raised when ingredient is not found."""
    pass


class UnitSystemNotInitializedError(InventoryEventError):
    """Raised when UnitSystem is not initialized."""
    pass


def _validate_and_convert_quantity(ingredient: DIIngredient, quantity: float, unit: str) -> float:
    """Validate and convert quantity to ingredient's unit.

    Args:
        ingredient: The ingredient to convert for
        quantity: The quantity to convert
        unit: The unit of the quantity

    Returns:
        The converted quantity in the ingredient's unit

    Raises:
        InvalidQuantityError: If quantity <= 0
        InvalidUnitError: If unit is invalid or incompatible
        UnitSystemNotInitializedError: If UnitSystem not initialized
    """
    if quantity <= 0:
        raise InvalidQuantityError("Quantity must be greater than zero")

    if not unit or not unit.strip():
        raise InvalidUnitError("Unit is required")

    unit = unit.strip()

    if not is_initialized():
        raise UnitSystemNotInitializedError("UnitSystem not initialized; call initialize() first")

    if not validate_unit(unit):
        raise InvalidUnitError(f"Unit '{unit}' is not a recognized unit")

    # Check category compatibility
    from_cat = category_of(unit)
    to_cat = category_of(ingredient.unit)
    if from_cat != to_cat:
        raise InvalidUnitError(
            f"Cannot convert '{unit}' to '{ingredient.unit}': "
            "different measurement categories (requires density information)"
        )

    # Convert the incoming quantity to the ingredient's unit
    return convert(quantity, unit, ingredient.unit)


def record_acquisition(
    db_session,
    ingredient_id: int,
    quantity: float,
    unit: str,
    cost: float = 0.0,
    acquired_at: Optional[datetime] = None
) -> tuple:
    """Record an acquisition event and update ingredient quantity atomically.

    This function performs a complete atomic transaction:
    1. Validate input
    2. Load the ingredient
    3. Validate/convert the requested quantity through UnitSystem
    4. Increase ingredient quantity
    3. Create and persist the Acquisition event
    4. Commit the transaction

    Args:
        db_session: SQLAlchemy database session
        ingredient_id: ID of the ingredient
        quantity: Quantity acquired (must be > 0)
        unit: Unit of the quantity
        cost: Cost of the acquisition (default 0, must be >= 0)
        acquired_at: Timestamp of acquisition (default: now)

    Returns:
        Tuple of (persistence Acquisition model, domain Acquisition object)

    Raises:
        IngredientNotFoundError: If ingredient not found
        InvalidQuantityError: If quantity <= 0
        InvalidUnitError: If unit invalid or incompatible
        UnitSystemNotInitializedError: If UnitSystem not initialized
        InventoryEventError: If cost < 0
    """
    from dinner_persistence.models import Acquisition, Ingredient
    from dinner_spinner.domain.acquisition import Acquisition as DIAcquisition
    from decimal import Decimal

    if cost < 0:
        raise InventoryEventError("Acquisition cost cannot be negative")

    # Load the ingredient
    ingredient = db_session.get(Ingredient, ingredient_id)
    if not ingredient:
        raise IngredientNotFoundError(f"Ingredient with id {ingredient_id} not found")

    # Validate and convert quantity
    converted_qty = _validate_and_convert_quantity(ingredient.to_domain(), quantity, unit)

    # Create domain ingredient and apply increase
    domain_ingredient = ingredient.to_domain()
    domain_ingredient.increase_quantity(quantity, unit)

    # Create domain acquisition event
    domain_acq = DIAcquisition(
        id=0,  # Will be set by DB
        ingredient_id=ingredient_id,
        quantity=quantity,
        unit=unit.strip(),
        cost=Decimal(str(cost)),
        acquired_at=acquired_at or datetime.utcnow()
    )

    try:
        # Sync domain changes back to persistence model
        ingredient.quantity = domain_ingredient.quantity
        ingredient.unit = domain_ingredient.unit

        # Create persistence acquisition
        acq = Acquisition(
            ingredient_id=ingredient_id,
            quantity=quantity,
            unit=unit.strip(),
            cost=cost,
            acquired_at=acquired_at or datetime.utcnow()
        )
        db_session.add(acq)
        db_session.flush()  # Get the ID

        # Update domain object with generated ID
        domain_acq.id = acq.id

        db_session.commit()

        return acq, domain_acq

    except Exception:
        db_session.rollback()
        raise


def record_consumption(
    db_session,
    ingredient_id: int,
    quantity: float,
    unit: str,
    consumed_at: Optional[datetime] = None
) -> tuple:
    """Record a consumption event and update ingredient quantity atomically.

    Args:
        db_session: SQLAlchemy database session
        ingredient_id: ID of the ingredient
        quantity: Quantity consumed (must be > 0)
        unit: Unit of the quantity
        consumed_at: Timestamp of consumption (default: now)

    Returns:
        Tuple of (persistence Consumption model, domain Consumption object)

    Raises:
        IngredientNotFoundError: If ingredient not found
        InvalidQuantityError: If quantity <= 0
        InvalidUnitError: If unit invalid or incompatible
        InsufficientInventoryError: If consumption would make quantity negative
        UnitSystemNotInitializedError: If UnitSystem not initialized
    """
    from dinner_persistence.models import Consumption, Ingredient
    from dinner_spinner.domain.consumption import Consumption as DIConsumption

    # Load the ingredient
    ingredient = db_session.get(Ingredient, ingredient_id)
    if not ingredient:
        raise IngredientNotFoundError(f"Ingredient with id {ingredient_id} not found")

    # Validate and convert quantity
    converted_qty = _validate_and_convert_quantity(ingredient.to_domain(), quantity, unit)

    # Check sufficient inventory
    domain_ingredient = ingredient.to_domain()
    if converted_qty > domain_ingredient.quantity:
        raise InsufficientInventoryError(
            f"Cannot consume {quantity} {unit} (={converted_qty} {domain_ingredient.unit}): "
            f"would result in negative inventory (current: {domain_ingredient.quantity} {domain_ingredient.unit})"
        )

    # Apply decrease
    domain_ingredient.decrease_quantity(quantity, unit)

    # Create domain consumption event
    domain_con = DIConsumption(
        id=0,
        ingredient_id=ingredient_id,
        quantity=quantity,
        unit=unit.strip(),
        consumed_at=consumed_at or datetime.utcnow()
    )

    try:
        # Sync domain changes back to persistence model
        ingredient.quantity = domain_ingredient.quantity
        ingredient.unit = domain_ingredient.unit

        # Create persistence consumption
        con = Consumption(
            ingredient_id=ingredient_id,
            quantity=quantity,
            unit=unit.strip(),
            consumed_at=consumed_at or datetime.utcnow()
        )
        db_session.add(con)
        db_session.flush()

        domain_con.id = con.id

        db_session.commit()

        return con, domain_con

    except Exception:
        db_session.rollback()
        raise


def record_waste(
    db_session,
    ingredient_id: int,
    quantity: float,
    unit: str,
    wasted_at: Optional[datetime] = None
) -> tuple:
    """Record a waste event and update ingredient quantity atomically.

    Args:
        db_session: SQLAlchemy database session
        ingredient_id: ID of the ingredient
        quantity: Quantity wasted (must be > 0)
        unit: Unit of the quantity
        wasted_at: Timestamp of waste (default: now)

    Returns:
        Tuple of (persistence Waste model, domain Waste object)

    Raises:
        IngredientNotFoundError: If ingredient not found
        InvalidQuantityError: If quantity <= 0
        InvalidUnitError: If unit invalid or incompatible
        InsufficientInventoryError: If waste would make quantity negative
        UnitSystemNotInitializedError: If UnitSystem not initialized
    """
    from dinner_persistence.models import Waste, Ingredient
    from dinner_spinner.domain.waste import Waste as DIWaste

    # Load the ingredient
    ingredient = db_session.get(Ingredient, ingredient_id)
    if not ingredient:
        raise IngredientNotFoundError(f"Ingredient with id {ingredient_id} not found")

    # Validate and convert quantity
    converted_qty = _validate_and_convert_quantity(ingredient.to_domain(), quantity, unit)

    # Check sufficient inventory
    domain_ingredient = ingredient.to_domain()
    if converted_qty > domain_ingredient.quantity:
        raise InsufficientInventoryError(
            f"Cannot waste {quantity} {unit} (={converted_qty} {domain_ingredient.unit}): "
            f"would result in negative inventory (current: {domain_ingredient.quantity} {domain_ingredient.unit})"
        )

    # Apply decrease
    domain_ingredient.decrease_quantity(quantity, unit)

    # Create domain waste event
    domain_was = DIWaste(
        id=0,
        ingredient_id=ingredient_id,
        quantity=quantity,
        unit=unit.strip(),
        wasted_at=wasted_at or datetime.utcnow()
    )

    try:
        # Sync domain changes back to persistence model
        ingredient.quantity = domain_ingredient.quantity
        ingredient.unit = domain_ingredient.unit

        # Create persistence waste
        was = Waste(
            ingredient_id=ingredient_id,
            quantity=quantity,
            unit=unit.strip(),
            wasted_at=wasted_at or datetime.utcnow()
        )
        db_session.add(was)
        db_session.flush()

        domain_was.id = was.id

        db_session.commit()

        return was, domain_was

    except Exception:
        db_session.rollback()
        raise


def get_ingredient_history(db_session, ingredient_id: int) -> dict:
    """Get complete event history for an ingredient.

    Args:
        db_session: SQLAlchemy database session
        ingredient_id: ID of the ingredient

    Returns:
        Dictionary with 'acquisitions', 'consumptions', 'wastes' lists
    """
    from dinner_persistence.models import Acquisition, Consumption, Waste

    acquisitions = db_session.query(Acquisition).filter(
        Acquisition.ingredient_id == ingredient_id
    ).order_by(Acquisition.acquired_at.desc()).all()

    consumptions = db_session.query(Consumption).filter(
        Consumption.ingredient_id == ingredient_id
    ).order_by(Consumption.consumed_at.desc()).all()

    wastes = db_session.query(Waste).filter(
        Waste.ingredient_id == ingredient_id
    ).order_by(Waste.wasted_at.desc()).all()

    return {
        'acquisitions': [a.to_domain() for a in acquisitions],
        'consumptions': [c.to_domain() for c in consumptions],
        'wastes': [w.to_domain() for w in wastes],
    }


def get_global_event_history(db_session, limit: int = 100) -> dict:
    """Get global event history across all ingredients.

    Args:
        db_session: SQLAlchemy database session
        limit: Maximum number of events per type to return

    Returns:
        Dictionary with 'acquisitions', 'consumptions', 'wastes' lists
    """
    from dinner_persistence.models import Acquisition, Consumption, Waste

    acquisitions = db_session.query(Acquisition).order_by(
        Acquisition.acquired_at.desc()
    ).limit(limit).all()

    consumptions = db_session.query(Consumption).order_by(
        Consumption.consumed_at.desc()
    ).limit(limit).all()

    wastes = db_session.query(Waste).order_by(
        Waste.wasted_at.desc()
    ).limit(limit).all()

    return {
        'acquisitions': [a.to_domain() for a in acquisitions],
        'consumptions': [c.to_domain() for c in consumptions],
        'wastes': [w.to_domain() for w in wastes],
    }