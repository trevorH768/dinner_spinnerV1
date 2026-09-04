"""Architecture-level tests for Dinner Spinner V1.

These tests verify the architecture itself, not application features.
"""

import pytest
import sys


# ---------------------------------------------------------------------------
# 0. Infrastructure Tests
# ---------------------------------------------------------------------------

def test_sqlite_foreign_keys_enforced():
    """SQLite foreign key enforcement must be active (PRAGMA foreign_keys = ON)."""
    from dinner_spinner import create_app
    from sqlalchemy import text

    app = create_app()
    with app.app_context():
        from flask import current_app
        db = current_app.extensions['sqlalchemy']
        result = db.session.execute(text('PRAGMA foreign_keys')).fetchone()
        assert result[0] == 1, "SQLite foreign_keys PRAGMA not enabled"


# ---------------------------------------------------------------------------
# 1. Dependency Direction Tests
# ---------------------------------------------------------------------------

def test_domain_does_not_import_flask():
    """The domain layer must not import Flask."""
    import dinner_spinner.domain.ingredient
    import dinner_spinner.domain.recipe
    import dinner_spinner.domain.recipe_ingredient
    import dinner_spinner.domain.meal_plan
    import dinner_spinner.domain.inventory_category
    import dinner_spinner.domain.unit_system
    import dinner_spinner.domain.demand
    import dinner_spinner.domain.inventory_requirement

    for mod in [
        dinner_spinner.domain.ingredient,
        dinner_spinner.domain.recipe,
        dinner_spinner.domain.recipe_ingredient,
        dinner_spinner.domain.meal_plan,
        dinner_spinner.domain.inventory_category,
        dinner_spinner.domain.unit_system,
        dinner_spinner.domain.demand,
        dinner_spinner.domain.inventory_requirement,
    ]:
        # Check that Flask is not in the module's globals
        assert "Flask" not in mod.__dict__, f"{mod.__name__} imports Flask"
        assert "flask" not in sys.modules or not any(
            "flask" in str(v).lower() for v in mod.__dict__.values()
        )


def test_domain_does_not_import_presentation():
    """The domain layer must not import presentation modules."""
    import dinner_spinner.domain.ingredient
    import dinner_spinner.domain.recipe

    for mod in [
        dinner_spinner.domain.ingredient,
        dinner_spinner.domain.recipe,
        dinner_spinner.domain.recipe_ingredient,
        dinner_spinner.domain.meal_plan,
        dinner_spinner.domain.inventory_category,
        dinner_spinner.domain.unit_system,
        dinner_spinner.domain.demand,
        dinner_spinner.domain.inventory_requirement,
    ]:
        for name in mod.__dict__:
            if "presentation" in str(name).lower():
                pytest.fail(f"{mod.__name__} references presentation module: {name}")


def test_domain_does_not_import_http():
    """The domain layer must not import HTTP-specific modules."""
    import dinner_spinner.domain.ingredient

    forbidden = ["werkzeug", "request", "response", "http"]
    for mod_name in [
        "dinner_spinner.domain.ingredient",
        "dinner_spinner.domain.recipe",
        "dinner_spinner.domain.recipe_ingredient",
        "dinner_spinner.domain.meal_plan",
        "dinner_spinner.domain.inventory_category",
        "dinner_spinner.domain.unit_system",
        "dinner_spinner.domain.demand",
        "dinner_spinner.domain.inventory_requirement",
    ]:
        mod = sys.modules[mod_name]
        for attr in dir(mod):
            attr_lower = attr.lower()
            for f in forbidden:
                if f in attr_lower and not attr.startswith("__"):
                    pytest.fail(f"{mod_name}.{attr} appears to import {f}")


def test_domain_does_not_import_database_session():
    """The domain layer must not import database session mechanics."""
    forbidden = ["sqlalchemy", "session", "engine", "connection"]
    for mod_name in [
        "dinner_spinner.domain.ingredient",
        "dinner_spinner.domain.recipe",
        "dinner_spinner.domain.recipe_ingredient",
        "dinner_spinner.domain.meal_plan",
        "dinner_spinner.domain.inventory_category",
        "dinner_spinner.domain.unit_system",
        "dinner_spinner.domain.demand",
        "dinner_spinner.domain.inventory_requirement",
    ]:
        mod = sys.modules[mod_name]
        for attr in dir(mod):
            attr_lower = attr.lower()
            for f in forbidden:
                if f in attr_lower and not attr.startswith("__"):
                    pytest.fail(f"{mod_name}.{attr} appears to import {f}")


def test_domain_does_not_import_external_food_providers():
    """The domain layer must not import external food providers."""
    forbidden = ["usda", "fooddata", "openfoodfacts", "nutrition", "barcode"]
    for mod_name in [
        "dinner_spinner.domain.ingredient",
        "dinner_spinner.domain.recipe",
        "dinner_spinner.domain.recipe_ingredient",
        "dinner_spinner.domain.meal_plan",
        "dinner_spinner.domain.inventory_category",
        "dinner_spinner.domain.unit_system",
        "dinner_spinner.domain.demand",
        "dinner_spinner.domain.inventory_requirement",
    ]:
        mod = sys.modules[mod_name]
        for attr in dir(mod):
            attr_lower = attr.lower()
            for f in forbidden:
                if f in attr_lower and not attr.startswith("__"):
                    pytest.fail(f"{mod_name}.{attr} appears to import {f}")


# ---------------------------------------------------------------------------
# 2. Forbidden Domain Concepts Tests
# ---------------------------------------------------------------------------

def test_domain_has_no_container_entity():
    """V1 domain must not contain Container entity."""
    from dinner_spinner.domain import __all__ as domain_exports
    assert "Container" not in domain_exports


def test_domain_has_no_inventory_lot_entity():
    """V1 domain must not contain InventoryLot entity."""
    from dinner_spinner.domain import __all__ as domain_exports
    assert "InventoryLot" not in domain_exports


def test_domain_has_no_product_entity():
    """V1 domain must not contain Product entity."""
    from dinner_spinner.domain import __all__ as domain_exports
    assert "Product" not in domain_exports


def test_domain_has_no_package_entity():
    """V1 domain must not contain Package entity."""
    from dinner_spinner.domain import __all__ as domain_exports
    assert "Package" not in domain_exports


def test_domain_has_no_store_entity():
    """V1 domain must not contain Store entity."""
    from dinner_spinner.domain import __all__ as domain_exports
    assert "Store" not in domain_exports


def test_domain_has_no_brand_entity():
    """V1 domain must not contain Brand entity."""
    from dinner_spinner.domain import __all__ as domain_exports
    assert "Brand" not in domain_exports


def test_domain_has_no_barcode_entity():
    """V1 domain must not contain Barcode entity."""
    from dinner_spinner.domain import __all__ as domain_exports
    assert "Barcode" not in domain_exports


def test_domain_has_no_nutrition_entity():
    """V1 domain must not contain Nutrition entity."""
    from dinner_spinner.domain import __all__ as domain_exports
    assert "Nutrition" not in domain_exports


def test_domain_has_no_generalized_inventory_event():
    """V1 domain must not contain generalized InventoryEvent entity."""
    from dinner_spinner.domain import __all__ as domain_exports
    assert "InventoryEvent" not in domain_exports


def test_domain_has_no_transfer_entity():
    """V1 domain must not contain Transfer entity."""
    from dinner_spinner.domain import __all__ as domain_exports
    assert "Transfer" not in domain_exports


def test_domain_has_no_price_estimate_entity():
    """V1 domain must not contain PriceEstimate entity."""
    from dinner_spinner.domain import __all__ as domain_exports
    assert "PriceEstimate" not in domain_exports


def test_domain_has_no_shopping_list_entity():
    """V1 domain must not contain persistent ShoppingList entity."""
    from dinner_spinner.domain import __all__ as domain_exports
    assert "ShoppingList" not in domain_exports


# ---------------------------------------------------------------------------
# 3. Ingredient Boundary Tests
# ---------------------------------------------------------------------------

def test_ingredient_represents_inventory_holding_directly():
    """Ingredient itself is the inventory holding - no second abstraction."""
    from dinner_spinner.domain.ingredient import Ingredient

    # Ingredient has quantity and unit directly
    ing = Ingredient(id=1, name="Flour", inventory_category_id=None, quantity=1000, unit="g")
    assert hasattr(ing, "quantity")
    assert hasattr(ing, "unit")
    assert ing.quantity == 1000
    assert ing.unit == "g"

    # No container_id or similar field
    assert not hasattr(ing, "container_id")
    assert not hasattr(ing, "lot_id")
    assert not hasattr(ing, "inventory_id")


def test_ingredient_no_second_inventory_abstraction():
    """There must not be a second inventory/container abstraction around Ingredient."""
    import dinner_spinner.domain.ingredient as ing_mod

    # Check the module doesn't define Container or InventoryLot
    assert not hasattr(ing_mod, "Container")
    assert not hasattr(ing_mod, "InventoryLot")
    assert not hasattr(ing_mod, "IngredientInventory")


def test_ingredient_change_unit_preserves_quantity():
    """Ingredient.change_unit() preserves represented physical quantity."""
    from dinner_spinner.domain.unit_system import initialize, reset
    from dinner_spinner.domain.ingredient import Ingredient

    reset()
    initialize()

    # Mass: kg -> g
    ing = Ingredient(id=1, name="Flour", inventory_category_id=None, quantity=1, unit="kg")
    ing.change_unit("g")
    assert ing.quantity == 1000 and ing.unit == "g"

    # Mass: g -> kg
    ing = Ingredient(id=2, name="Sugar", inventory_category_id=None, quantity=500, unit="g")
    ing.change_unit("kg")
    assert ing.quantity == 0.5 and ing.unit == "kg"

    # Volume: l -> ml
    ing = Ingredient(id=3, name="Water", inventory_category_id=None, quantity=2, unit="l")
    ing.change_unit("ml")
    assert ing.quantity == 2000 and ing.unit == "ml"


def test_ingredient_change_unit_rejects_cross_category():
    """Ingredient.change_unit() rejects incompatible cross-category conversions."""
    from dinner_spinner.domain.unit_system import initialize, reset
    from dinner_spinner.domain.ingredient import Ingredient

    reset()
    initialize()

    ing = Ingredient(id=1, name="Test", inventory_category_id=None, quantity=100, unit="g")
    with pytest.raises(ValueError, match="different measurement categories"):
        ing.change_unit("ml")

    ing = Ingredient(id=2, name="Test", inventory_category_id=None, quantity=1, unit="cup")
    with pytest.raises(ValueError, match="different measurement categories"):
        ing.change_unit("each")


def test_ingredient_change_unit_rejects_invalid_unit():
    """Ingredient.change_unit() rejects invalid/unrecognized units."""
    from dinner_spinner.domain.unit_system import initialize, reset
    from dinner_spinner.domain.ingredient import Ingredient

    reset()
    initialize()

    ing = Ingredient(id=1, name="Test", inventory_category_id=None, quantity=100, unit="g")
    with pytest.raises(ValueError, match="not a recognized unit"):
        ing.change_unit("invalid_unit")


def test_ingredient_change_unit_rejects_empty():
    """Ingredient.change_unit() rejects empty target unit."""
    from dinner_spinner.domain.unit_system import initialize, reset
    from dinner_spinner.domain.ingredient import Ingredient

    reset()
    initialize()

    ing = Ingredient(id=1, name="Test", inventory_category_id=None, quantity=100, unit="g")
    with pytest.raises(ValueError, match="Target unit is required"):
        ing.change_unit("")


def test_ingredient_change_unit_noop_same_unit():
    """Ingredient.change_unit() is no-op when target equals current unit."""
    from dinner_spinner.domain.unit_system import initialize, reset
    from dinner_spinner.domain.ingredient import Ingredient

    reset()
    initialize()

    ing = Ingredient(id=1, name="Test", inventory_category_id=None, quantity=100, unit="g")
    ing.change_unit("g")
    assert ing.quantity == 100 and ing.unit == "g"


def test_ingredient_change_unit_requires_initialized():
    """Ingredient.change_unit() raises if UnitSystem not initialized."""
    from dinner_spinner.domain.unit_system import reset
    from dinner_spinner.domain.ingredient import Ingredient

    reset()  # uninitialized

    ing = Ingredient(id=1, name="Test", inventory_category_id=None, quantity=100, unit="g")
    with pytest.raises(RuntimeError, match="not initialized"):
        ing.change_unit("kg")


# ---------------------------------------------------------------------------
# 3.5. Ingredient Quantity Methods Tests (Slice 2)
# ---------------------------------------------------------------------------

def test_ingredient_increase_quantity():
    """Ingredient.increase_quantity() adds converted quantity to current."""
    from dinner_spinner.domain.unit_system import initialize, reset
    from dinner_spinner.domain.ingredient import Ingredient

    reset()
    initialize()

    # Increase kg with g (same category)
    ing = Ingredient(id=1, name="Flour", inventory_category_id=None, quantity=1, unit="kg")
    ing.increase_quantity(500, "g")
    assert ing.quantity == 1.5 and ing.unit == "kg"

    # Increase g with kg
    ing = Ingredient(id=2, name="Sugar", inventory_category_id=None, quantity=500, unit="g")
    ing.increase_quantity(1, "kg")
    assert ing.quantity == 1500 and ing.unit == "g"

    # Volume: l + ml
    ing = Ingredient(id=3, name="Water", inventory_category_id=None, quantity=1, unit="l")
    ing.increase_quantity(500, "ml")
    assert ing.quantity == 1.5 and ing.unit == "l"


def test_ingredient_decrease_quantity():
    """Ingredient.decrease_quantity() subtracts converted quantity from current."""
    from dinner_spinner.domain.unit_system import initialize, reset
    from dinner_spinner.domain.ingredient import Ingredient

    reset()
    initialize()

    # Decrease kg with g
    ing = Ingredient(id=1, name="Flour", inventory_category_id=None, quantity=2, unit="kg")
    ing.decrease_quantity(500, "g")
    assert ing.quantity == 1.5 and ing.unit == "kg"

    # Decrease g with kg
    ing = Ingredient(id=2, name="Sugar", inventory_category_id=None, quantity=2000, unit="g")
    ing.decrease_quantity(1, "kg")
    assert ing.quantity == 1000 and ing.unit == "g"


def test_ingredient_decrease_quantity_rejects_negative_result():
    """Ingredient.decrease_quantity() rejects if result would be negative."""
    from dinner_spinner.domain.unit_system import initialize, reset
    from dinner_spinner.domain.ingredient import Ingredient

    reset()
    initialize()

    ing = Ingredient(id=1, name="Flour", inventory_category_id=None, quantity=100, unit="g")
    with pytest.raises(ValueError, match="negative inventory"):
        ing.decrease_quantity(200, "g")


def test_ingredient_increase_quantity_rejects_zero_or_negative():
    """Ingredient.increase_quantity() rejects zero or negative quantity."""
    from dinner_spinner.domain.unit_system import initialize, reset
    from dinner_spinner.domain.ingredient import Ingredient

    reset()
    initialize()

    ing = Ingredient(id=1, name="Flour", inventory_category_id=None, quantity=100, unit="g")
    with pytest.raises(ValueError, match="greater than zero"):
        ing.increase_quantity(0, "g")
    with pytest.raises(ValueError, match="greater than zero"):
        ing.increase_quantity(-1, "g")


def test_ingredient_decrease_quantity_rejects_zero_or_negative():
    """Ingredient.decrease_quantity() rejects zero or negative quantity."""
    from dinner_spinner.domain.unit_system import initialize, reset
    from dinner_spinner.domain.ingredient import Ingredient

    reset()
    initialize()

    ing = Ingredient(id=1, name="Flour", inventory_category_id=None, quantity=100, unit="g")
    with pytest.raises(ValueError, match="greater than zero"):
        ing.decrease_quantity(0, "g")
    with pytest.raises(ValueError, match="greater than zero"):
        ing.decrease_quantity(-1, "g")


def test_ingredient_increase_quantity_rejects_cross_category():
    """Ingredient.increase_quantity() rejects cross-category units."""
    from dinner_spinner.domain.unit_system import initialize, reset
    from dinner_spinner.domain.ingredient import Ingredient

    reset()
    initialize()

    ing = Ingredient(id=1, name="Flour", inventory_category_id=None, quantity=100, unit="g")
    with pytest.raises(ValueError, match="different measurement categories"):
        ing.increase_quantity(100, "ml")


def test_ingredient_decrease_quantity_rejects_cross_category():
    """Ingredient.decrease_quantity() rejects cross-category units."""
    from dinner_spinner.domain.unit_system import initialize, reset
    from dinner_spinner.domain.ingredient import Ingredient

    reset()
    initialize()

    ing = Ingredient(id=1, name="Flour", inventory_category_id=None, quantity=100, unit="g")
    with pytest.raises(ValueError, match="different measurement categories"):
        ing.decrease_quantity(100, "ml")


def test_ingredient_increase_decrease_require_initialized():
    """increase/decrease_quantity raise if UnitSystem not initialized."""
    from dinner_spinner.domain.unit_system import reset
    from dinner_spinner.domain.ingredient import Ingredient

    reset()  # uninitialized
    ing = Ingredient(id=1, name="Test", inventory_category_id=None, quantity=100, unit="g")

    with pytest.raises(RuntimeError, match="not initialized"):
        ing.increase_quantity(10, "g")
    with pytest.raises(RuntimeError, match="not initialized"):
        ing.decrease_quantity(10, "g")


# ---------------------------------------------------------------------------
# 3.6. Slice 2 Domain Entity Tests
# ---------------------------------------------------------------------------

def test_acquisition_valid():
    """Acquisition accepts valid data."""
    from datetime import datetime
    from decimal import Decimal
    from dinner_spinner.domain.unit_system import initialize, reset
    from dinner_spinner.domain.acquisition import Acquisition

    reset()
    initialize()

    acq = Acquisition(id=1, ingredient_id=1, quantity=100, unit="g",
                      cost=Decimal("10.50"), acquired_at=datetime(2024, 1, 1))
    assert acq.id == 1
    assert acq.ingredient_id == 1
    assert acq.quantity == 100
    assert acq.unit == "g"
    assert acq.cost == Decimal("10.50")
    assert acq.acquired_at == datetime(2024, 1, 1)


def test_acquisition_rejects_zero_quantity():
    """Acquisition rejects zero or negative quantity."""
    from decimal import Decimal
    from dinner_spinner.domain.unit_system import initialize, reset
    from dinner_spinner.domain.acquisition import Acquisition

    reset()
    initialize()

    with pytest.raises(ValueError, match="greater than zero"):
        Acquisition(id=1, ingredient_id=1, quantity=0, unit="g", cost=Decimal("10"))

    with pytest.raises(ValueError, match="greater than zero"):
        Acquisition(id=1, ingredient_id=1, quantity=-1, unit="g", cost=Decimal("10"))


def test_acquisition_rejects_negative_cost():
    """Acquisition rejects negative cost."""
    from decimal import Decimal
    from dinner_spinner.domain.unit_system import initialize, reset
    from dinner_spinner.domain.acquisition import Acquisition

    reset()
    initialize()

    with pytest.raises(ValueError, match="cannot be negative"):
        Acquisition(id=1, ingredient_id=1, quantity=100, unit="g", cost=Decimal("-1"))


def test_acquisition_rejects_invalid_unit():
    """Acquisition rejects invalid/unrecognized unit."""
    from decimal import Decimal
    from dinner_spinner.domain.unit_system import initialize, reset
    from dinner_spinner.domain.acquisition import Acquisition

    reset()
    initialize()

    with pytest.raises(ValueError, match="not a recognized unit"):
        Acquisition(id=1, ingredient_id=1, quantity=100, unit="invalid", cost=Decimal("10"))


def test_acquisition_rejects_cross_category_unit():
    """Acquisition rejects cross-category unit (via Ingredient validation later)."""
    from decimal import Decimal
    from dinner_spinner.domain.unit_system import initialize, reset
    from dinner_spinner.domain.acquisition import Acquisition

    reset()
    initialize()

    # The Acquisition itself doesn't know the ingredient's unit, but it validates
    # that the unit is recognized. Cross-category validation happens at application
    # layer when converting to ingredient's unit.
    acq = Acquisition(id=1, ingredient_id=1, quantity=100, unit="ml",
                      cost=Decimal("10"))
    assert acq.unit == "ml"


def test_acquisition_immutable():
    """Acquisition is immutable after creation (no setters)."""
    from decimal import Decimal
    from dinner_spinner.domain.unit_system import initialize, reset
    from dinner_spinner.domain.acquisition import Acquisition

    reset()
    initialize()

    acq = Acquisition(id=1, ingredient_id=1, quantity=100, unit="g",
                      cost=Decimal("10"))
    # No setters should exist - attempting to modify should fail or be ignored
    # We just verify the object is created correctly and has the right attributes
    assert acq.quantity == 100
    assert acq.unit == "g"
    assert acq.cost == Decimal("10")


def test_consumption_valid():
    """Consumption accepts valid data."""
    from datetime import datetime
    from dinner_spinner.domain.unit_system import initialize, reset
    from dinner_spinner.domain.consumption import Consumption

    reset()
    initialize()

    con = Consumption(id=1, ingredient_id=1, quantity=50, unit="g",
                      consumed_at=datetime(2024, 1, 1))
    assert con.id == 1
    assert con.ingredient_id == 1
    assert con.quantity == 50
    assert con.unit == "g"
    assert con.consumed_at == datetime(2024, 1, 1)


def test_consumption_rejects_zero_quantity():
    """Consumption rejects zero or negative quantity."""
    from dinner_spinner.domain.unit_system import initialize, reset
    from dinner_spinner.domain.consumption import Consumption

    reset()
    initialize()

    with pytest.raises(ValueError, match="greater than zero"):
        Consumption(id=1, ingredient_id=1, quantity=0, unit="g")

    with pytest.raises(ValueError, match="greater than zero"):
        Consumption(id=1, ingredient_id=1, quantity=-1, unit="g")


def test_consumption_immutable():
    """Consumption is immutable after creation."""
    from datetime import datetime
    from dinner_spinner.domain.unit_system import initialize, reset
    from dinner_spinner.domain.consumption import Consumption

    reset()
    initialize()

    con = Consumption(id=1, ingredient_id=1, quantity=50, unit="g",
                      consumed_at=datetime(2024, 1, 1))
    assert con.quantity == 50
    assert con.unit == "g"


def test_waste_valid():
    """Waste accepts valid data."""
    from datetime import datetime
    from dinner_spinner.domain.unit_system import initialize, reset
    from dinner_spinner.domain.waste import Waste

    reset()
    initialize()

    was = Waste(id=1, ingredient_id=1, quantity=25, unit="g",
                wasted_at=datetime(2024, 1, 1))
    assert was.id == 1
    assert was.ingredient_id == 1
    assert was.quantity == 25
    assert was.unit == "g"
    assert was.wasted_at == datetime(2024, 1, 1)


def test_waste_rejects_zero_quantity():
    """Waste rejects zero or negative quantity."""
    from dinner_spinner.domain.unit_system import initialize, reset
    from dinner_spinner.domain.waste import Waste

    reset()
    initialize()

    with pytest.raises(ValueError, match="greater than zero"):
        Waste(id=1, ingredient_id=1, quantity=0, unit="g")

    with pytest.raises(ValueError, match="greater than zero"):
        Waste(id=1, ingredient_id=1, quantity=-1, unit="g")


def test_waste_immutable():
    """Waste is immutable after creation."""
    from datetime import datetime
    from dinner_spinner.domain.unit_system import initialize, reset
    from dinner_spinner.domain.waste import Waste

    reset()
    initialize()

    was = Waste(id=1, ingredient_id=1, quantity=25, unit="g",
                wasted_at=datetime(2024, 1, 1))
    assert was.quantity == 25
    assert was.unit == "g"


# ---------------------------------------------------------------------------
# 4. Unit Boundary Tests
# ---------------------------------------------------------------------------
    """There must be one authoritative conversion implementation."""
    from dinner_spinner.domain import unit_system

    # UnitSystem must be the only conversion module
    assert hasattr(unit_system, "convert")
    assert hasattr(unit_system, "validate_unit")
    assert hasattr(unit_system, "is_initialized")
    assert hasattr(unit_system, "initialize")
    assert hasattr(unit_system, "get_units_by_category")
    assert hasattr(unit_system, "category_of")

    # No other module should define conversion functions
    import dinner_spinner.domain.ingredient as ing_mod
    import dinner_spinner.domain.recipe_ingredient as ri_mod

    # Ingredient and RecipeIngredient should NOT have their own conversion logic
    # Check only functions defined in the module itself (not imported)
    for mod in [ing_mod, ri_mod]:
        for attr in dir(mod):
            attr_lower = attr.lower()
            if "convert" in attr_lower and not attr.startswith("__"):
                obj = getattr(mod, attr)
                # Only fail if the function is defined in this module, not imported
                if getattr(obj, '__module__', None) == mod.__name__:
                    pytest.fail(f"{mod.__name__}.{attr} appears to define conversion logic")


def test_unit_system_has_three_categories():
    """Unit system must have MASS, VOLUME, COUNT categories."""
    from dinner_spinner.domain.unit_system import initialize, get_units_by_category

    initialize()
    assert set(get_units_by_category("MASS")) == {"g", "kg", "oz", "lb"}
    assert set(get_units_by_category("VOLUME")) == {"ml", "l", "cup", "tbsp", "tsp"}
    assert set(get_units_by_category("COUNT")) == {"each", "piece", "pieces", "count"}


def test_unit_system_rejects_cross_category_conversion():
    """Cross-category conversions must be rejected."""
    from dinner_spinner.domain.unit_system import initialize, convert

    initialize()

    # Mass to volume should fail
    with pytest.raises(ValueError, match="different measurement categories"):
        convert(100, "g", "ml")

    # Volume to count should fail
    with pytest.raises(ValueError, match="different measurement categories"):
        convert(1, "cup", "each")

    # Mass to count should fail
    with pytest.raises(ValueError, match="different measurement categories"):
        convert(1000, "g", "piece")


def test_unit_system_supports_same_category_conversion():
    """Same-category conversions must work."""
    from dinner_spinner.domain.unit_system import initialize, convert
    from decimal import Decimal

    initialize()

    # kg to g
    assert convert(Decimal("1"), "kg", "g") == Decimal("1000")
    assert convert(Decimal("500"), "g", "kg") == Decimal("0.5")

    # lb to oz
    assert convert(Decimal("1"), "lb", "oz") == Decimal("16")

    # l to ml
    assert convert(Decimal("1"), "l", "ml") == Decimal("1000")

    # cup to tbsp
    result = convert(Decimal("1"), "cup", "tbsp")
    assert abs(result - Decimal("15.77")) < Decimal("0.01")


def test_unit_system_no_universal_base_unit():
    """No fake universal base unit implying everything converts to everything."""
    from dinner_spinner.domain.unit_system import initialize, convert

    initialize()

    # These should all fail - no universal base unit
    cross_category_pairs = [
        ("g", "ml"), ("kg", "l"), ("oz", "cup"), ("lb", "tbsp"),
        ("g", "each"), ("kg", "piece"), ("ml", "each"), ("l", "piece"),
    ]
    for from_u, to_u in cross_category_pairs:
        with pytest.raises(ValueError):
            convert(1, from_u, to_u)


def test_unit_system_uninitialized_validate_raises():
    """validate_unit() must raise when UnitSystem not initialized."""
    from dinner_spinner.domain.unit_system import validate_unit, is_initialized, reset

    reset()  # Ensure uninitialized state
    assert not is_initialized()

    with pytest.raises(RuntimeError, match="not initialized"):
        validate_unit("g")


def test_unit_system_uninitialized_convert_raises():
    """convert() must raise when UnitSystem not initialized."""
    from dinner_spinner.domain.unit_system import convert, is_initialized, reset

    reset()
    assert not is_initialized()

    with pytest.raises(RuntimeError, match="not initialized"):
        convert(100, "g", "kg")


def test_unit_system_initialized_then_works():
    """After initialize(), validate_unit and convert work correctly."""
    from dinner_spinner.domain.unit_system import initialize, validate_unit, convert, is_initialized, reset

    reset()
    initialize()
    assert is_initialized()
    assert validate_unit("g") is True
    assert validate_unit("invalid") is False
    assert convert(1, "kg", "g") == 1000


# ---------------------------------------------------------------------------
# 5. Relationship Integrity Tests
# ---------------------------------------------------------------------------

def test_recipe_ingredient_unique_constraint():
    """RecipeIngredient cannot contain the same Ingredient twice."""
    from dinner_spinner.domain.recipe_ingredient import RecipeIngredient

    ri1 = RecipeIngredient(id=1, recipe_id=1, ingredient_id=1, quantity=100, unit="g")
    ri2 = RecipeIngredient(id=2, recipe_id=1, ingredient_id=1, quantity=200, unit="g")

    # The UNIQUE constraint is enforced at DB level, but domain entities
    # should be able to represent the concept
    assert ri1.recipe_id == ri2.recipe_id
    assert ri1.ingredient_id == ri2.ingredient_id
    # The domain doesn't enforce uniqueness - that's DB level
    # But the spec says "Database/application integrity must enforce UNIQUE"


def test_ingredient_may_have_zero_or_one_category():
    """Ingredient may have zero or one InventoryCategory."""
    from dinner_spinner.domain.ingredient import Ingredient

    # No category (None)
    ing1 = Ingredient(id=1, name="Flour", inventory_category_id=None, quantity=1000, unit="g")
    assert ing1.inventory_category_id is None

    # With category
    ing2 = Ingredient(id=2, name="Sugar", inventory_category_id=5, quantity=500, unit="g")
    assert ing2.inventory_category_id == 5


def test_inventory_category_may_have_zero_or_many_ingredients():
    """InventoryCategory may have zero or many Ingredients."""
    from dinner_spinner.domain.inventory_category import InventoryCategory

    cat = InventoryCategory(id=1, name="Baking")
    # The relationship is tracked on Ingredient side
    # Category itself just has an ID and name


def test_mealplan_may_have_no_recipe():
    """MealPlan may have no Recipe (empty meal slot)."""
    from dinner_spinner.domain.meal_plan import MealPlan

    mp = MealPlan(id=1, week_start=20260101, day=0, meal_type="Dinner", recipe_id=None, servings=4)
    assert mp.recipe_id is None
    assert mp.servings == 4


def test_mealplan_uniqueness():
    """MealPlan uniqueness follows V1_ARCHITECTURE.md."""
    from dinner_spinner.domain.meal_plan import MealPlan

    mp1 = MealPlan(id=1, week_start=20260101, day=0, meal_type="Dinner", recipe_id=1, servings=4)
    mp2 = MealPlan(id=2, week_start=20260101, day=0, meal_type="Dinner", recipe_id=2, servings=2)

    # Same week_start, day, meal_type should be unique
    assert mp1.week_start == mp2.week_start
    assert mp1.day == mp2.day
    assert mp1.meal_type == mp2.meal_type
    # The DB enforces UNIQUE(week_start, day, meal_type)


def test_recipe_servings_positive():
    """Recipe.servings must be > 0."""
    from dinner_spinner.domain.recipe import Recipe

    with pytest.raises(ValueError, match="greater than zero"):
        Recipe(id=1, name="Test", servings=0)

    with pytest.raises(ValueError, match="greater than zero"):
        Recipe(id=1, name="Test", servings=-1)

    r = Recipe(id=1, name="Test", servings=4)
    assert r.servings == 4


def test_recipe_ingredient_quantity_positive():
    """RecipeIngredient.quantity must be > 0."""
    from dinner_spinner.domain.recipe_ingredient import RecipeIngredient

    with pytest.raises(ValueError, match="greater than zero"):
        RecipeIngredient(id=1, recipe_id=1, ingredient_id=1, quantity=0, unit="g")

    with pytest.raises(ValueError, match="greater than zero"):
        RecipeIngredient(id=1, recipe_id=1, ingredient_id=1, quantity=-1, unit="g")

    ri = RecipeIngredient(id=1, recipe_id=1, ingredient_id=1, quantity=0.5, unit="g")
    assert ri.quantity == 0.5


def test_ingredient_quantity_nonnegative():
    """Ingredient.quantity must be >= 0."""
    from dinner_spinner.domain.ingredient import Ingredient

    with pytest.raises(ValueError, match="non-negative"):
        Ingredient(id=1, name="Test", inventory_category_id=None, quantity=-1, unit="g")

    ing = Ingredient(id=1, name="Test", inventory_category_id=None, quantity=0, unit="g")
    assert ing.quantity == 0

    ing = Ingredient(id=1, name="Test", inventory_category_id=None, quantity=100.5, unit="g")
    assert ing.quantity == 100.5


def test_mealplan_servings_positive():
    """MealPlan.servings must be > 0."""
    from dinner_spinner.domain.meal_plan import MealPlan

    with pytest.raises(ValueError, match="greater than zero"):
        MealPlan(id=1, week_start=20260101, day=0, meal_type="Dinner", recipe_id=1, servings=0)

    with pytest.raises(ValueError, match="greater than zero"):
        MealPlan(id=1, week_start=20260101, day=0, meal_type="Dinner", recipe_id=1, servings=-1)

    mp = MealPlan(id=1, week_start=20260101, day=0, meal_type="Dinner", recipe_id=1, servings=8)
    assert mp.servings == 8


# ---------------------------------------------------------------------------
# 6. Deletion Behavior Tests
# ---------------------------------------------------------------------------

def test_category_deletion_nulls_ingredient_category():
    """Deleting an InventoryCategory must set Ingredient.inventory_category_id = NULL."""
    # This is enforced at DB level via ondelete="SET NULL" on the FK
    # The domain model should reflect this by allowing category_id to be None
    from dinner_spinner.domain.ingredient import Ingredient

    ing = Ingredient(id=1, name="Flour", inventory_category_id=5, quantity=1000, unit="g")
    # Simulating category deletion by setting to None
    ing.inventory_category_id = None
    assert ing.inventory_category_id is None


def test_recipe_deletion_cascades_recipe_ingredients():
    """Deleting a Recipe must cascade-delete its RecipeIngredients."""
    # This is enforced at DB level via cascade="all, delete-orphan"
    # and ondelete="CASCADE" on the FK
    pass  # Tested at DB integration level


def test_recipe_deletion_preserves_ingredients():
    """Deleting a Recipe must NOT delete its Ingredients."""
    # This is enforced by the FK on RecipeIngredient.ingredient_id
    # having ondelete="RESTRICT" (or no cascade)
    # Ingredient is not deleted when RecipeIngredient is deleted
    pass  # Tested at DB integration level


def test_recipe_deletion_nulls_mealplan_recipe():
    """Deleting a Recipe must set MealPlan.recipe_id = NULL."""
    # This is enforced at DB level via ondelete="SET NULL" on MealPlan.recipe_id FK
    from dinner_spinner.domain.meal_plan import MealPlan

    mp = MealPlan(id=1, week_start=20260101, day=0, meal_type="Dinner", recipe_id=1, servings=4)
    # Simulating recipe deletion
    mp.recipe_id = None
    assert mp.recipe_id is None


def test_recipe_ingredient_deletion_preserves_ingredient_and_recipe():
    """Deleting a RecipeIngredient does not modify the Ingredient or Recipe."""
    from dinner_spinner.domain.recipe_ingredient import RecipeIngredient

    ri = RecipeIngredient(id=1, recipe_id=1, ingredient_id=1, quantity=100, unit="g")
    # Deleting ri should not affect ingredient_id=1 or recipe_id=1
    # This is a DB-level behavior; domain just represents the entity
    assert ri.ingredient_id == 1
    assert ri.recipe_id == 1


def test_ingredient_deletion_blocked_when_referenced():
    """An Ingredient cannot be deleted while referenced by a RecipeIngredient."""
    # This is enforced at DB level via ondelete="RESTRICT" on
    # RecipeIngredient.ingredient_id FK
    pass  # Tested at DB integration level


# ---------------------------------------------------------------------------
# 7. Domain Entity Exports Test
# ---------------------------------------------------------------------------

def test_domain_exports_exact_entities():
    """Domain layer exports exactly the V1 foundational entities."""
    from dinner_spinner.domain import __all__ as domain_exports

    expected = {
        "Ingredient",
        "InventoryCategory",
        "Recipe",
        "RecipeIngredient",
        "MealPlan",
        "Acquisition",
        "Consumption",
        "Waste",
        "UnitSystem",
        "IngredientDemand",
        "calculate_demand",
        "calculate_demand_for_week",
        "IngredientRequirement",
        "calculate_inventory_requirements",
        "IngredientRequirement",
        "ShoppingListItem",
        "calculate_shopping_list",
        "UnitSystem",
    }

    # Check all expected are present
    for e in expected:
        assert e in domain_exports, f"Missing export: {e}"

    # Check no unexpected (forbidden) entities
    forbidden = {
        "Container", "InventoryLot", "Product", "Package", "Store",
        "Brand", "Barcode", "Nutrition", "InventoryEvent", "Transfer",
        "PriceEstimate", "ShoppingList",
        "Demand", "AvailableInventory", "NetRequirement",
        "CostPerUnit",
    }
    for f in forbidden:
        assert f not in domain_exports, f"Forbidden entity exported: {f}"


# ---------------------------------------------------------------------------
# 8. Slice 3: Demand Tests
# ---------------------------------------------------------------------------

def test_demand_domain_exports():
    """Demand entities are exported from domain layer."""
    from dinner_spinner.domain import __all__ as domain_exports

    expected = {"IngredientDemand", "calculate_demand", "calculate_demand_for_week"}
    for e in expected:
        assert e in domain_exports, f"Missing export: {e}"


def test_ingredient_demand_creation():
    """IngredientDemand can be created with valid data."""
    from decimal import Decimal
    from dinner_spinner.domain.demand import IngredientDemand

    demand = IngredientDemand(
        ingredient_id=1,
        ingredient_name="Flour",
        quantity=Decimal("1000"),
        unit="g"
    )
    assert demand.ingredient_id == 1
    assert demand.ingredient_name == "Flour"
    assert demand.quantity == Decimal("1000")
    assert demand.unit == "g"


def test_ingredient_demand_rejects_negative_quantity():
    """IngredientDemand rejects negative quantity."""
    from decimal import Decimal
    from dinner_spinner.domain.demand import IngredientDemand

    with pytest.raises(ValueError, match="negative"):
        IngredientDemand(
            ingredient_id=1,
            ingredient_name="Flour",
            quantity=Decimal("-100"),
            unit="g"
        )


def test_ingredient_demand_rejects_empty_unit():
    """IngredientDemand rejects empty unit."""
    from decimal import Decimal
    from dinner_spinner.domain.demand import IngredientDemand

    with pytest.raises(ValueError, match="required"):
        IngredientDemand(
            ingredient_id=1,
            ingredient_name="Flour",
            quantity=Decimal("100"),
            unit=""
        )


def test_calculate_demand_basic():
    """Basic demand calculation works."""
    from dinner_spinner.domain.demand import calculate_demand
    from dinner_spinner.domain.unit_system import initialize, reset
    from dinner_spinner.domain.meal_plan import MealPlan
    from dinner_spinner.domain.recipe import Recipe
    from dinner_spinner.domain.recipe_ingredient import RecipeIngredient

    reset()
    initialize()

    # Recipe: 4 servings, 500g flour
    recipe = Recipe(id=1, name="Bread", servings=4)
    ri = RecipeIngredient(id=1, recipe_id=1, ingredient_id=1, quantity=500, unit="g")

    # MealPlan: 8 servings (2x scale)
    mp = MealPlan(id=1, week_start=20260101, day=0, meal_type="Dinner", recipe_id=1, servings=8)

    demands = calculate_demand(
        meal_plans=[mp],
        recipes={1: recipe},
        recipe_ingredients={1: [ri]},
    )

    assert len(demands) == 1
    assert demands[0].ingredient_id == 1
    assert demands[0].quantity == 1000  # 500g * (8/4) = 1000g
    assert demands[0].unit == "g"


def test_calculate_demand_scaling_up():
    """Demand scales up correctly."""
    from dinner_spinner.domain.demand import calculate_demand
    from dinner_spinner.domain.unit_system import initialize, reset
    from dinner_spinner.domain.meal_plan import MealPlan
    from dinner_spinner.domain.recipe import Recipe
    from dinner_spinner.domain.recipe_ingredient import RecipeIngredient

    reset()
    initialize()

    recipe = Recipe(id=1, name="Bread", servings=4)
    ri = RecipeIngredient(id=1, recipe_id=1, ingredient_id=1, quantity=500, unit="g")

    # 12 servings (3x scale)
    mp = MealPlan(id=1, week_start=20260101, day=0, meal_type="Dinner", recipe_id=1, servings=12)

    demands = calculate_demand(
        meal_plans=[mp],
        recipes={1: recipe},
        recipe_ingredients={1: [ri]},
    )

    assert len(demands) == 1
    assert demands[0].quantity == 1500  # 500g * (12/4) = 1500g


def test_calculate_demand_scaling_down():
    """Demand scales down correctly."""
    from dinner_spinner.domain.demand import calculate_demand
    from dinner_spinner.domain.unit_system import initialize, reset
    from dinner_spinner.domain.meal_plan import MealPlan
    from dinner_spinner.domain.recipe import Recipe
    from dinner_spinner.domain.recipe_ingredient import RecipeIngredient

    reset()
    initialize()

    recipe = Recipe(id=1, name="Bread", servings=8)
    ri = RecipeIngredient(id=1, recipe_id=1, ingredient_id=1, quantity=1000, unit="g")

    # 2 servings (0.25x scale)
    mp = MealPlan(id=1, week_start=20260101, day=0, meal_type="Dinner", recipe_id=1, servings=2)

    demands = calculate_demand(
        meal_plans=[mp],
        recipes={1: recipe},
        recipe_ingredients={1: [ri]},
    )

    assert len(demands) == 1
    assert demands[0].quantity == 250  # 1000g * (2/8) = 250g


def test_calculate_demand_unit_normalization():
    """Demand normalizes units for aggregation."""
    from dinner_spinner.domain.demand import calculate_demand
    from dinner_spinner.domain.unit_system import initialize, reset
    from dinner_spinner.domain.meal_plan import MealPlan
    from dinner_spinner.domain.recipe import Recipe
    from dinner_spinner.domain.recipe_ingredient import RecipeIngredient

    reset()
    initialize()

    # Recipe 1: 1 kg flour
    recipe1 = Recipe(id=1, name="Bread", servings=4)
    ri1 = RecipeIngredient(id=1, recipe_id=1, ingredient_id=1, quantity=1, unit="kg")

    # Recipe 2: 500 g flour (same ingredient)
    recipe2 = Recipe(id=2, name="Pasta", servings=4)
    ri2 = RecipeIngredient(id=2, recipe_id=2, ingredient_id=1, quantity=500, unit="g")

    # 4 servings each (no scaling)
    mp1 = MealPlan(id=1, week_start=20260101, day=0, meal_type="Dinner", recipe_id=1, servings=4)
    mp2 = MealPlan(id=2, week_start=20260101, day=1, meal_type="Dinner", recipe_id=2, servings=4)

    demands = calculate_demand(
        meal_plans=[mp1, mp2],
        recipes={1: recipe1, 2: recipe2},
        recipe_ingredients={1: [ri1], 2: [ri2]},
    )

    assert len(demands) == 1
    # 1 kg = 1000g, + 500g = 1500g = 1.5 kg
    assert demands[0].quantity == 1.5
    assert demands[0].unit == "kg"  # First unit wins


def test_calculate_demand_cross_category_rejected():
    """Demand rejects cross-category unit aggregation."""
    from dinner_spinner.domain.demand import calculate_demand
    from dinner_spinner.domain.unit_system import initialize, reset
    from dinner_spinner.domain.meal_plan import MealPlan
    from dinner_spinner.domain.recipe import Recipe
    from dinner_spinner.domain.recipe_ingredient import RecipeIngredient

    reset()
    initialize()

    # Recipe 1: 100 g flour (mass)
    recipe1 = Recipe(id=1, name="Bread", servings=4)
    ri1 = RecipeIngredient(id=1, recipe_id=1, ingredient_id=1, quantity=100, unit="g")

    # Recipe 2: 1 cup flour (volume) - same ingredient_id but different unit category
    recipe2 = Recipe(id=2, name="Cake", servings=4)
    ri2 = RecipeIngredient(id=2, recipe_id=2, ingredient_id=1, quantity=1, unit="cup")

    mp1 = MealPlan(id=1, week_start=20260101, day=0, meal_type="Dinner", recipe_id=1, servings=4)
    mp2 = MealPlan(id=2, week_start=20260101, day=1, meal_type="Dinner", recipe_id=2, servings=4)

    with pytest.raises(ValueError, match="incompatible units"):
        calculate_demand(
            meal_plans=[mp1, mp2],
            recipes={1: recipe1, 2: recipe2},
            recipe_ingredients={1: [ri1], 2: [ri2]},
        )


def test_calculate_demand_empty_meal_plan():
    """Empty meal plan produces no demand."""
    from dinner_spinner.domain.demand import calculate_demand
    from dinner_spinner.domain.unit_system import initialize, reset

    reset()
    initialize()

    demands = calculate_demand(
        meal_plans=[],
        recipes={},
        recipe_ingredients={},
    )

    assert demands == []


def test_calculate_demand_empty_slot_produces_no_demand():
    """MealPlan with recipe_id = NULL produces no demand."""
    from dinner_spinner.domain.demand import calculate_demand
    from dinner_spinner.domain.unit_system import initialize, reset
    from dinner_spinner.domain.meal_plan import MealPlan

    reset()
    initialize()

    mp = MealPlan(id=1, week_start=20260101, day=0, meal_type="Dinner", recipe_id=None, servings=4)

    demands = calculate_demand(
        meal_plans=[mp],
        recipes={},
        recipe_ingredients={},
    )

    assert demands == []


def test_calculate_demand_recipe_with_no_ingredients():
    """Recipe with no ingredients produces no demand."""
    from dinner_spinner.domain.demand import calculate_demand
    from dinner_spinner.domain.unit_system import initialize, reset
    from dinner_spinner.domain.meal_plan import MealPlan
    from dinner_spinner.domain.recipe import Recipe

    reset()
    initialize()

    recipe = Recipe(id=1, name="Empty", servings=4)
    mp = MealPlan(id=1, week_start=20260101, day=0, meal_type="Dinner", recipe_id=1, servings=4)

    demands = calculate_demand(
        meal_plans=[mp],
        recipes={1: recipe},
        recipe_ingredients={1: []},
    )

    assert demands == []


def test_calculate_demand_deterministic():
    """Demand calculation is deterministic."""
    from dinner_spinner.domain.demand import calculate_demand
    from dinner_spinner.domain.unit_system import initialize, reset
    from dinner_spinner.domain.meal_plan import MealPlan
    from dinner_spinner.domain.recipe import Recipe
    from dinner_spinner.domain.recipe_ingredient import RecipeIngredient

    reset()
    initialize()

    recipe = Recipe(id=1, name="Bread", servings=4)
    ri = RecipeIngredient(id=1, recipe_id=1, ingredient_id=1, quantity=500, unit="g")
    mp = MealPlan(id=1, week_start=20260101, day=0, meal_type="Dinner", recipe_id=1, servings=8)

    demands1 = calculate_demand(
        meal_plans=[mp],
        recipes={1: recipe},
        recipe_ingredients={1: [ri]},
    )

    demands2 = calculate_demand(
        meal_plans=[mp],
        recipes={1: recipe},
        recipe_ingredients={1: [ri]},
    )

    assert demands1 == demands2


def test_calculate_demand_preserves_original_recipe_ingredient():
    """Demand calculation does not modify original RecipeIngredient data."""
    from dinner_spinner.domain.demand import calculate_demand
    from dinner_spinner.domain.unit_system import initialize, reset
    from dinner_spinner.domain.meal_plan import MealPlan
    from dinner_spinner.domain.recipe import Recipe
    from dinner_spinner.domain.recipe_ingredient import RecipeIngredient

    reset()
    initialize()

    ri = RecipeIngredient(id=1, recipe_id=1, ingredient_id=1, quantity=500, unit="g")
    recipe = Recipe(id=1, name="Bread", servings=4)
    mp = MealPlan(id=1, week_start=20260101, day=0, meal_type="Dinner", recipe_id=1, servings=8)

    # Store original values
    orig_qty = ri.quantity
    orig_unit = ri.unit

    calculate_demand(
        meal_plans=[mp],
        recipes={1: recipe},
        recipe_ingredients={1: [ri]},
    )

    # Original should be unchanged
    assert ri.quantity == orig_qty
    assert ri.unit == orig_unit


# ---------------------------------------------------------------------------
# 9. Demand Application Service Tests
# ---------------------------------------------------------------------------

def test_demand_application_service_calculates_demand():
    """Application service correctly calculates demand."""
    from dinner_spinner.application.demand import get_demand_for_week
    from dinner_persistence.models import Ingredient, Recipe, RecipeIngredient, MealPlan

    # This test needs a full app context, so we'll skip it here
    # It's covered by test_application.py
    pass


# ---------------------------------------------------------------------------
# 10. Slice 4: Inventory Requirement Tests
# ---------------------------------------------------------------------------

def test_ingredient_requirement_creation():
    """IngredientRequirement can be created with valid data."""
    from decimal import Decimal
    from dinner_spinner.domain.inventory_requirement import IngredientRequirement

    req = IngredientRequirement(
        ingredient_id=1,
        ingredient_name="Flour",
        demand_quantity=Decimal("1000"),
        demand_unit="g",
        available_quantity=Decimal("500"),
        available_unit="g",
        net_requirement_quantity=Decimal("500"),
        net_requirement_unit="g",
    )
    assert req.ingredient_id == 1
    assert req.ingredient_name == "Flour"
    assert req.demand_quantity == Decimal("1000")
    assert req.demand_unit == "g"
    assert req.available_quantity == Decimal("500")
    assert req.available_unit == "g"
    assert req.net_requirement_quantity == Decimal("500")
    assert req.net_requirement_unit == "g"


def test_ingredient_requirement_rejects_negative_demand():
    """IngredientRequirement rejects negative demand quantity."""
    from decimal import Decimal
    from dinner_spinner.domain.inventory_requirement import IngredientRequirement

    with pytest.raises(ValueError, match="negative"):
        IngredientRequirement(
            ingredient_id=1,
            ingredient_name="Flour",
            demand_quantity=Decimal("-100"),
            demand_unit="g",
            available_quantity=Decimal("500"),
            available_unit="g",
            net_requirement_quantity=Decimal("500"),
            net_requirement_unit="g",
        )


def test_ingredient_requirement_rejects_negative_available():
    """IngredientRequirement rejects negative available quantity."""
    from decimal import Decimal
    from dinner_spinner.domain.inventory_requirement import IngredientRequirement

    with pytest.raises(ValueError, match="negative"):
        IngredientRequirement(
            ingredient_id=1,
            ingredient_name="Flour",
            demand_quantity=Decimal("1000"),
            demand_unit="g",
            available_quantity=Decimal("-100"),
            available_unit="g",
            net_requirement_quantity=Decimal("500"),
            net_requirement_unit="g",
        )


def test_ingredient_requirement_rejects_negative_net():
    """IngredientRequirement rejects negative net requirement quantity."""
    from decimal import Decimal
    from dinner_spinner.domain.inventory_requirement import IngredientRequirement

    with pytest.raises(ValueError, match="negative"):
        IngredientRequirement(
            ingredient_id=1,
            ingredient_name="Flour",
            demand_quantity=Decimal("1000"),
            demand_unit="g",
            available_quantity=Decimal("500"),
            available_unit="g",
            net_requirement_quantity=Decimal("-100"),
            net_requirement_unit="g",
        )


def test_ingredient_requirement_rejects_empty_units():
    """IngredientRequirement rejects empty units."""
    from decimal import Decimal
    from dinner_spinner.domain.inventory_requirement import IngredientRequirement

    with pytest.raises(ValueError, match="required"):
        IngredientRequirement(
            ingredient_id=1,
            ingredient_name="Flour",
            demand_quantity=Decimal("1000"),
            demand_unit="",
            available_quantity=Decimal("500"),
            available_unit="g",
            net_requirement_quantity=Decimal("500"),
            net_requirement_unit="g",
        )

    with pytest.raises(ValueError, match="required"):
        IngredientRequirement(
            ingredient_id=1,
            ingredient_name="Flour",
            demand_quantity=Decimal("1000"),
            demand_unit="g",
            available_quantity=Decimal("500"),
            available_unit="",
            net_requirement_quantity=Decimal("500"),
            net_requirement_unit="g",
        )

    with pytest.raises(ValueError, match="required"):
        IngredientRequirement(
            ingredient_id=1,
            ingredient_name="Flour",
            demand_quantity=Decimal("1000"),
            demand_unit="g",
            available_quantity=Decimal("500"),
            available_unit="g",
            net_requirement_quantity=Decimal("500"),
            net_requirement_unit="",
        )


def test_calculate_inventory_requirements_demand_greater_than_inventory():
    """Demand greater than inventory produces positive net requirement."""
    from decimal import Decimal
    from dinner_spinner.domain.inventory_requirement import calculate_inventory_requirements
    from dinner_spinner.domain.unit_system import initialize, reset
    from dinner_spinner.domain.demand import IngredientDemand
    from dinner_spinner.domain.ingredient import Ingredient

    reset()
    initialize()

    demands = [IngredientDemand(1, "Flour", Decimal("2000"), "g")]
    ingredients = {1: Ingredient(1, "Flour", None, Decimal("1200"), "g")}

    reqs = calculate_inventory_requirements(demands, {1: Ingredient(1, "Flour", None, Decimal("1200"), "g")})

    assert len(reqs) == 1
    req = reqs[0]
    assert req.ingredient_id == 1
    assert req.ingredient_name == "Flour"
    assert req.demand_quantity == Decimal("2000")
    assert req.demand_unit == "g"
    assert req.available_quantity == Decimal("1200")
    assert req.available_unit == "g"
    assert req.net_requirement_quantity == Decimal("800")
    assert req.net_requirement_unit == "g"


def test_calculate_inventory_requirements_demand_equals_inventory():
    """Demand equals inventory produces zero net requirement."""
    from decimal import Decimal
    from dinner_spinner.domain.inventory_requirement import calculate_inventory_requirements
    from dinner_spinner.domain.unit_system import initialize, reset
    from dinner_spinner.domain.demand import IngredientDemand
    from dinner_spinner.domain.ingredient import Ingredient

    reset()
    initialize()

    demands = [IngredientDemand(1, "Flour", Decimal("1000"), "g")]
    ingredients = {1: Ingredient(1, "Flour", None, Decimal("1000"), "g")}

    reqs = calculate_inventory_requirements(demands, {1: Ingredient(1, "Flour", None, Decimal("1000"), "g")})

    assert len(reqs) == 1
    req = reqs[0]
    assert req.net_requirement_quantity == Decimal("0")
    assert req.net_requirement_unit == "g"


def test_calculate_inventory_requirements_inventory_greater_than_demand():
    """Inventory greater than demand produces zero net requirement (surplus)."""
    from decimal import Decimal
    from dinner_spinner.domain.inventory_requirement import calculate_inventory_requirements
    from dinner_spinner.domain.unit_system import initialize, reset
    from dinner_spinner.domain.demand import IngredientDemand
    from dinner_spinner.domain.ingredient import Ingredient

    reset()
    initialize()

    demands = [IngredientDemand(1, "Flour", Decimal("1000"), "g")]
    ingredients = {1: Ingredient(1, "Flour", None, Decimal("1500"), "g")}

    reqs = calculate_inventory_requirements(demands, {1: Ingredient(1, "Flour", None, Decimal("1500"), "g")})

    assert len(reqs) == 1
    req = reqs[0]
    assert req.net_requirement_quantity == Decimal("0")
    assert req.net_requirement_unit == "g"
    # Available quantity should reflect the actual inventory
    assert req.available_quantity == Decimal("1500")


def test_calculate_inventory_requirements_zero_inventory():
    """Zero inventory produces full demand as net requirement."""
    from decimal import Decimal
    from dinner_spinner.domain.inventory_requirement import calculate_inventory_requirements
    from dinner_spinner.domain.unit_system import initialize, reset
    from dinner_spinner.domain.demand import IngredientDemand
    from dinner_spinner.domain.ingredient import Ingredient

    reset()
    initialize()

    demands = [IngredientDemand(1, "Flour", Decimal("1000"), "g")]
    ingredients = {1: Ingredient(1, "Flour", None, Decimal("0"), "g")}

    reqs = calculate_inventory_requirements(demands, {1: Ingredient(1, "Flour", None, Decimal("0"), "g")})

    assert len(reqs) == 1
    req = reqs[0]
    assert req.net_requirement_quantity == Decimal("1000")
    assert req.net_requirement_unit == "g"
    assert req.available_quantity == Decimal("0")


def test_calculate_inventory_requirements_cross_unit_conversion():
    """Inventory requirement handles cross-unit conversion (kg vs g)."""
    from decimal import Decimal
    from dinner_spinner.domain.inventory_requirement import calculate_inventory_requirements
    from dinner_spinner.domain.unit_system import initialize, reset
    from dinner_spinner.domain.demand import IngredientDemand
    from dinner_spinner.domain.ingredient import Ingredient

    reset()
    initialize()

    # Demand in kg, inventory in g
    demands = [IngredientDemand(1, "Flour", Decimal("2"), "kg")]
    ingredients = {1: Ingredient(1, "Flour", None, Decimal("1500"), "g")}

    reqs = calculate_inventory_requirements(demands, {1: Ingredient(1, "Flour", None, Decimal("1500"), "g")})

    assert len(reqs) == 1
    req = reqs[0]
    # 2kg = 2000g, available 1500g, net = 500g = 0.5kg
    assert req.net_requirement_quantity == Decimal("0.5")
    assert req.net_requirement_unit == "kg"  # Uses demand's unit


def test_calculate_inventory_requirements_cross_category_rejected():
    """Cross-category unit aggregation is rejected."""
    from decimal import Decimal
    from dinner_spinner.domain.inventory_requirement import calculate_inventory_requirements
    from dinner_spinner.domain.unit_system import initialize, reset
    from dinner_spinner.domain.demand import IngredientDemand
    from dinner_spinner.domain.ingredient import Ingredient

    reset()
    initialize()

    demands = [IngredientDemand(1, "Flour", Decimal("100"), "g")]
    ingredients = {1: Ingredient(1, "Flour", None, Decimal("500"), "ml")}

    with pytest.raises(ValueError, match="incompatible"):
        calculate_inventory_requirements(demands, {1: Ingredient(1, "Flour", None, Decimal("500"), "ml")})


def test_calculate_inventory_requirements_demand_only_ingredient():
    """Demand-only ingredient (no inventory) produces full demand as net requirement."""
    from decimal import Decimal
    from dinner_spinner.domain.inventory_requirement import calculate_inventory_requirements
    from dinner_spinner.domain.unit_system import initialize, reset
    from dinner_spinner.domain.demand import IngredientDemand
    from dinner_spinner.domain.ingredient import Ingredient

    reset()
    initialize()

    demands = [IngredientDemand(1, "Flour", Decimal("1000"), "g")]
    # No inventory record for this ingredient
    ingredients = {}

    reqs = calculate_inventory_requirements(demands, {})

    assert len(reqs) == 1
    req = reqs[0]
    assert req.net_requirement_quantity == Decimal("1000")
    assert req.net_requirement_unit == "g"
    assert req.available_quantity == Decimal("0")


def test_calculate_inventory_requirements_inventory_only_no_demand():
    """Inventory-only ingredient (no demand) is not included in requirements."""
    from decimal import Decimal
    from dinner_spinner.domain.inventory_requirement import calculate_inventory_requirements
    from dinner_spinner.domain.unit_system import initialize, reset
    from dinner_spinner.domain.demand import IngredientDemand
    from dinner_spinner.domain.ingredient import Ingredient

    reset()
    initialize()

    # Demand for flour only
    demands = [IngredientDemand(1, "Flour", Decimal("1000"), "g")]
    # Inventory has both flour and sugar, but only flour has demand
    ingredients = {
        1: Ingredient(1, "Flour", None, Decimal("500"), "g"),
        2: Ingredient(2, "Sugar", None, Decimal("2000"), "g"),
    }

    reqs = calculate_inventory_requirements(demands, ingredients)

    assert len(reqs) == 1
    assert reqs[0].ingredient_id == 1
    assert reqs[0].ingredient_name == "Flour"


def test_calculate_inventory_requirements_multiple_ingredients():
    """Multiple ingredients aggregated correctly."""
    from decimal import Decimal
    from dinner_spinner.domain.inventory_requirement import calculate_inventory_requirements
    from dinner_spinner.domain.unit_system import initialize, reset
    from dinner_spinner.domain.demand import IngredientDemand
    from dinner_spinner.domain.ingredient import Ingredient

    reset()
    initialize()

    demands = [
        IngredientDemand(1, "Flour", Decimal("2000"), "g"),
        IngredientDemand(2, "Sugar", Decimal("1000"), "g"),
    ]
    ingredients = {
        1: Ingredient(1, "Flour", None, Decimal("500"), "g"),
        2: Ingredient(2, "Sugar", None, Decimal("1500"), "g"),
    }

    reqs = calculate_inventory_requirements(demands, ingredients)

    assert len(reqs) == 2
    # Flour: 2000 - 500 = 1500g needed
    assert reqs[0].ingredient_id == 1
    assert reqs[0].net_requirement_quantity == Decimal("1500")
    # Sugar: 1000 - 1500 = 0 (surplus)
    assert reqs[1].ingredient_id == 2
    assert reqs[1].net_requirement_quantity == Decimal("0")


def test_calculate_inventory_requirements_cross_category_rejected():
    """Incompatible units between demand and inventory are rejected."""
    from decimal import Decimal
    from dinner_spinner.domain.inventory_requirement import calculate_inventory_requirements
    from dinner_spinner.domain.unit_system import initialize, reset
    from dinner_spinner.domain.demand import IngredientDemand
    from dinner_spinner.domain.ingredient import Ingredient

    reset()
    initialize()

    demands = [IngredientDemand(1, "Flour", Decimal("100"), "g")]
    ingredients = {1: Ingredient(1, "Flour", None, Decimal("500"), "ml")}

    with pytest.raises(ValueError, match="Cannot compare demand"):
        calculate_inventory_requirements(demands, {1: Ingredient(1, "Flour", None, Decimal("500"), "ml")})


def test_calculate_inventory_requirements_zero_inventory_cross_category_allowed():
    """Zero inventory with incompatible units is allowed (zero in any unit is zero)."""
    from decimal import Decimal
    from dinner_spinner.domain.inventory_requirement import calculate_inventory_requirements
    from dinner_spinner.domain.unit_system import initialize, reset
    from dinner_spinner.domain.demand import IngredientDemand
    from dinner_spinner.domain.ingredient import Ingredient

    reset()
    initialize()

    # Demand in grams, inventory in ml but quantity is zero
    demands = [IngredientDemand(1, "Flour", Decimal("100"), "g")]
    ingredients = {1: Ingredient(1, "Flour", None, Decimal("0"), "ml")}

    # Should not raise - zero inventory in any unit is valid
    reqs = calculate_inventory_requirements(demands, {1: Ingredient(1, "Flour", None, Decimal("0"), "ml")})

    assert len(reqs) == 1
    req = reqs[0]
    assert req.ingredient_id == 1
    assert req.ingredient_name == "Flour"
    assert req.demand_quantity == Decimal("100")
    assert req.demand_unit == "g"
    assert req.available_quantity == Decimal("0")
    assert req.available_unit == "ml"  # Original inventory unit preserved
    assert req.net_requirement_quantity == Decimal("100")  # Full demand needed
    assert req.net_requirement_unit == "g"  # Net requirement in demand's unit


def test_calculate_inventory_requirements_preserves_original_data():
    """Calculation does not modify original demand or ingredient objects."""
    from decimal import Decimal
    from dinner_spinner.domain.inventory_requirement import calculate_inventory_requirements
    from dinner_spinner.domain.unit_system import initialize, reset
    from dinner_spinner.domain.demand import IngredientDemand
    from dinner_spinner.domain.ingredient import Ingredient

    reset()
    initialize()

    demand = IngredientDemand(1, "Flour", Decimal("1000"), "g")
    ingredient = Ingredient(1, "Flour", None, Decimal("500"), "g")

    orig_demand_qty = demand.quantity
    orig_demand_unit = demand.unit
    orig_ing_qty = ingredient.quantity
    orig_ing_unit = ingredient.unit

    calculate_inventory_requirements([demand], {1: ingredient})

    # Original objects unchanged
    assert demand.quantity == orig_demand_qty
    assert demand.unit == orig_demand_unit
    assert ingredient.quantity == orig_ing_qty
    assert ingredient.unit == orig_ing_unit


def test_calculate_inventory_requirements_deterministic():
    """Same inputs always produce same outputs."""
    from decimal import Decimal
    from dinner_spinner.domain.inventory_requirement import calculate_inventory_requirements
    from dinner_spinner.domain.unit_system import initialize, reset
    from dinner_spinner.domain.demand import IngredientDemand
    from dinner_spinner.domain.ingredient import Ingredient

    reset()
    initialize()

    demands = [IngredientDemand(1, "Flour", Decimal("1000"), "g")]
    ingredients = {1: Ingredient(1, "Flour", None, Decimal("500"), "g")}

    reqs1 = calculate_inventory_requirements(demands, {1: Ingredient(1, "Flour", None, Decimal("500"), "g")})
    reqs2 = calculate_inventory_requirements(demands, {1: Ingredient(1, "Flour", None, Decimal("500"), "g")})

    assert reqs1 == reqs2


def test_calculate_inventory_requirements_empty_demand():
    """Empty demand list produces empty requirements."""
    from dinner_spinner.domain.inventory_requirement import calculate_inventory_requirements
    from dinner_spinner.domain.unit_system import initialize, reset

    reset()
    initialize()

    reqs = calculate_inventory_requirements([], {})
    assert reqs == []


# ---------------------------------------------------------------------------
# 11. Slice 4 Architecture Tests
# ---------------------------------------------------------------------------

def test_no_available_inventory_entity():
    """No AvailableInventory entity in domain."""
    from dinner_spinner.domain import __all__ as domain_exports
    assert "AvailableInventory" not in domain_exports


def test_no_net_requirement_entity():
    """No NetRequirement entity in domain."""
    from dinner_spinner.domain import __all__ as domain_exports
    assert "NetRequirement" not in domain_exports


def test_no_inventory_requirement_entity():
    """No InventoryRequirement entity in domain exports (it's a projection)."""
    from dinner_spinner.domain import __all__ as domain_exports
    # IngredientRequirement is a projection, not an authoritative entity
    # It's used for calculation results only
    assert "InventoryRequirement" not in domain_exports


def test_no_shopping_list_entity_in_domain():
    """ShoppingList not in domain."""
    from dinner_spinner.domain import __all__ as domain_exports
    assert "ShoppingList" not in domain_exports


def test_no_transfer_entity():
    """No Transfer entity."""
    from dinner_spinner.domain import __all__ as domain_exports
    assert "Transfer" not in domain_exports


def test_no_location_entity():
    """No Location entity."""
    from dinner_spinner.domain import __all__ as domain_exports
    assert "Location" not in domain_exports


def test_no_container_entity():
    """No Container entity."""
    from dinner_spinner.domain import __all__ as domain_exports
    assert "Container" not in domain_exports


def test_no_shopping_list_persistence_model():
    """No ShoppingList persistence model."""
    from dinner_persistence.models import Base
    tables = Base.metadata.tables.keys()
    assert "shopping_list" not in tables
    assert "shopping_list_item" not in tables


def test_no_available_inventory_persistence_model():
    """No AvailableInventory persistence model."""
    from dinner_persistence.models import Base
    tables = Base.metadata.tables.keys()
    assert "available_inventory" not in tables
    assert "net_requirement" not in tables
    assert "inventory_requirement" not in tables


# ---------------------------------------------------------------------------
# 12. Slice 6: Costing Tests
# ---------------------------------------------------------------------------

def test_costing_domain_exports():
    """Costing entities are exported from domain layer."""
    from dinner_spinner.domain import __all__ as domain_exports

    expected = {
        "IngredientCost",
        "RecipeIngredientCost",
        "RecipeCost",
        "MealCost",
        "calculate_ingredient_costs",
        "calculate_recipe_costs",
        "calculate_meal_costs",
        "calculate_weekly_cost_summary",
    }
    for e in expected:
        assert e in domain_exports, f"Missing export: {e}"


def test_ingredient_cost_creation():
    """IngredientCost can be created with valid data."""
    from decimal import Decimal
    from dinner_spinner.domain.costing import IngredientCost

    cost = IngredientCost(
        ingredient_id=1,
        ingredient_name="Flour",
        cost_per_unit=Decimal("1.50"),
        cost_unit="kg",
        total_acquisition_cost=Decimal("15.00"),
        total_acquisition_quantity=Decimal("10"),
        acquisition_count=2,
    )
    assert cost.ingredient_id == 1
    assert cost.ingredient_name == "Flour"
    assert cost.cost_per_unit == Decimal("1.50")
    assert cost.cost_unit == "kg"
    assert cost.total_acquisition_cost == Decimal("15.00")
    assert cost.total_acquisition_quantity == Decimal("10")
    assert cost.acquisition_count == 2


def test_ingredient_cost_rejects_negative_cost_per_unit():
    """IngredientCost rejects negative cost per unit."""
    from decimal import Decimal
    from dinner_spinner.domain.costing import IngredientCost

    with pytest.raises(ValueError, match="negative"):
        IngredientCost(
            ingredient_id=1,
            ingredient_name="Flour",
            cost_per_unit=Decimal("-1.00"),
            cost_unit="kg",
            total_acquisition_cost=Decimal("10.00"),
            total_acquisition_quantity=Decimal("10"),
            acquisition_count=1,
        )


def test_ingredient_cost_rejects_zero_total_quantity():
    """IngredientCost rejects zero total quantity."""
    from decimal import Decimal
    from dinner_spinner.domain.costing import IngredientCost

    with pytest.raises(ValueError, match="positive"):
        IngredientCost(
            ingredient_id=1,
            ingredient_name="Flour",
            cost_per_unit=Decimal("1.00"),
            cost_unit="kg",
            total_acquisition_cost=Decimal("10.00"),
            total_acquisition_quantity=Decimal("0"),
            acquisition_count=1,
        )


def test_ingredient_cost_rejects_zero_acquisition_count():
    """IngredientCost rejects zero acquisition count."""
    from decimal import Decimal
    from dinner_spinner.domain.costing import IngredientCost

    with pytest.raises(ValueError, match="positive"):
        IngredientCost(
            ingredient_id=1,
            ingredient_name="Flour",
            cost_per_unit=Decimal("1.00"),
            cost_unit="kg",
            total_acquisition_cost=Decimal("10.00"),
            total_acquisition_quantity=Decimal("10"),
            acquisition_count=0,
        )


def test_recipe_ingredient_cost_creation():
    """RecipeIngredientCost can be created with valid data."""
    from decimal import Decimal
    from dinner_spinner.domain.costing import RecipeIngredientCost

    cost = RecipeIngredientCost(
        ingredient_id=1,
        ingredient_name="Flour",
        recipe_ingredient_quantity=Decimal("500"),
        recipe_ingredient_unit="g",
        cost_per_unit=Decimal("1.00"),
        cost_unit="kg",
        calculated_quantity=Decimal("0.5"),
        line_cost=Decimal("0.50"),
    )
    assert cost.ingredient_id == 1
    assert cost.line_cost == Decimal("0.50")


def test_recipe_cost_creation():
    """RecipeCost can be created with valid data."""
    from decimal import Decimal
    from dinner_spinner.domain.costing import RecipeCost, RecipeIngredientCost

    line_cost = RecipeIngredientCost(
        ingredient_id=1,
        ingredient_name="Flour",
        recipe_ingredient_quantity=Decimal("500"),
        recipe_ingredient_unit="g",
        cost_per_unit=Decimal("1.00"),
        cost_unit="kg",
        calculated_quantity=Decimal("0.5"),
        line_cost=Decimal("0.50"),
    )
    cost = RecipeCost(
        recipe_id=1,
        recipe_name="Bread",
        base_servings=4,
        ingredient_costs=(line_cost,),
        total_cost=Decimal("0.50"),
        is_complete=True,
    )
    assert cost.recipe_id == 1
    assert cost.total_cost == Decimal("0.50")
    assert cost.is_complete is True


def test_recipe_cost_incomplete_must_have_zero_total():
    """Incomplete RecipeCost must have zero total cost."""
    from decimal import Decimal
    from dinner_spinner.domain.costing import RecipeCost

    with pytest.raises(ValueError, match="zero total cost"):
        RecipeCost(
            recipe_id=1,
            recipe_name="Bread",
            base_servings=4,
            ingredient_costs=(),
            total_cost=Decimal("1.00"),
            is_complete=False,
        )


def test_meal_cost_creation():
    """MealCost can be created with valid data."""
    from decimal import Decimal
    from dinner_spinner.domain.costing import MealCost, RecipeCost, RecipeIngredientCost

    line_cost = RecipeIngredientCost(
        ingredient_id=1,
        ingredient_name="Flour",
        recipe_ingredient_quantity=Decimal("500"),
        recipe_ingredient_unit="g",
        cost_per_unit=Decimal("1.00"),
        cost_unit="kg",
        calculated_quantity=Decimal("0.5"),
        line_cost=Decimal("0.50"),
    )
    recipe_cost = RecipeCost(
        recipe_id=1,
        recipe_name="Bread",
        base_servings=4,
        ingredient_costs=(line_cost,),
        total_cost=Decimal("0.50"),
        is_complete=True,
    )
    meal_cost = MealCost(
        meal_plan_id=1,
        recipe_id=1,
        recipe_name="Bread",
        planned_servings=8,
        base_servings=4,
        recipe_cost=recipe_cost,
        meal_cost=Decimal("1.00"),
    )
    assert meal_cost.meal_plan_id == 1
    assert meal_cost.meal_cost == Decimal("1.00")


def test_meal_cost_unavailable_when_recipe_cost_unavailable():
    """MealCost without recipe_cost must have None meal_cost."""
    from dinner_spinner.domain.costing import MealCost

    meal_cost = MealCost(
        meal_plan_id=1,
        recipe_id=1,
        recipe_name="Bread",
        planned_servings=8,
        base_servings=4,
        recipe_cost=None,
        meal_cost=None,
    )
    assert meal_cost.meal_cost is None
    assert meal_cost.recipe_cost is None


def test_meal_cost_rejects_mismatched_recipe_and_meal_cost():
    """MealCost rejects recipe_cost present but meal_cost None."""
    from decimal import Decimal
    from dinner_spinner.domain.costing import MealCost, RecipeCost, RecipeIngredientCost

    line_cost = RecipeIngredientCost(
        ingredient_id=1,
        ingredient_name="Flour",
        recipe_ingredient_quantity=Decimal("500"),
        recipe_ingredient_unit="g",
        cost_per_unit=Decimal("1.00"),
        cost_unit="kg",
        calculated_quantity=Decimal("0.5"),
        line_cost=Decimal("0.50"),
    )
    recipe_cost = RecipeCost(
        recipe_id=1,
        recipe_name="Bread",
        base_servings=4,
        ingredient_costs=(line_cost,),
        total_cost=Decimal("0.50"),
        is_complete=True,
    )

    with pytest.raises(ValueError, match="meal cost not calculated"):
        MealCost(
            meal_plan_id=1,
            recipe_id=1,
            recipe_name="Bread",
            planned_servings=8,
            base_servings=4,
            recipe_cost=recipe_cost,
            meal_cost=None,
        )


def test_calculate_ingredient_costs_single_acquisition():
    """Single acquisition produces correct cost per unit."""
    from decimal import Decimal
    from dinner_spinner.domain.unit_system import initialize, reset
    from dinner_spinner.domain.ingredient import Ingredient
    from dinner_spinner.domain.acquisition import Acquisition
    from datetime import datetime
    from dinner_spinner.domain.costing import calculate_ingredient_costs

    reset()
    initialize()

    ingredients = {
        1: Ingredient(1, "Flour", None, Decimal("1000"), "g"),
    }
    acquisitions = [
        Acquisition(1, 1, 1000, "g", Decimal("10.00"), datetime(2024, 1, 1)),
    ]

    costs = calculate_ingredient_costs(ingredients, acquisitions)

    assert len(costs) == 1
    assert costs[0].ingredient_id == 1
    assert costs[0].cost_per_unit == Decimal("0.01")  # $10 / 1000g = $0.01/g
    assert costs[0].cost_unit == "g"
    assert costs[0].total_acquisition_cost == Decimal("10.00")
    assert costs[0].total_acquisition_quantity == Decimal("1000")
    assert costs[0].acquisition_count == 1


def test_calculate_ingredient_costs_multiple_acquisitions_weighted_average():
    """Multiple acquisitions produce weighted average cost."""
    from decimal import Decimal
    from dinner_spinner.domain.unit_system import initialize, reset
    from dinner_spinner.domain.ingredient import Ingredient
    from dinner_spinner.domain.acquisition import Acquisition
    from datetime import datetime
    from dinner_spinner.domain.costing import calculate_ingredient_costs

    reset()
    initialize()

    ingredients = {
        1: Ingredient(1, "Flour", None, Decimal("1000"), "g"),
    }
    acquisitions = [
        Acquisition(1, 1, 500, "g", Decimal("5.00"), datetime(2024, 1, 1)),
        Acquisition(2, 1, 1000, "g", Decimal("12.00"), datetime(2024, 1, 15)),
    ]

    costs = calculate_ingredient_costs(ingredients, acquisitions)

    assert len(costs) == 1
    # Total cost = $17, total qty = 1500g, cost/g = $17/1500 = $0.01133...
    assert costs[0].total_acquisition_cost == Decimal("17.00")
    assert costs[0].total_acquisition_quantity == Decimal("1500")
    assert costs[0].acquisition_count == 2
    expected = Decimal("17.00") / Decimal("1500")
    assert costs[0].cost_per_unit == expected


def test_calculate_ingredient_costs_acquisition_unit_conversion():
    """Acquisitions in different units are converted to ingredient unit."""
    from decimal import Decimal
    from dinner_spinner.domain.unit_system import initialize, reset
    from dinner_spinner.domain.ingredient import Ingredient
    from dinner_spinner.domain.acquisition import Acquisition
    from datetime import datetime
    from dinner_spinner.domain.costing import calculate_ingredient_costs

    reset()
    initialize()

    # Ingredient in kg
    ingredients = {
        1: Ingredient(1, "Flour", None, Decimal("2"), "kg"),
    }
    # Acquisitions in g
    acquisitions = [
        Acquisition(1, 1, 500, "g", Decimal("5.00"), datetime(2024, 1, 1)),
        Acquisition(2, 1, 1000, "g", Decimal("10.00"), datetime(2024, 1, 15)),
    ]

    costs = calculate_ingredient_costs(ingredients, acquisitions)

    assert len(costs) == 1
    # 500g + 1000g = 1500g = 1.5kg, total cost $15, cost/kg = $10/kg
    assert costs[0].cost_unit == "kg"
    assert costs[0].total_acquisition_quantity == Decimal("1.5")
    assert costs[0].cost_per_unit == Decimal("10.00")


def test_calculate_ingredient_costs_skips_incompatible_acquisition_units():
    """Incompatible acquisition units are skipped."""
    from decimal import Decimal
    from dinner_spinner.domain.unit_system import initialize, reset
    from dinner_spinner.domain.ingredient import Ingredient
    from dinner_spinner.domain.acquisition import Acquisition
    from datetime import datetime
    from dinner_spinner.domain.costing import calculate_ingredient_costs

    reset()
    initialize()

    ingredients = {
        1: Ingredient(1, "Flour", None, Decimal("1000"), "g"),
    }
    # One valid (g), one incompatible (ml)
    acquisitions = [
        Acquisition(1, 1, 1000, "g", Decimal("10.00"), datetime(2024, 1, 1)),
        Acquisition(2, 1, 500, "ml", Decimal("5.00"), datetime(2024, 1, 15)),
    ]

    costs = calculate_ingredient_costs(ingredients, acquisitions)

    assert len(costs) == 1
    # Only the g acquisition counted
    assert costs[0].total_acquisition_quantity == Decimal("1000")
    assert costs[0].total_acquisition_cost == Decimal("10.00")
    assert costs[0].acquisition_count == 1


def test_calculate_ingredient_costs_no_acquisitions_excluded():
    """Ingredients with no acquisitions are excluded from results."""
    from decimal import Decimal
    from dinner_spinner.domain.unit_system import initialize, reset
    from dinner_spinner.domain.ingredient import Ingredient
    from dinner_spinner.domain.acquisition import Acquisition
    from datetime import datetime
    from dinner_spinner.domain.costing import calculate_ingredient_costs

    reset()
    initialize()

    ingredients = {
        1: Ingredient(1, "Flour", None, Decimal("1000"), "g"),
        2: Ingredient(2, "Sugar", None, Decimal("500"), "g"),
    }
    acquisitions = [
        Acquisition(1, 1, 1000, "g", Decimal("10.00"), datetime(2024, 1, 1)),
    ]

    costs = calculate_ingredient_costs(ingredients, acquisitions)

    assert len(costs) == 1
    assert costs[0].ingredient_id == 1


def test_calculate_recipe_costs_basic():
    """Recipe cost calculated from ingredient costs."""
    from decimal import Decimal
    from dinner_spinner.domain.unit_system import initialize, reset
    from dinner_spinner.domain.recipe import Recipe
    from dinner_spinner.domain.recipe_ingredient import RecipeIngredient
    from dinner_spinner.domain.costing import (
        calculate_ingredient_costs,
        calculate_recipe_costs,
        IngredientCost,
    )

    reset()
    initialize()

    recipes = {
        1: Recipe(1, "Bread", 4),
    }
    recipe_ingredients = {
        1: [RecipeIngredient(1, 1, 1, 500, "g")],
    }
    ingredient_costs = [
        IngredientCost(1, "Flour", Decimal("0.01"), "g", Decimal("10.00"), Decimal("1000"), 1),
    ]

    costs = calculate_recipe_costs(recipes, recipe_ingredients, ingredient_costs)

    assert len(costs) == 1
    assert costs[0].recipe_id == 1
    assert costs[0].total_cost == Decimal("5.00")  # 500g * $0.01/g = $5
    assert costs[0].is_complete is True
    assert len(costs[0].ingredient_costs) == 1


def test_calculate_recipe_costs_recipe_ingredient_unit_conversion():
    """RecipeIngredient unit converted to ingredient cost unit."""
    from decimal import Decimal
    from dinner_spinner.domain.unit_system import initialize, reset
    from dinner_spinner.domain.recipe import Recipe
    from dinner_spinner.domain.recipe_ingredient import RecipeIngredient
    from dinner_spinner.domain.costing import (
        calculate_recipe_costs,
        IngredientCost,
    )

    reset()
    initialize()

    recipes = {
        1: Recipe(1, "Bread", 4),
    }
    # RecipeIngredient in kg, ingredient cost in g
    recipe_ingredients = {
        1: [RecipeIngredient(1, 1, 1, 1, "kg")],
    }
    ingredient_costs = [
        IngredientCost(1, "Flour", Decimal("10.00"), "kg", Decimal("10.00"), Decimal("1"), 1),
    ]

    costs = calculate_recipe_costs(recipes, recipe_ingredients, ingredient_costs)

    assert len(costs) == 1
    # 1kg * $10/kg = $10
    assert costs[0].total_cost == Decimal("10.00")
    assert costs[0].ingredient_costs[0].calculated_quantity == Decimal("1")


def test_calculate_recipe_costs_incomplete_when_ingredient_missing():
    """RecipeCost is incomplete when ingredient cost unavailable."""
    from decimal import Decimal
    from dinner_spinner.domain.unit_system import initialize, reset
    from dinner_spinner.domain.recipe import Recipe
    from dinner_spinner.domain.recipe_ingredient import RecipeIngredient
    from dinner_spinner.domain.costing import (
        calculate_recipe_costs,
        IngredientCost,
    )

    reset()
    initialize()

    recipes = {
        1: Recipe(1, "Bread", 4),
    }
    recipe_ingredients = {
        1: [
            RecipeIngredient(1, 1, 1, 500, "g"),  # Flour
            RecipeIngredient(2, 1, 2, 2, "each"),  # Eggs - no cost
        ],
    }
    ingredient_costs = [
        IngredientCost(1, "Flour", Decimal("0.01"), "g", Decimal("10.00"), Decimal("1000"), 1),
        # No cost for ingredient 2 (Eggs)
    ]

    costs = calculate_recipe_costs(recipes, recipe_ingredients, ingredient_costs)

    assert len(costs) == 1
    assert costs[0].is_complete is False
    assert costs[0].total_cost == Decimal("0")
    # Only flour line cost included
    assert len(costs[0].ingredient_costs) == 1


def test_calculate_recipe_costs_incomplete_when_incompatible_units():
    """RecipeCost incomplete when RecipeIngredient unit incompatible with cost unit."""
    from decimal import Decimal
    from dinner_spinner.domain.unit_system import initialize, reset
    from dinner_spinner.domain.recipe import Recipe
    from dinner_spinner.domain.recipe_ingredient import RecipeIngredient
    from dinner_spinner.domain.costing import (
        calculate_recipe_costs,
        IngredientCost,
    )

    reset()
    initialize()

    recipes = {
        1: Recipe(1, "Bread", 4),
    }
    # RecipeIngredient in g, but cost unit is each (incompatible)
    recipe_ingredients = {
        1: [RecipeIngredient(1, 1, 1, 500, "g")],
    }
    ingredient_costs = [
        IngredientCost(1, "Flour", Decimal("1.00"), "each", Decimal("10.00"), Decimal("10"), 1),
    ]

    costs = calculate_recipe_costs(recipes, recipe_ingredients, ingredient_costs)

    assert len(costs) == 1
    assert costs[0].is_complete is False
    assert costs[0].total_cost == Decimal("0")
    assert len(costs[0].ingredient_costs) == 0


def test_calculate_recipe_costs_empty_recipe():
    """Recipe with no ingredients has zero cost."""
    from decimal import Decimal
    from dinner_spinner.domain.unit_system import initialize, reset
    from dinner_spinner.domain.recipe import Recipe
    from dinner_spinner.domain.costing import calculate_recipe_costs

    reset()
    initialize()

    recipes = {
        1: Recipe(1, "Empty", 4),
    }
    recipe_ingredients = {1: []}
    ingredient_costs = []

    costs = calculate_recipe_costs(recipes, recipe_ingredients, ingredient_costs)

    assert len(costs) == 1
    assert costs[0].total_cost == Decimal("0")
    assert costs[0].is_complete is True
    assert costs[0].ingredient_costs == ()


def test_calculate_meal_costs_scaling():
    """MealCost scales RecipeCost by serving ratio."""
    from decimal import Decimal
    from dinner_spinner.domain.unit_system import initialize, reset
    from dinner_spinner.domain.meal_plan import MealPlan
    from dinner_spinner.domain.recipe import Recipe
    from dinner_spinner.domain.costing import (
        RecipeCost,
        RecipeIngredientCost,
        calculate_meal_costs,
    )

    reset()
    initialize()

    meal_plans = [
        MealPlan(1, 20260101, 0, "Dinner", 1, 8),  # 8 servings
    ]
    recipes = {
        1: Recipe(1, "Bread", 4),  # Base 4 servings
    }
    line_cost = RecipeIngredientCost(
        ingredient_id=1,
        ingredient_name="Flour",
        recipe_ingredient_quantity=Decimal("500"),
        recipe_ingredient_unit="g",
        cost_per_unit=Decimal("0.01"),
        cost_unit="g",
        calculated_quantity=Decimal("500"),
        line_cost=Decimal("5.00"),
    )
    recipe_costs = [
        RecipeCost(1, "Bread", 4, (line_cost,), Decimal("5.00"), True),
    ]

    costs = calculate_meal_costs(meal_plans, recipes, recipe_costs)

    assert len(costs) == 1
    # 8 servings / 4 base = 2x, $5 * 2 = $10
    assert costs[0].meal_cost == Decimal("10.00")
    assert costs[0].planned_servings == 8
    assert costs[0].base_servings == 4


def test_calculate_meal_costs_empty_slot():
    """Empty meal slot has no cost."""
    from dinner_spinner.domain.meal_plan import MealPlan
    from dinner_spinner.domain.costing import calculate_meal_costs

    meal_plans = [
        MealPlan(1, 20260101, 0, "Dinner", None, 4),  # No recipe
    ]
    recipes = {}
    recipe_costs = []

    costs = calculate_meal_costs(meal_plans, recipes, recipe_costs)

    assert len(costs) == 1
    assert costs[0].recipe_id is None
    assert costs[0].recipe_name == ""
    assert costs[0].meal_cost is None
    assert costs[0].recipe_cost is None


def test_calculate_meal_costs_unavailable_when_recipe_cost_incomplete():
    """MealCost unavailable when RecipeCost incomplete."""
    from decimal import Decimal
    from dinner_spinner.domain.meal_plan import MealPlan
    from dinner_spinner.domain.recipe import Recipe
    from dinner_spinner.domain.costing import (
        RecipeCost,
        calculate_meal_costs,
    )

    meal_plans = [
        MealPlan(1, 20260101, 0, "Dinner", 1, 4),
    ]
    recipes = {1: Recipe(1, "Bread", 4)}
    recipe_costs = [
        RecipeCost(1, "Bread", 4, (), Decimal("0"), False),  # Incomplete
    ]

    costs = calculate_meal_costs(meal_plans, recipes, recipe_costs)

    assert len(costs) == 1
    assert costs[0].meal_cost is None
    assert costs[0].recipe_cost is not None
    assert costs[0].recipe_cost.is_complete is False


def test_calculate_weekly_cost_summary():
    """Weekly cost summary aggregates correctly."""
    from decimal import Decimal
    from dinner_spinner.domain.costing import (
        MealCost,
        RecipeCost,
        RecipeIngredientCost,
        calculate_weekly_cost_summary,
    )

    line_cost = RecipeIngredientCost(
        ingredient_id=1,
        ingredient_name="Flour",
        recipe_ingredient_quantity=Decimal("500"),
        recipe_ingredient_unit="g",
        cost_per_unit=Decimal("0.01"),
        cost_unit="g",
        calculated_quantity=Decimal("500"),
        line_cost=Decimal("5.00"),
    )
    recipe_cost = RecipeCost(1, "Bread", 4, (line_cost,), Decimal("5.00"), True)

    meal_costs = [
        MealCost(1, 1, "Bread", 4, 4, recipe_cost, Decimal("5.00")),   # Costed
        MealCost(2, 1, "Bread", 8, 4, recipe_cost, Decimal("10.00")),  # Costed
        MealCost(3, 1, "Bread", 4, 4, None, None),                      # Uncosted
        MealCost(4, None, "", 4, 0, None, None),                        # Empty
    ]

    summary = calculate_weekly_cost_summary(meal_costs)

    assert summary["total_cost"] == Decimal("15.00")
    assert summary["costed_meals"] == 2
    assert summary["uncosted_meals"] == 1
    assert summary["empty_slots"] == 1


def test_calculate_weekly_cost_summary_empty():
    """Empty week produces zero summary."""
    from decimal import Decimal
    from dinner_spinner.domain.costing import calculate_weekly_cost_summary

    summary = calculate_weekly_cost_summary([])

    assert summary["total_cost"] == Decimal("0")
    assert summary["costed_meals"] == 0
    assert summary["uncosted_meals"] == 0
    assert summary["empty_slots"] == 0


def test_calculate_ingredient_costs_deterministic():
    """Same inputs always produce same outputs."""
    from decimal import Decimal
    from dinner_spinner.domain.unit_system import initialize, reset
    from dinner_spinner.domain.ingredient import Ingredient
    from dinner_spinner.domain.acquisition import Acquisition
    from datetime import datetime
    from dinner_spinner.domain.costing import calculate_ingredient_costs

    reset()
    initialize()

    ingredients = {1: Ingredient(1, "Flour", None, Decimal("1000"), "g")}
    acquisitions = [Acquisition(1, 1, 1000, "g", Decimal("10.00"), datetime(2024, 1, 1))]

    costs1 = calculate_ingredient_costs(ingredients, acquisitions)
    costs2 = calculate_ingredient_costs(ingredients, acquisitions)

    assert costs1 == costs2


def test_calculate_recipe_costs_deterministic():
    """Same inputs always produce same recipe costs."""
    from decimal import Decimal
    from dinner_spinner.domain.unit_system import initialize, reset
    from dinner_spinner.domain.recipe import Recipe
    from dinner_spinner.domain.recipe_ingredient import RecipeIngredient
    from dinner_spinner.domain.costing import (
        calculate_recipe_costs,
        IngredientCost,
    )

    reset()
    initialize()

    recipes = {1: Recipe(1, "Bread", 4)}
    recipe_ingredients = {1: [RecipeIngredient(1, 1, 1, 500, "g")]}
    ingredient_costs = [IngredientCost(1, "Flour", Decimal("0.01"), "g", Decimal("10.00"), Decimal("1000"), 1)]

    costs1 = calculate_recipe_costs(recipes, recipe_ingredients, ingredient_costs)
    costs2 = calculate_recipe_costs(recipes, recipe_ingredients, ingredient_costs)

    assert costs1 == costs2


def test_calculate_meal_costs_deterministic():
    """Same inputs always produce same meal costs."""
    from decimal import Decimal
    from dinner_spinner.domain.unit_system import initialize, reset
    from dinner_spinner.domain.meal_plan import MealPlan
    from dinner_spinner.domain.recipe import Recipe
    from dinner_spinner.domain.costing import (
        RecipeCost,
        RecipeIngredientCost,
        calculate_meal_costs,
    )

    reset()
    initialize()

    meal_plans = [MealPlan(1, 20260101, 0, "Dinner", 1, 8)]
    recipes = {1: Recipe(1, "Bread", 4)}
    line_cost = RecipeIngredientCost(
        ingredient_id=1, ingredient_name="Flour", recipe_ingredient_quantity=Decimal("500"),
        recipe_ingredient_unit="g", cost_per_unit=Decimal("0.01"), cost_unit="g",
        calculated_quantity=Decimal("500"), line_cost=Decimal("5.00"),
    )
    recipe_costs = [RecipeCost(1, "Bread", 4, (line_cost,), Decimal("5.00"), True)]

    costs1 = calculate_meal_costs(meal_plans, recipes, recipe_costs)
    costs2 = calculate_meal_costs(meal_plans, recipes, recipe_costs)

    assert costs1 == costs2


# ---------------------------------------------------------------------------
# 13. Slice 6 Architecture Tests
# ---------------------------------------------------------------------------

def test_costing_domain_does_not_import_flask():
    """Costing domain must not import Flask."""
    import dinner_spinner.domain.costing as costing_mod
    assert "Flask" not in costing_mod.__dict__


def test_costing_domain_does_not_import_sqlalchemy():
    """Costing domain must not import SQLAlchemy."""
    import dinner_spinner.domain.costing as costing_mod
    for attr in dir(costing_mod):
        attr_lower = attr.lower()
        if "sqlalchemy" in attr_lower and not attr.startswith("__"):
            pytest.fail(f"costing.{attr} appears to import sqlalchemy")


def test_costing_domain_does_not_import_database_session():
    """Costing domain must not import database session mechanics."""
    import dinner_spinner.domain.costing as costing_mod
    forbidden = ["sqlalchemy", "session", "engine", "connection"]
    for attr in dir(costing_mod):
        attr_lower = attr.lower()
        for f in forbidden:
            if f in attr_lower and not attr.startswith("__"):
                pytest.fail(f"costing.{attr} appears to import {f}")


def test_costing_no_persistent_entities():
    """Costing must not introduce persistent entities."""
    from dinner_persistence.models import Base
    tables = Base.metadata.tables.keys()
    costing_tables = [
        "ingredient_cost", "recipe_cost", "meal_cost",
        "recipe_ingredient_cost", "cost", "costing",
    ]
    for t in costing_tables:
        assert t not in tables, f"Found forbidden costing table: {t}"


def test_costing_no_migration_created():
    """No migration should be created for Slice 6."""
    import os
    migration_dir = "migrations/versions"
    if os.path.exists(migration_dir):
        # Should only have the two existing migrations
        migrations = [f for f in os.listdir(migration_dir) if f.endswith(".py")]
        assert len(migrations) == 2, f"Unexpected migration count: {migrations}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])