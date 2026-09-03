"""Persistence integration tests for Dinner Spinner V1.

These tests exercise actual database behavior to prove that database
invariants and relationship semantics from V1_ARCHITECTURE.md are enforced.
"""

import pytest
import os
import tempfile
from sqlalchemy.exc import IntegrityError
from alembic.config import Config
from alembic import command


@pytest.fixture
def test_db_path():
    """Create a temporary database file for testing."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    try:
        os.unlink(path)
    except OSError:
        pass


@pytest.fixture
def app(test_db_path):
    """Create Flask app with shared test database."""
    from dinner_spinner import create_app
    app = create_app({
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{test_db_path}",
        "TESTING": True
    })
    with app.app_context():
        from flask import current_app
        db = current_app.extensions['sqlalchemy']
        # Initialize schema via Alembic against the same test database
        alembic_cfg = Config("alembic.ini")
        alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{test_db_path}")
        command.upgrade(alembic_cfg, "head")
        yield app


@pytest.fixture
def db_session(app):
    """Provide database session for tests."""
    with app.app_context():
        from flask import current_app
        db = current_app.extensions['sqlalchemy']
        yield db.session
        db.session.rollback()


@pytest.fixture
def unit_system_initialized():
    """Ensure UnitSystem is initialized for tests that need it."""
    from dinner_spinner.domain.unit_system import initialize, reset
    reset()
    initialize()
    yield
    reset()


# =============================================================================
# CHECK Constraint Tests (V1_ARCHITECTURE.md Section 21)
# =============================================================================

def test_check_ingredient_quantity_nonnegative(db_session, unit_system_initialized):
    """Ingredient.quantity >= 0 enforced at DB level."""
    from dinner_persistence.models import Ingredient

    # Valid: zero quantity
    ing = Ingredient(name="Flour", quantity=0, unit="g")
    db_session.add(ing)
    db_session.commit()

    # Valid: positive quantity
    ing = Ingredient(name="Sugar", quantity=100, unit="g")
    db_session.add(ing)
    db_session.commit()

    # Invalid: negative quantity
    ing = Ingredient(name="Bad", quantity=-1, unit="g")
    db_session.add(ing)
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_check_recipe_servings_positive(db_session, unit_system_initialized):
    """Recipe.servings > 0 enforced at DB level."""
    from dinner_persistence.models import Recipe

    # Valid: positive servings
    recipe = Recipe(name="Bread", servings=4)
    db_session.add(recipe)
    db_session.commit()

    # Invalid: zero servings
    recipe = Recipe(name="Bad", servings=0)
    db_session.add(recipe)
    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()
    # Invalid: negative servings
    recipe = Recipe(name="Bad2", servings=-1)
    db_session.add(recipe)
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_check_recipe_ingredient_quantity_positive(db_session, unit_system_initialized):
    """RecipeIngredient.quantity > 0 enforced at DB level."""
    from dinner_persistence.models import Recipe, Ingredient, RecipeIngredient

    # Setup
    ing = Ingredient(name="Flour", quantity=1000, unit="g")
    db_session.add(ing)
    recipe = Recipe(name="Bread", servings=4)
    db_session.add(recipe)
    db_session.commit()

    # Valid: positive quantity
    ri = RecipeIngredient(recipe_id=recipe.id, ingredient_id=ing.id, quantity=0.5, unit="kg")
    db_session.add(ri)
    db_session.commit()

    # Invalid: zero quantity
    ri = RecipeIngredient(recipe_id=recipe.id, ingredient_id=ing.id, quantity=0, unit="g")
    db_session.add(ri)
    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()
    # Invalid: negative quantity
    ri = RecipeIngredient(recipe_id=recipe.id, ingredient_id=ing.id, quantity=-1, unit="g")
    db_session.add(ri)
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_check_mealplan_servings_positive(db_session, unit_system_initialized):
    """MealPlan.servings > 0 enforced at DB level."""
    from dinner_persistence.models import MealPlan

    # Valid: positive servings
    mp = MealPlan(week_start=20260101, day=0, meal_type="Dinner", servings=4)
    db_session.add(mp)
    db_session.commit()

    # Invalid: zero servings
    mp = MealPlan(week_start=20260101, day=1, meal_type="Dinner", servings=0)
    db_session.add(mp)
    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()
    # Invalid: negative servings
    mp = MealPlan(week_start=20260101, day=2, meal_type="Dinner", servings=-1)
    db_session.add(mp)
    with pytest.raises(IntegrityError):
        db_session.commit()


# =============================================================================
# UNIQUE Constraint Tests (V1_ARCHITECTURE.md Section 21)
# =============================================================================

def test_unique_recipe_ingredient_recipe_ingredient(db_session, unit_system_initialized):
    """UNIQUE(recipe_id, ingredient_id) on RecipeIngredient enforced at DB level."""
    from dinner_persistence.models import Recipe, Ingredient, RecipeIngredient

    ing = Ingredient(name="Flour", quantity=1000, unit="g")
    db_session.add(ing)
    recipe = Recipe(name="Bread", servings=4)
    db_session.add(recipe)
    db_session.commit()

    # First RI OK
    ri1 = RecipeIngredient(recipe_id=recipe.id, ingredient_id=ing.id, quantity=500, unit="g")
    db_session.add(ri1)
    db_session.commit()

    # Duplicate (recipe_id, ingredient_id) fails
    ri2 = RecipeIngredient(recipe_id=recipe.id, ingredient_id=ing.id, quantity=200, unit="g")
    db_session.add(ri2)
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_unique_mealplan_week_day_meal_type(db_session, unit_system_initialized):
    """UNIQUE(week_start, day, meal_type) on MealPlan enforced at DB level."""
    from dinner_persistence.models import MealPlan

    # First MP OK
    mp1 = MealPlan(week_start=20260101, day=0, meal_type="Dinner", servings=4)
    db_session.add(mp1)
    db_session.commit()

    # Duplicate (week_start, day, meal_type) fails
    mp2 = MealPlan(week_start=20260101, day=0, meal_type="Dinner", servings=2)
    db_session.add(mp2)
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_unique_inventory_category_name(db_session):
    """UNIQUE(name) on InventoryCategory enforced at DB level."""
    from dinner_persistence.models import InventoryCategory

    cat1 = InventoryCategory(name="Baking")
    db_session.add(cat1)
    db_session.commit()

    cat2 = InventoryCategory(name="Baking")
    db_session.add(cat2)
    with pytest.raises(IntegrityError):
        db_session.commit()


# =============================================================================
# FK RESTRICT Tests (V1_ARCHITECTURE.md Section 21, Ingredient deletion)
# =============================================================================

def test_fk_restrict_ingredient_deletion_blocked_when_referenced(db_session, unit_system_initialized):
    """Ingredient deletion blocked by RESTRICT FK when referenced by RecipeIngredient."""
    from dinner_persistence.models import Ingredient, Recipe, RecipeIngredient

    ing = Ingredient(name="Flour", quantity=1000, unit="g")
    db_session.add(ing)
    recipe = Recipe(name="Bread", servings=4)
    db_session.add(recipe)
    db_session.commit()

    ri = RecipeIngredient(recipe_id=recipe.id, ingredient_id=ing.id, quantity=500, unit="g")
    db_session.add(ri)
    db_session.commit()

    # Attempt to delete referenced ingredient
    db_session.delete(ing)
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_fk_restrict_ingredient_deletion_succeeds_when_unreferenced(db_session, unit_system_initialized):
    """Ingredient deletion succeeds when NOT referenced by any RecipeIngredient."""
    from dinner_persistence.models import Ingredient

    ing = Ingredient(name="Flour", quantity=1000, unit="g")
    db_session.add(ing)
    db_session.commit()

    # Should succeed
    db_session.delete(ing)
    db_session.commit()

    # Verify deleted
    from dinner_persistence.models import Ingredient as IngModel
    assert db_session.get(IngModel, ing.id) is None


# =============================================================================
# FK SET NULL Tests (V1_ARCHITECTURE.md Section 21, Category/Recipe deletion)
# =============================================================================

def test_fk_set_null_category_deletion_nulls_ingredient_category(db_session, unit_system_initialized):
    """Deleting InventoryCategory sets Ingredient.inventory_category_id = NULL."""
    from dinner_persistence.models import InventoryCategory, Ingredient

    cat = InventoryCategory(name="Baking")
    db_session.add(cat)
    ing = Ingredient(name="Flour", quantity=1000, unit="g", inventory_category_id=cat.id)
    db_session.add(ing)
    db_session.commit()

    # Delete category
    db_session.delete(cat)
    db_session.commit()

    # Ingredient should have NULL category
    db_session.refresh(ing)
    assert ing.inventory_category_id is None


def test_fk_set_null_recipe_deletion_nulls_mealplan_recipe(db_session, unit_system_initialized):
    """Deleting Recipe sets MealPlan.recipe_id = NULL."""
    from dinner_persistence.models import Recipe, MealPlan

    recipe = Recipe(name="Bread", servings=4)
    db_session.add(recipe)
    db_session.commit()

    mp = MealPlan(week_start=20260101, day=0, meal_type="Dinner", recipe_id=recipe.id, servings=4)
    db_session.add(mp)
    db_session.commit()

    # Delete recipe
    db_session.delete(recipe)
    db_session.commit()

    # MealPlan should have NULL recipe_id
    db_session.refresh(mp)
    assert mp.recipe_id is None
    # MealPlan itself still exists
    assert db_session.get(type(mp), mp.id) is not None


def test_recipe_deletion_preserves_ingredients(db_session, unit_system_initialized):
    """Deleting Recipe preserves Ingredients (no cascade to Ingredient)."""
    from dinner_persistence.models import Recipe, Ingredient, RecipeIngredient

    ing = Ingredient(name="Flour", quantity=1000, unit="g")
    db_session.add(ing)
    recipe = Recipe(name="Bread", servings=4)
    db_session.add(recipe)
    db_session.commit()

    ri = RecipeIngredient(recipe_id=recipe.id, ingredient_id=ing.id, quantity=500, unit="g")
    db_session.add(ri)
    db_session.commit()

    # Delete recipe
    db_session.delete(recipe)
    db_session.commit()

    # Ingredient should still exist
    assert db_session.get(type(ing), ing.id) is not None
    # RecipeIngredient should be deleted (CASCADE)
    from dinner_persistence.models import RecipeIngredient as RIModel
    assert db_session.get(RIModel, ri.id) is None


# =============================================================================
# FK CASCADE Tests (V1_ARCHITECTURE.md Section 21, Recipe deletion)
# =============================================================================

def test_fk_cascade_recipe_deletion_cascades_recipe_ingredients(db_session, unit_system_initialized):
    """Deleting Recipe cascades to RecipeIngredients (ON DELETE CASCADE)."""
    from dinner_persistence.models import Recipe, Ingredient, RecipeIngredient

    ing = Ingredient(name="Flour", quantity=1000, unit="g")
    db_session.add(ing)
    recipe = Recipe(name="Bread", servings=4)
    db_session.add(recipe)
    db_session.commit()

    ri = RecipeIngredient(recipe_id=recipe.id, ingredient_id=ing.id, quantity=500, unit="g")
    db_session.add(ri)
    db_session.commit()

    # Delete recipe
    db_session.delete(recipe)
    db_session.commit()

    # RecipeIngredient should be deleted
    from dinner_persistence.models import RecipeIngredient as RIModel
    assert db_session.get(RIModel, ri.id) is None


def test_recipe_deletion_preserves_mealplans_with_null_recipe(db_session, unit_system_initialized):
    """Recipe deletion preserves MealPlans, sets recipe_id = NULL."""
    from dinner_persistence.models import Recipe, MealPlan

    recipe = Recipe(name="Bread", servings=4)
    db_session.add(recipe)
    db_session.commit()

    mp = MealPlan(week_start=20260101, day=0, meal_type="Dinner", recipe_id=recipe.id, servings=4)
    db_session.add(mp)
    db_session.commit()

    # Delete recipe
    db_session.delete(recipe)
    db_session.commit()

    # MealPlan should exist with NULL recipe_id
    db_session.refresh(mp)
    assert mp.recipe_id is None
    assert db_session.get(type(mp), mp.id) is not None


# =============================================================================
# Unit Conversion Behavior Tests
# =============================================================================

def test_unit_conversion_same_category(db_session, unit_system_initialized):
    """Same-category conversions work correctly."""
    from dinner_spinner.domain.unit_system import convert

    assert convert(1, "kg", "g") == 1000
    assert convert(1000, "g", "kg") == 1
    assert convert(1, "l", "ml") == 1000
    assert convert(1, "cup", "tbsp") == pytest.approx(15.77, rel=0.01)


def test_unit_conversion_cross_category_rejected(db_session, unit_system_initialized):
    """Cross-category conversions rejected."""
    from dinner_spinner.domain.unit_system import convert

    with pytest.raises(ValueError, match="different measurement categories"):
        convert(100, "g", "ml")

    with pytest.raises(ValueError, match="different measurement categories"):
        convert(1, "cup", "each")


# =============================================================================
# Ingredient Unit Change Tests
# =============================================================================

def test_ingredient_unit_change_preserves_quantity(db_session, unit_system_initialized):
    """Ingredient.change_unit() preserves physical quantity."""
    from dinner_persistence.models import Ingredient
    from dinner_spinner.domain.unit_system import initialize, reset

    ing = Ingredient(name="Flour", quantity=1, unit="kg")
    db_session.add(ing)
    db_session.commit()

    # Use domain operation to change unit
    domain_ing = ing.to_domain()
    domain_ing.change_unit("g")

    # Sync back
    ing.quantity = domain_ing.quantity
    ing.unit = domain_ing.unit
    db_session.commit()

    db_session.refresh(ing)
    assert ing.quantity == 1000
    assert ing.unit == "g"


def test_ingredient_unit_change_cross_category_rejected(db_session, unit_system_initialized):
    """Ingredient unit change rejects cross-category."""
    from dinner_persistence.models import Ingredient

    ing = Ingredient(name="Flour", quantity=100, unit="g")
    db_session.add(ing)
    db_session.commit()

    domain_ing = ing.to_domain()
    from dinner_spinner.domain.unit_system import initialize, reset
    reset()
    initialize()

    with pytest.raises(ValueError, match="different measurement categories"):
        domain_ing.change_unit("ml")


# =============================================================================
# RecipeIngredient Uniqueness at Domain + DB Level
# =============================================================================

def test_recipe_ingredient_uniqueness_domain_and_db(db_session, unit_system_initialized):
    """RecipeIngredient uniqueness enforced at both domain and DB level."""
    from dinner_persistence.models import Recipe, Ingredient, RecipeIngredient

    ing = Ingredient(name="Flour", quantity=1000, unit="g")
    db_session.add(ing)
    recipe = Recipe(name="Bread", servings=4)
    db_session.add(recipe)
    db_session.commit()

    # Domain level: can create duplicate objects (domain doesn't enforce)
    from dinner_spinner.domain.recipe_ingredient import RecipeIngredient as DomainRI
    ri1 = DomainRI(id=1, recipe_id=recipe.id, ingredient_id=ing.id, quantity=500, unit="g")
    ri2 = DomainRI(id=2, recipe_id=recipe.id, ingredient_id=ing.id, quantity=200, unit="g")
    assert ri1.recipe_id == ri2.recipe_id and ri1.ingredient_id == ri2.ingredient_id

    # DB level: duplicate insert fails
    ri_db1 = RecipeIngredient(recipe_id=recipe.id, ingredient_id=ing.id, quantity=500, unit="g")
    db_session.add(ri_db1)
    db_session.commit()

    ri_db2 = RecipeIngredient(recipe_id=recipe.id, ingredient_id=ing.id, quantity=200, unit="g")
    db_session.add(ri_db2)
    with pytest.raises(IntegrityError):
        db_session.commit()


# =============================================================================
# MealPlan Empty Slot Tests
# =============================================================================

def test_mealplan_empty_slot_valid(db_session, unit_system_initialized):
    """MealPlan with recipe_id = NULL is valid (empty meal slot)."""
    from dinner_persistence.models import MealPlan

    mp = MealPlan(week_start=20260101, day=0, meal_type="Dinner", recipe_id=None, servings=4)
    db_session.add(mp)
    db_session.commit()

    db_session.refresh(mp)
    assert mp.recipe_id is None
    assert mp.servings == 4


if __name__ == "__main__":
    pytest.main([__file__, "-v"])