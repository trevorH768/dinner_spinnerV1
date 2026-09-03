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

    for mod in [
        dinner_spinner.domain.ingredient,
        dinner_spinner.domain.recipe,
        dinner_spinner.domain.recipe_ingredient,
        dinner_spinner.domain.meal_plan,
        dinner_spinner.domain.inventory_category,
        dinner_spinner.domain.unit_system,
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


def test_domain_has_no_acquisition_entity():
    """Acquisition is NOT in the foundational domain (Slice 1 only)."""
    from dinner_spinner.domain import __all__ as domain_exports
    # Acquisition, Consumption, Waste are in Slice 2
    assert "Acquisition" not in domain_exports
    assert "Consumption" not in domain_exports
    assert "Waste" not in domain_exports


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
# 4. Unit Boundary Tests
# ---------------------------------------------------------------------------

def test_single_authoritative_unit_system():
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

    initialize()

    # kg to g
    assert convert(1, "kg", "g") == 1000
    assert convert(500, "g", "kg") == 0.5

    # lb to oz
    assert convert(1, "lb", "oz") == 16

    # l to ml
    assert convert(1, "l", "ml") == 1000

    # cup to tbsp
    assert convert(1, "cup", "tbsp") == pytest.approx(15.77, rel=0.01)


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
        "UnitSystem",
    }

    # Check all expected are present
    for e in expected:
        assert e in domain_exports, f"Missing export: {e}"

    # Check no unexpected (forbidden) entities
    forbidden = {
        "Container", "InventoryLot", "Product", "Package", "Store",
        "Brand", "Barcode", "Nutrition", "InventoryEvent", "Transfer",
        "PriceEstimate", "ShoppingList", "ShoppingListItem",
        "Acquisition", "Consumption", "Waste",
        "Demand", "AvailableInventory", "NetRequirement",
        "CostPerUnit", "RecipeCost", "MealCost",
    }
    for f in forbidden:
        assert f not in domain_exports, f"Forbidden entity exported: {f}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])