"""Persistence layer — SQLAlchemy models for Dinner Spinner V1.

These models map directly to the domain entities defined in domain/.
They are the authoritative database representation and enforce the
constraints specified by V1_ARCHITECTURE.md.

The persistence layer depends on the domain layer (for entity types),
but the domain layer deliberately does NOT depend on this layer.
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    Boolean,
    ForeignKey,
    UniqueConstraint,
    CheckConstraint,
    Numeric,
)
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

# Domain entity imports are done lazily in to_domain() methods
# to avoid circular imports with dinner_spinner package initialization.

Base = declarative_base()


# ---------------------------------------------------------------------------
# InventoryCategory
# ---------------------------------------------------------------------------


class InventoryCategory(Base):
    __tablename__ = "inventory_category"

    id = Column(Integer, primary_key=True)
    name = Column(String(70), nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # One-to-many: a category may have many ingredients
    # No cascade: FK ondelete="SET NULL" handles deletion; deleting category
    # must not delete ingredients (V1_ARCHITECTURE.md lines 182-192)
    ingredients = relationship(
        "Ingredient",
        back_populates="inventory_category",
    )

    def to_domain(self):
        from dinner_spinner.domain.inventory_category import InventoryCategory as DC_IC
        return DC_IC(id=self.id, name=self.name)


# ---------------------------------------------------------------------------
# Ingredient
# ---------------------------------------------------------------------------


class Ingredient(Base):
    __tablename__ = "ingredient"

    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    inventory_category_id = Column(
        Integer, ForeignKey("inventory_category.id", ondelete="SET NULL"), nullable=True
    )
    quantity = Column(Float, nullable=False, default=0)
    unit = Column(String(40), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Many-to-one: ingredient belongs to optional category
    inventory_category = relationship(
        "InventoryCategory",
        back_populates="ingredients",
        uselist=False,
    )

    # One-to-many: ingredient referenced by many RecipeIngredients
    # No cascade: FK ondelete="RESTRICT" blocks deletion when referenced;
    # deleting ingredient must not delete recipe_ingredients (V1_ARCHITECTURE.md
    # lines 254-258, 167-169)
    recipe_ingredients = relationship(
        "RecipeIngredient",
        back_populates="ingredient",
    )

    # One-to-many: ingredient has many Acquisitions
    # No cascade: FK ondelete="RESTRICT" blocks deletion when referenced
    acquisitions = relationship(
        "Acquisition",
        back_populates="ingredient",
    )

    # One-to-many: ingredient has many Consumptions
    # No cascade: FK ondelete="RESTRICT" blocks deletion when referenced
    consumptions = relationship(
        "Consumption",
        back_populates="ingredient",
    )

    # One-to-many: ingredient has many Wastes
    # No cascade: FK ondelete="RESTRICT" blocks deletion when referenced
    wastes = relationship(
        "Waste",
        back_populates="ingredient",
    )

    __table_args__ = (
        CheckConstraint("quantity >= 0", name="ck_ingredient_quantity_nonnegative"),
    )

    def to_domain(self):
        from dinner_spinner.domain.ingredient import Ingredient as DI_Ingredient
        from dinner_spinner.domain.inventory_category import InventoryCategory as DC_IC
        from decimal import Decimal
        cat = (
            DC_IC(id=self.inventory_category.id, name=self.inventory_category.name)
            if self.inventory_category
            else None
        )
        return DI_Ingredient(
            id=self.id,
            name=self.name,
            inventory_category_id=self.inventory_category_id,
            quantity=Decimal(str(self.quantity)),
            unit=self.unit,
        )


# ---------------------------------------------------------------------------
# Recipe
# ---------------------------------------------------------------------------


class Recipe(Base):
    __tablename__ = "recipe"

    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    servings = Column(Integer, nullable=False)
    instructions = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # One-to-many: recipe has many RecipeIngredients
    recipe_ingredients = relationship(
        "RecipeIngredient",
        back_populates="recipe",
        cascade="all, delete-orphan",
    )

    # One-to-many (inverse): MealPlans referencing this recipe
    # No cascade: FK ondelete="SET NULL" handles deletion; deleting recipe
    # must not delete meal plans, must set recipe_id = NULL (V1_ARCHITECTURE.md
    # lines 313-317)
    meal_plans = relationship(
        "MealPlan",
        back_populates="recipe",
    )

    __table_args__ = (
        CheckConstraint("servings > 0", name="ck_recipe_servings_positive"),
    )

    def to_domain(self):
        from dinner_spinner.domain.recipe import Recipe as DI_Recipe
        return DI_Recipe(
            id=self.id,
            name=self.name,
            servings=self.servings,
            instructions=self.instructions,
        )


# ---------------------------------------------------------------------------
# RecipeIngredient
# ---------------------------------------------------------------------------


class RecipeIngredient(Base):
    __tablename__ = "recipe_ingredient"

    id = Column(Integer, primary_key=True)
    recipe_id = Column(
        Integer, ForeignKey("recipe.id", ondelete="CASCADE"), nullable=False
    )
    ingredient_id = Column(
        Integer, ForeignKey("ingredient.id", ondelete="RESTRICT"), nullable=False
    )
    quantity = Column(Float, nullable=False)
    unit = Column(String(40), nullable=False)

    # Many-to-one: belongs to a recipe
    recipe = relationship("Recipe", back_populates="recipe_ingredients")

    # Many-to-one: belongs to an ingredient
    ingredient = relationship("Ingredient", back_populates="recipe_ingredients")

    __table_args__ = (
        UniqueConstraint(
            "recipe_id", "ingredient_id", name="uq_recipe_ingredient_recipe_ingredient"
        ),
        CheckConstraint("quantity > 0", name="ck_recipe_ingredient_quantity_positive"),
    )

    def to_domain(self):
        from dinner_spinner.domain.recipe_ingredient import RecipeIngredient as DI_RecipeIngredient
        return DI_RecipeIngredient(
            id=self.id,
            recipe_id=self.recipe_id,
            ingredient_id=self.ingredient_id,
            quantity=self.quantity,
            unit=self.unit,
        )


# ---------------------------------------------------------------------------
# MealPlan
# ---------------------------------------------------------------------------


class MealPlan(Base):
    __tablename__ = "meal_plan"

    id = Column(Integer, primary_key=True)
    week_start = Column(Integer, nullable=False)
    day = Column(Integer, nullable=False)
    meal_type = Column(String(40), nullable=False)
    recipe_id = Column(
        Integer, ForeignKey("recipe.id", ondelete="SET NULL"), nullable=True
    )
    servings = Column(Integer, nullable=False)

    # Many-to-one: meal plan references a recipe (nullable)
    recipe = relationship("Recipe", back_populates="meal_plans")

    __table_args__ = (
        UniqueConstraint(
            "week_start",
            "day",
            "meal_type",
            name="uq_mealplan_week_day_meal_type",
        ),
        CheckConstraint("servings > 0", name="ck_mealplan_servings_positive"),
    )

    def to_domain(self):
        from dinner_spinner.domain.meal_plan import MealPlan as DI_MealPlan
        return DI_MealPlan(
            id=self.id,
            week_start=self.week_start,
            day=self.day,
            meal_type=self.meal_type,
            recipe_id=self.recipe_id,
            servings=self.servings,
        )


# ---------------------------------------------------------------------------
# Acquisition
# ---------------------------------------------------------------------------


class Acquisition(Base):
    __tablename__ = "acquisition"

    id = Column(Integer, primary_key=True)
    ingredient_id = Column(
        Integer, ForeignKey("ingredient.id", ondelete="RESTRICT"), nullable=False
    )
    quantity = Column(Float, nullable=False)
    unit = Column(String(40), nullable=False)
    cost = Column(Numeric(10, 2), nullable=False, default=0)
    acquired_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Many-to-one: acquisition belongs to an ingredient
    ingredient = relationship("Ingredient", back_populates="acquisitions", uselist=False)

    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_acquisition_quantity_positive"),
        CheckConstraint("cost >= 0", name="ck_acquisition_cost_nonnegative"),
    )

    def to_domain(self):
        from dinner_spinner.domain.acquisition import Acquisition as DI_Acquisition
        from decimal import Decimal
        return DI_Acquisition(
            id=self.id,
            ingredient_id=self.ingredient_id,
            quantity=self.quantity,
            unit=self.unit,
            cost=Decimal(str(self.cost)),
            acquired_at=self.acquired_at,
        )


# ---------------------------------------------------------------------------
# Consumption
# ---------------------------------------------------------------------------


class Consumption(Base):
    __tablename__ = "consumption"

    id = Column(Integer, primary_key=True)
    ingredient_id = Column(
        Integer, ForeignKey("ingredient.id", ondelete="RESTRICT"), nullable=False
    )
    quantity = Column(Float, nullable=False)
    unit = Column(String(40), nullable=False)
    consumed_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Many-to-one: consumption belongs to an ingredient
    ingredient = relationship("Ingredient", back_populates="consumptions", uselist=False)

    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_consumption_quantity_positive"),
    )

    def to_domain(self):
        from dinner_spinner.domain.consumption import Consumption as DI_Consumption
        return DI_Consumption(
            id=self.id,
            ingredient_id=self.ingredient_id,
            quantity=self.quantity,
            unit=self.unit,
            consumed_at=self.consumed_at,
        )


# ---------------------------------------------------------------------------
# Waste
# ---------------------------------------------------------------------------


class Waste(Base):
    __tablename__ = "waste"

    id = Column(Integer, primary_key=True)
    ingredient_id = Column(
        Integer, ForeignKey("ingredient.id", ondelete="RESTRICT"), nullable=False
    )
    quantity = Column(Float, nullable=False)
    unit = Column(String(40), nullable=False)
    wasted_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Many-to-one: waste belongs to an ingredient
    ingredient = relationship("Ingredient", back_populates="wastes", uselist=False)

    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_waste_quantity_positive"),
    )

    def to_domain(self):
        from dinner_spinner.domain.waste import Waste as DI_Waste
        return DI_Waste(
            id=self.id,
            ingredient_id=self.ingredient_id,
            quantity=self.quantity,
            unit=self.unit,
            wasted_at=self.wasted_at,
        )