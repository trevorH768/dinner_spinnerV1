# =============================================================================
# Slice 5: Shopping List Tests
# =============================================================================

import pytest
import tempfile
import os
from datetime import datetime
from decimal import Decimal
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
        # Initialize schema via Alembic
        from alembic.config import Config
        from alembic import command
        alembic_cfg = Config("alembic.ini")
        alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{test_db_path}")
        command.upgrade(alembic_cfg, "head")
        yield app


@pytest.fixture
def app_without_init(test_db_path):
    """Create Flask app with shared test database."""
    from dinner_spinner import create_app
    app = create_app({
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{test_db_path}",
        "TESTING": True
    })
    with app.app_context():
        from flask import current_app
        db = current_app.extensions['sqlalchemy']
        # Initialize schema via Alembic
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
# Slice 5: Shopping List Tests
# =============================================================================


class TestShoppingListDomain:
    """Tests for the Shopping List domain logic."""

    def test_shopping_list_from_requirements(self, unit_system_initialized):
        """Shopping list is calculated from inventory requirements."""
        from dinner_spinner.domain.shopping_list import calculate_shopping_list
        from dinner_spinner.domain.inventory_requirement import IngredientRequirement
        from dinner_spinner.domain.unit_system import initialize, reset
        from decimal import Decimal

        reset()
        initialize()

        # Requirements with mixed net requirements
        requirements = [
            IngredientRequirement(
                ingredient_id=1, ingredient_name="Flour",
                demand_quantity=Decimal("2000"), demand_unit="g",
                available_quantity=Decimal("1000"), available_unit="g",
                net_requirement_quantity=Decimal("800"), net_requirement_unit="g"
            ),
            IngredientRequirement(
                ingredient_id=2, ingredient_name="Milk",
                demand_quantity=Decimal("250"), demand_unit="ml",
                available_quantity=Decimal("2000"), available_unit="ml",
                net_requirement_quantity=Decimal("0"), net_requirement_unit="ml"
            ),
            IngredientRequirement(
                ingredient_id=3, ingredient_name="Eggs",
                demand_quantity=Decimal("2"), demand_unit="each",
                available_quantity=Decimal("12"), available_unit="each",
                net_requirement_quantity=Decimal("0"), net_requirement_unit="each"
            ),
            IngredientRequirement(
                ingredient_id=4, ingredient_name="Sugar",
                demand_quantity=Decimal("1000"), demand_unit="g",
                available_quantity=Decimal("0"), available_unit="g",
                net_requirement_quantity=Decimal("1000"), net_requirement_unit="g"
            ),
        ]
        shopping_list = calculate_shopping_list(requirements)

        # Should only include items with positive net requirements
        assert len(shopping_list) == 2
        # Deterministic ordering: ingredient_name then ingredient_id
        assert shopping_list[0].ingredient_name == "Flour"
        assert shopping_list[0].quantity == 800
        assert shopping_list[0].unit == "g"
        assert shopping_list[1].ingredient_name == "Sugar"
        assert shopping_list[1].quantity == 1000
        assert shopping_list[1].unit == "g"

    def test_shopping_list_empty_when_no_requirements(self, unit_system_initialized):
        """Empty requirements produce empty shopping list."""
        from dinner_spinner.domain.shopping_list import calculate_shopping_list

        shopping_list = calculate_shopping_list([])
        assert len(shopping_list) == 0

    def test_shopping_list_deterministic_ordering(self, unit_system_initialized):
        """Shopping list has deterministic ordering (name then ID)."""
        from dinner_spinner.domain.shopping_list import calculate_shopping_list
        from dinner_spinner.domain.inventory_requirement import IngredientRequirement
        from decimal import Decimal

        requirements = [
            IngredientRequirement(
                ingredient_id=2, ingredient_name="Sugar",
                demand_quantity=Decimal("1000"), demand_unit="g",
                available_quantity=Decimal("0"), available_unit="g",
                net_requirement_quantity=Decimal("1000"), net_requirement_unit="g"
            ),
            IngredientRequirement(
                ingredient_id=1, ingredient_name="Flour",
                demand_quantity=Decimal("2000"), demand_unit="g",
                available_quantity=Decimal("1000"), available_unit="g",
                net_requirement_quantity=Decimal("800"), net_requirement_unit="g"
            ),
        ]
        shopping_list = calculate_shopping_list(requirements)
        assert len(shopping_list) == 2
        # Deterministic ordering: ingredient_name then ingredient_id
        assert shopping_list[0].ingredient_name == "Flour"
        assert shopping_list[1].ingredient_name == "Sugar"

    def test_shopping_list_excludes_zero_requirements(self, unit_system_initialized):
        """Requirements with zero net requirement are excluded."""
        from dinner_spinner.domain.shopping_list import calculate_shopping_list
        from dinner_spinner.domain.inventory_requirement import IngredientRequirement
        from decimal import Decimal

        requirements = [
            IngredientRequirement(
                ingredient_id=1, ingredient_name="Flour",
                demand_quantity=Decimal("1000"), demand_unit="g",
                available_quantity=Decimal("1000"), available_unit="g",
                net_requirement_quantity=Decimal("0"), net_requirement_unit="g"
            ),
        ]
        shopping_list = calculate_shopping_list(requirements)
        assert len(shopping_list) == 0

    def test_shopping_list_deterministic_ordering(self, unit_system_initialized):
        """Shopping list has deterministic ordering (name then ID)."""
        from dinner_spinner.domain.shopping_list import calculate_shopping_list
        from dinner_spinner.domain.inventory_requirement import IngredientRequirement
        from decimal import Decimal

        requirements = [
            IngredientRequirement(
                ingredient_id=2, ingredient_name="Sugar",
                demand_quantity=Decimal("1000"), demand_unit="g",
                available_quantity=Decimal("0"), available_unit="g",
                net_requirement_quantity=Decimal("1000"), net_requirement_unit="g"
            ),
            IngredientRequirement(
                ingredient_id=1, ingredient_name="Flour",
                demand_quantity=Decimal("2000"), demand_unit="g",
                available_quantity=Decimal("1000"), available_unit="g",
                net_requirement_quantity=Decimal("800"), net_requirement_unit="g"
            ),
        ]
        shopping_list = calculate_shopping_list(requirements)
        assert len(shopping_list) == 2
        # Deterministic ordering: ingredient_name then ingredient_id
        assert shopping_list[0].ingredient_name == "Flour"
        assert shopping_list[1].ingredient_name == "Sugar"

    def test_shopping_list_excludes_zero_requirements(self, unit_system_initialized):
        """Requirements with zero net requirement are excluded."""
        from dinner_spinner.domain.shopping_list import calculate_shopping_list
        from dinner_spinner.domain.inventory_requirement import IngredientRequirement
        from decimal import Decimal

        requirements = [
            IngredientRequirement(
                ingredient_id=1, ingredient_name="Flour",
                demand_quantity=Decimal("1000"), demand_unit="g",
                available_quantity=Decimal("1000"), available_unit="g",
                net_requirement_quantity=Decimal("0"), net_requirement_unit="g"
            ),
        ]
        shopping_list = calculate_shopping_list(requirements)
        assert len(shopping_list) == 0

    def test_shopping_list_deterministic_ordering(self, unit_system_initialized):
        """Shopping list has deterministic ordering (name then ID)."""
        from dinner_spinner.domain.shopping_list import calculate_shopping_list
        from dinner_spinner.domain.inventory_requirement import IngredientRequirement
        from decimal import Decimal

        requirements = [
            IngredientRequirement(
                ingredient_id=2, ingredient_name="Sugar",
                demand_quantity=Decimal("1000"), demand_unit="g",
                available_quantity=Decimal("0"), available_unit="g",
                net_requirement_quantity=Decimal("1000"), net_requirement_unit="g"
            ),
            IngredientRequirement(
                ingredient_id=1, ingredient_name="Flour",
                demand_quantity=Decimal("2000"), demand_unit="g",
                available_quantity=Decimal("1000"), available_unit="g",
                net_requirement_quantity=Decimal("800"), net_requirement_unit="g"
            ),
        ]
        shopping_list = calculate_shopping_list(requirements)
        assert len(shopping_list) == 2
        # Deterministic ordering: ingredient_name then ingredient_id
        assert shopping_list[0].ingredient_name == "Flour"
        assert shopping_list[1].ingredient_name == "Sugar"

    def test_shopping_list_excludes_zero_requirements(self, unit_system_initialized):
        """Requirements with zero net requirement are excluded."""
        from dinner_spinner.domain.shopping_list import calculate_shopping_list
        from dinner_spinner.domain.inventory_requirement import IngredientRequirement
        from decimal import Decimal

        requirements = [
            IngredientRequirement(
                ingredient_id=1, ingredient_name="Flour",
                demand_quantity=Decimal("1000"), demand_unit="g",
                available_quantity=Decimal("1000"), available_unit="g",
                net_requirement_quantity=Decimal("0"), net_requirement_unit="g"
            ),
        ]
        shopping_list = calculate_shopping_list(requirements)
        assert len(shopping_list) == 0

    def test_shopping_list_deterministic_ordering(self, unit_system_initialized):
        """Shopping list has deterministic ordering (name then ID)."""
        from dinner_spinner.domain.shopping_list import calculate_shopping_list
        from dinner_spinner.domain.inventory_requirement import IngredientRequirement
        from decimal import Decimal

        requirements = [
            IngredientRequirement(
                ingredient_id=2, ingredient_name="Sugar",
                demand_quantity=Decimal("1000"), demand_unit="g",
                available_quantity=Decimal("0"), available_unit="g",
                net_requirement_quantity=Decimal("1000"), net_requirement_unit="g"
            ),
            IngredientRequirement(
                ingredient_id=1, ingredient_name="Flour",
                demand_quantity=Decimal("2000"), demand_unit="g",
                available_quantity=Decimal("1000"), available_unit="g",
                net_requirement_quantity=Decimal("800"), net_requirement_unit="g"
            ),
        ]
        shopping_list = calculate_shopping_list(requirements)
        assert len(shopping_list) == 2
        # Deterministic ordering: ingredient_name then ingredient_id
        assert shopping_list[0].ingredient_name == "Flour"
        assert shopping_list[1].ingredient_name == "Sugar"

    def test_shopping_list_excludes_zero_requirements(self, unit_system_initialized):
        """Requirements with zero net requirement are excluded."""
        from dinner_spinner.domain.shopping_list import calculate_shopping_list
        from dinner_spinner.domain.inventory_requirement import IngredientRequirement
        from decimal import Decimal

        requirements = [
            IngredientRequirement(
                ingredient_id=1, ingredient_name="Flour",
                demand_quantity=Decimal("1000"), demand_unit="g",
                available_quantity=Decimal("1000"), available_unit="g",
                net_requirement_quantity=Decimal("0"), net_requirement_unit="g"
            ),
        ]
        shopping_list = calculate_shopping_list(requirements)
        assert len(shopping_list) == 0

    def test_shopping_list_deterministic_ordering(self, unit_system_initialized):
        """Shopping list has deterministic ordering (name then ID)."""
        from dinner_spinner.domain.shopping_list import calculate_shopping_list
        from dinner_spinner.domain.inventory_requirement import IngredientRequirement
        from decimal import Decimal

        requirements = [
            IngredientRequirement(
                ingredient_id=2, ingredient_name="Sugar",
                demand_quantity=Decimal("1000"), demand_unit="g",
                available_quantity=Decimal("0"), available_unit="g",
                net_requirement_quantity=Decimal("1000"), net_requirement_unit="g"
            ),
            IngredientRequirement(
                ingredient_id=1, ingredient_name="Flour",
                demand_quantity=Decimal("2000"), demand_unit="g",
                available_quantity=Decimal("1000"), available_unit="g",
                net_requirement_quantity=Decimal("800"), net_requirement_unit="g"
            ),
        ]
        shopping_list = calculate_shopping_list(requirements)
        assert len(shopping_list) == 2
        # Deterministic ordering: ingredient_name then ingredient_id
        assert shopping_list[0].ingredient_name == "Flour"
        assert shopping_list[1].ingredient_name == "Sugar"

    def test_shopping_list_excludes_zero_requirements(self, unit_system_initialized):
        """Requirements with zero net requirement are excluded."""
        from dinner_spinner.domain.shopping_list import calculate_shopping_list
        from dinner_spinner.domain.inventory_requirement import IngredientRequirement
        from decimal import Decimal

        requirements = [
            IngredientRequirement(
                ingredient_id=1, ingredient_name="Flour",
                demand_quantity=Decimal("1000"), demand_unit="g",
                available_quantity=Decimal("1000"), available_unit="g",
                net_requirement_quantity=Decimal("0"), net_requirement_unit="g"
            ),
        ]
        shopping_list = calculate_shopping_list(requirements)
        assert len(shopping_list) == 0

    def test_shopping_list_preserves_decimal_precision(self, unit_system_initialized):
        """Decimal quantities are preserved exactly."""
        from dinner_spinner.domain.shopping_list import calculate_shopping_list
        from dinner_spinner.domain.inventory_requirement import IngredientRequirement
        from decimal import Decimal

        requirements = [
            IngredientRequirement(
                ingredient_id=1, ingredient_name="Flour",
                demand_quantity=Decimal("1000.123"), demand_unit="g",
                available_quantity=Decimal("100.456"), available_unit="g",
                net_requirement_quantity=Decimal("900.667"), net_requirement_unit="g"
            ),
        ]
        shopping_list = calculate_shopping_list(requirements)
        assert len(shopping_list) == 1
        assert shopping_list[0].quantity == Decimal("900.667")

    def test_shopping_list_preserves_ingredient_identity(self, unit_system_initialized):
        """Duplicate ingredient names remain separate by ID."""
        from dinner_spinner.domain.shopping_list import calculate_shopping_list
        from dinner_spinner.domain.inventory_requirement import IngredientRequirement
        from decimal import Decimal

        requirements = [
            IngredientRequirement(
                ingredient_id=1, ingredient_name="Flour",
                demand_quantity=Decimal("1000"), demand_unit="g",
                available_quantity=Decimal("0"), available_unit="g",
                net_requirement_quantity=Decimal("1000"), net_requirement_unit="g"
            ),
            IngredientRequirement(
                ingredient_id=2, ingredient_name="Flour",
                demand_quantity=Decimal("500"), demand_unit="g",
                available_quantity=Decimal("0"), available_unit="g",
                net_requirement_quantity=Decimal("500"), net_requirement_unit="g"
            ),
        ]
        shopping_list = calculate_shopping_list(requirements)
        assert len(shopping_list) == 2
        assert shopping_list[0].ingredient_id == 1
        assert shopping_list[1].ingredient_id == 2
        assert shopping_list[0].ingredient_name == "Flour"
        assert shopping_list[1].ingredient_name == "Flour"


class TestShoppingListApplicationService:
    """Tests for the application service layer."""

    def test_get_shopping_list_for_week(self, db_session, unit_system_initialized):
        """get_shopping_list_for_week delegates to Slice 4 and returns shopping list."""
        from dinner_spinner.application.shopping_list import get_shopping_list_for_week
        from dinner_persistence.models import Ingredient, Recipe, RecipeIngredient, MealPlan
        from dinner_spinner.domain.unit_system import initialize, reset
        import datetime

        reset()
        initialize()

        # Clear existing data
        db_session.query(MealPlan).delete()
        db_session.query(RecipeIngredient).delete()
        db_session.query(Recipe).delete()
        db_session.query(Ingredient).delete()
        db_session.commit()

        # Create test data
        flour = Ingredient(name="Flour", quantity=1000, unit="g")
        milk = Ingredient(name="Milk", quantity=2000, unit="ml")
        eggs = Ingredient(name="Eggs", quantity=12, unit="each")
        db_session.add_all([flour, milk, eggs])
        db_session.flush()

        bread = Recipe(name="Bread", servings=4, instructions="Mix and bake")
        db_session.add(bread)
        db_session.flush()

        pancake = Recipe(name="Pancakes", servings=8, instructions="Mix and fry")
        db_session.add(pancake)
        db_session.flush()

        # Bread: 500g flour per 4 servings
        db_session.add(RecipeIngredient(recipe_id=bread.id, ingredient_id=flour.id, quantity=500, unit="g"))
        # Pancakes: 200g flour + 250ml milk + 2 eggs per 8 servings
        db_session.add(RecipeIngredient(recipe_id=pancake.id, ingredient_id=flour.id, quantity=200, unit="g"))
        db_session.add(RecipeIngredient(recipe_id=pancake.id, ingredient_id=milk.id, quantity=250, unit="ml"))
        db_session.add(RecipeIngredient(recipe_id=pancake.id, ingredient_id=eggs.id, quantity=2, unit="each"))
        db_session.commit()

        today = datetime.date.today()
        week_start = int((today - datetime.timedelta(days=today.weekday())).strftime("%Y%m%d"))
        
        mp1 = MealPlan(week_start=week_start, day=0, meal_type="Breakfast", recipe_id=bread.id, servings=8)
        mp2 = MealPlan(week_start=week_start, day=0, meal_type="Dinner", recipe_id=pancake.id, servings=8)
        db_session.add_all([mp1, mp2])
        db_session.commit()

        # Get shopping list
        from dinner_spinner.application.shopping_list import get_shopping_list_for_week
        shopping_list = get_shopping_list_for_week(db_session, week_start)

        # Bread 8 servings = 2x base = 1000g flour
        # Pancakes 8 servings = 1x base = 200g flour + 250ml milk + 2 eggs
        # Total: Flour 1200g, Milk 250ml, Eggs 2 each
        # Inventory: Flour 1000g, Milk 2000ml, Eggs 12
        # Net: Flour 200g, Milk 0, Eggs 0
        assert len(shopping_list) == 1
        assert shopping_list[0].ingredient_name == "Flour"
        assert shopping_list[0].quantity == 200
        assert shopping_list[0].unit == "g"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])