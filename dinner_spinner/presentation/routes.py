"""Presentation layer — Flask routes and templates."""

from flask import Blueprint, render_template, request, redirect, url_for, flash

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    """Home page showing meal plan and inventory overview."""
    from dinner_persistence import db
    from dinner_persistence.models import MealPlan, Ingredient, InventoryCategory

    # Get current week's meal plan
    from datetime import datetime, timedelta
    today = datetime.now().date()
    week_start = int((today - timedelta(days=today.weekday())).strftime("%Y%m%d"))

    meal_plans = db.session.query(MealPlan).filter(
        MealPlan.week_start == week_start
    ).order_by(MealPlan.day, MealPlan.meal_type).all()

    # Get ingredients grouped by category
    categories = db.session.query(InventoryCategory).all()
    ingredients_by_cat = {}
    for cat in categories:
        ingredients = db.session.query(Ingredient).filter(
            Ingredient.inventory_category_id == cat.id
        ).all()
        ingredients_by_cat[cat.name] = ingredients

    # Uncategorized ingredients
    uncategorized = db.session.query(Ingredient).filter(
        Ingredient.inventory_category_id.is_(None)
    ).all()
    if uncategorized:
        ingredients_by_cat["Uncategorized"] = uncategorized

    return render_template(
        "index.html",
        meal_plans=meal_plans,
        ingredients_by_cat=ingredients_by_cat,
        week_start=week_start,
    )


@bp.route("/ingredients")
def ingredients():
    """List all ingredients."""
    from dinner_persistence import db
    from dinner_persistence.models import Ingredient

    ingredients = db.session.query(Ingredient).order_by(Ingredient.name).all()
    return render_template("ingredients.html", ingredients=ingredients)


@bp.route("/ingredients/new", methods=["GET", "POST"])
def ingredient_new():
    """Create a new ingredient."""
    from dinner_persistence import db
    from dinner_persistence.models import Ingredient, InventoryCategory

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        quantity = float(request.form.get("quantity", 0) or 0)
        unit = request.form.get("unit", "").strip()
        category_id = request.form.get("category_id")
        category_id = int(category_id) if category_id else None

        if not name:
            flash("Name is required", "error")
        elif not unit:
            flash("Unit is required", "error")
        elif quantity < 0:
            flash("Quantity cannot be negative", "error")
        else:
            ingredient = Ingredient(
                name=name,
                quantity=quantity,
                unit=unit,
                inventory_category_id=category_id,
            )
            db.session.add(ingredient)
            db.session.commit()
            flash("Ingredient created", "success")
            return redirect(url_for("main.ingredients"))

    categories = db.session.query(InventoryCategory).order_by(InventoryCategory.name).all()
    return render_template("ingredient_form.html", categories=categories, ingredient=None)


@bp.route("/ingredients/<int:id>/edit", methods=["GET", "POST"])
def ingredient_edit(id):
    """Edit an ingredient."""
    from dinner_persistence import db
    from dinner_persistence.models import Ingredient, InventoryCategory

    ingredient = db.session.get(Ingredient, id)
    if not ingredient:
        flash("Ingredient not found", "error")
        return redirect(url_for("main.ingredients"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        quantity = float(request.form.get("quantity", 0) or 0)
        unit = request.form.get("unit", "").strip()
        category_id = request.form.get("category_id")
        category_id = int(category_id) if category_id else None

        if not name:
            flash("Name is required", "error")
        elif not unit:
            flash("Unit is required", "error")
        elif quantity < 0:
            flash("Quantity cannot be negative", "error")
        else:
            # Use domain operation for unit change to preserve physical quantity
            domain_ingredient = ingredient.to_domain()
            domain_ingredient.quantity = quantity  # Update quantity first

            if unit != ingredient.unit:
                # Unit changed - use domain operation to preserve physical quantity
                try:
                    domain_ingredient.change_unit(unit)
                except ValueError as e:
                    flash(f"Unit change failed: {e}", "error")
                    categories = db.session.query(InventoryCategory).order_by(InventoryCategory.name).all()
                    return render_template("ingredient_form.html", categories=categories, ingredient=ingredient)
                except RuntimeError as e:
                    flash(f"Unit system error: {e}", "error")
                    categories = db.session.query(InventoryCategory).order_by(InventoryCategory.name).all()
                    return render_template("ingredient_form.html", categories=categories, ingredient=ingredient)

            # Sync domain changes back to persistence model
            ingredient.name = name
            ingredient.quantity = domain_ingredient.quantity
            ingredient.unit = domain_ingredient.unit
            ingredient.inventory_category_id = category_id

            db.session.commit()
            flash("Ingredient updated", "success")
            return redirect(url_for("main.ingredients"))

    categories = db.session.query(InventoryCategory).order_by(InventoryCategory.name).all()
    return render_template("ingredient_form.html", categories=categories, ingredient=ingredient)


@bp.route("/ingredients/<int:id>/delete", methods=["POST"])
def ingredient_delete(id):
    """Delete an ingredient (if not referenced by recipes)."""
    from dinner_persistence import db
    from dinner_persistence.models import Ingredient, RecipeIngredient
    from sqlalchemy.exc import IntegrityError

    ingredient = db.session.get(Ingredient, id)
    if not ingredient:
        flash("Ingredient not found", "error")
        return redirect(url_for("main.ingredients"))

    # Attempt deletion; DB RESTRICT FK will block if referenced
    try:
        db.session.delete(ingredient)
        db.session.commit()
        flash("Ingredient deleted", "success")
    except IntegrityError:
        db.session.rollback()
        flash("Cannot delete ingredient: referenced by one or more recipes", "error")

    return redirect(url_for("main.ingredients"))


@bp.route("/categories")
def categories():
    """List all inventory categories."""
    from dinner_persistence import db
    from dinner_persistence.models import InventoryCategory

    categories = db.session.query(InventoryCategory).order_by(InventoryCategory.name).all()
    return render_template("categories.html", categories=categories)


@bp.route("/categories/new", methods=["GET", "POST"])
def category_new():
    """Create a new category."""
    from dinner_persistence import db
    from dinner_persistence.models import InventoryCategory

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            flash("Name is required", "error")
        else:
            try:
                category = InventoryCategory(name=name)
                db.session.add(category)
                db.session.commit()
                flash("Category created", "success")
            except Exception as e:
                db.session.rollback()
                flash(f"Error: {e}", "error")
            return redirect(url_for("main.categories"))

    return render_template("category_form.html", category=None)


@bp.route("/categories/<int:id>/edit", methods=["GET", "POST"])
def category_edit(id):
    """Edit a category."""
    from dinner_persistence import db
    from dinner_persistence.models import InventoryCategory

    category = db.session.get(InventoryCategory, id)
    if not category:
        flash("Category not found", "error")
        return redirect(url_for("main.categories"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            flash("Name is required", "error")
        else:
            category.name = name
            db.session.commit()
            flash("Category updated", "success")
            return redirect(url_for("main.categories"))

    return render_template("category_form.html", category=category)


@bp.route("/categories/<int:id>/delete", methods=["POST"])
def category_delete(id):
    """Delete a category (sets ingredient category to NULL)."""
    from dinner_persistence import db
    from dinner_persistence.models import InventoryCategory

    category = db.session.get(InventoryCategory, id)
    if not category:
        flash("Category not found", "error")
        return redirect(url_for("main.categories"))

    # The ondelete="SET NULL" on the FK handles this
    db.session.delete(category)
    db.session.commit()
    flash("Category deleted (ingredients now uncategorized)", "success")
    return redirect(url_for("main.categories"))


@bp.route("/recipes")
def recipes():
    """List all recipes."""
    from dinner_persistence import db
    from dinner_persistence.models import Recipe

    recipes = db.session.query(Recipe).order_by(Recipe.name).all()
    return render_template("recipes.html", recipes=recipes)


@bp.route("/recipes/new", methods=["GET", "POST"])
def recipe_new():
    """Create a new recipe."""
    from dinner_persistence import db
    from dinner_persistence.models import Recipe, RecipeIngredient, Ingredient

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        servings = int(request.form.get("servings", 0) or 0)
        instructions = request.form.get("instructions", "").strip() or None

        if not name:
            flash("Name is required", "error")
        elif servings <= 0:
            flash("Servings must be greater than zero", "error")
        else:
            recipe = Recipe(name=name, servings=servings, instructions=instructions)
            db.session.add(recipe)
            db.session.flush()

            # Handle recipe ingredients
            ingredient_ids = request.form.getlist("ingredient_id")
            quantities = request.form.getlist("quantity")
            units = request.form.getlist("unit")

            for ing_id, qty, unit in zip(ingredient_ids, quantities, units):
                if ing_id and qty and unit:
                    ri = RecipeIngredient(
                        recipe_id=recipe.id,
                        ingredient_id=int(ing_id),
                        quantity=float(qty),
                        unit=unit,
                    )
                    db.session.add(ri)

            db.session.commit()
            flash("Recipe created", "success")
            return redirect(url_for("main.recipes"))

    ingredients = db.session.query(Ingredient).order_by(Ingredient.name).all()
    return render_template("recipe_form.html", ingredients=ingredients, recipe=None)


@bp.route("/recipes/<int:id>")
def recipe_detail(id):
    """View recipe details."""
    from dinner_persistence import db
    from dinner_persistence.models import Recipe

    recipe = db.session.get(Recipe, id)
    if not recipe:
        flash("Recipe not found", "error")
        return redirect(url_for("main.recipes"))

    return render_template("recipe_detail.html", recipe=recipe)


@bp.route("/recipes/<int:id>/edit", methods=["GET", "POST"])
def recipe_edit(id):
    """Edit a recipe."""
    from dinner_persistence import db
    from dinner_persistence.models import Recipe, RecipeIngredient, Ingredient

    recipe = db.session.get(Recipe, id)
    if not recipe:
        flash("Recipe not found", "error")
        return redirect(url_for("main.recipes"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        servings = int(request.form.get("servings", 0) or 0)
        instructions = request.form.get("instructions", "").strip() or None

        if not name:
            flash("Name is required", "error")
        elif servings <= 0:
            flash("Servings must be greater than zero", "error")
        else:
            recipe.name = name
            recipe.servings = servings
            recipe.instructions = instructions

            # Remove old recipe ingredients
            for ri in recipe.recipe_ingredients:
                db.session.delete(ri)

            # Add new ones
            ingredient_ids = request.form.getlist("ingredient_id")
            quantities = request.form.getlist("quantity")
            units = request.form.getlist("unit")

            for ing_id, qty, unit in zip(ingredient_ids, quantities, units):
                if ing_id and qty and unit:
                    ri = RecipeIngredient(
                        recipe_id=recipe.id,
                        ingredient_id=int(ing_id),
                        quantity=float(qty),
                        unit=unit,
                    )
                    db.session.add(ri)

            db.session.commit()
            flash("Recipe updated", "success")
            return redirect(url_for("main.recipe_detail", id=recipe.id))

    ingredients = db.session.query(Ingredient).order_by(Ingredient.name).all()
    return render_template("recipe_form.html", ingredients=ingredients, recipe=recipe)


@bp.route("/recipes/<int:id>/delete", methods=["POST"])
def recipe_delete(id):
    """Delete a recipe (cascades recipe ingredients, nulls meal plans)."""
    from dinner_persistence import db
    from dinner_persistence.models import Recipe

    recipe = db.session.get(Recipe, id)
    if not recipe:
        flash("Recipe not found", "error")
        return redirect(url_for("main.recipes"))

    db.session.delete(recipe)
    db.session.commit()
    flash("Recipe deleted (meal plans referencing it are now empty)", "success")
    return redirect(url_for("main.recipes"))


@bp.route("/meal-plan")
def meal_plan():
    """View and manage meal plan."""
    from dinner_persistence import db
    from dinner_persistence.models import MealPlan, Recipe, Ingredient
    from datetime import datetime, timedelta

    today = datetime.now().date()
    week_start = int((today - timedelta(days=today.weekday())).strftime("%Y%m%d"))

    # Get or create meal plan slots for the week
    meal_types = ["Breakfast", "Lunch", "Dinner"]
    days = list(range(7))  # 0=Monday, 6=Sunday

    meal_plans = {}
    for day in days:
        for meal_type in meal_types:
            mp = db.session.query(MealPlan).filter(
                MealPlan.week_start == week_start,
                MealPlan.day == day,
                MealPlan.meal_type == meal_type
            ).first()
            if not mp:
                mp = MealPlan(
                    week_start=week_start,
                    day=day,
                    meal_type=meal_type,
                    recipe_id=None,
                    servings=1
                )
                db.session.add(mp)
            meal_plans[(day, meal_type)] = mp

    db.session.commit()

    recipes = db.session.query(Recipe).order_by(Recipe.name).all()

    return render_template(
        "meal_plan.html",
        meal_plans=meal_plans,
        recipes=recipes,
        meal_types=meal_types,
        days=days,
        week_start=week_start,
    )


@bp.route("/meal-plan/<int:week_start>", methods=["POST"])
def meal_plan_update(week_start):
    """Update meal plan for a week."""
    from dinner_persistence import db
    from dinner_persistence.models import MealPlan

    meal_types = ["Breakfast", "Lunch", "Dinner"]
    days = list(range(7))

    for day in days:
        for meal_type in meal_types:
            recipe_id = request.form.get(f"recipe_{day}_{meal_type}")
            servings = request.form.get(f"servings_{day}_{meal_type}")

            recipe_id = int(recipe_id) if recipe_id else None
            servings = int(servings) if servings else 1

            mp = db.session.query(MealPlan).filter(
                MealPlan.week_start == week_start,
                MealPlan.day == day,
                MealPlan.meal_type == meal_type
            ).first()

            if mp:
                mp.recipe_id = recipe_id
                mp.servings = max(1, servings)
            else:
                mp = MealPlan(
                    week_start=week_start,
                    day=day,
                    meal_type=meal_type,
                    recipe_id=recipe_id,
                    servings=max(1, servings)
                )
                db.session.add(mp)

    db.session.commit()
    flash("Meal plan updated", "success")
    return redirect(url_for("main.meal_plan"))


# =============================================================================
# Slice 2: Inventory Event Routes
# =============================================================================

@bp.route("/inventory/events")
def inventory_events():
    """Global event history view."""
    from dinner_persistence import db
    from dinner_spinner.application.inventory_events import get_global_event_history

    history = get_global_event_history(db.session, limit=50)
    return render_template("inventory_events.html", history=history)


@bp.route("/ingredients/<int:id>/events")
def ingredient_events(id):
    """Per-ingredient event history view."""
    from dinner_persistence import db
    from dinner_persistence.models import Ingredient
    from dinner_spinner.application.inventory_events import get_ingredient_history

    ingredient = db.session.get(Ingredient, id)
    if not ingredient:
        flash("Ingredient not found", "error")
        return redirect(url_for("main.ingredients"))

    history = get_ingredient_history(db.session, id)
    return render_template("ingredient_events.html", ingredient=ingredient, history=history)


@bp.route("/ingredients/<int:id>/acquire", methods=["GET", "POST"])
def ingredient_acquire(id):
    """Record an acquisition for an ingredient."""
    from dinner_persistence import db
    from dinner_persistence.models import Ingredient, InventoryCategory
    from dinner_spinner.application.inventory_events import (
        record_acquisition, InvalidQuantityError, InvalidUnitError,
        InventoryEventError, IngredientNotFoundError
    )

    ingredient = db.session.get(Ingredient, id)
    if not ingredient:
        flash("Ingredient not found", "error")
        return redirect(url_for("main.ingredients"))

    if request.method == "POST":
        quantity = float(request.form.get("quantity", 0) or 0)
        unit = request.form.get("unit", "").strip()
        cost = float(request.form.get("cost", 0) or 0)

        try:
            record_acquisition(db.session, ingredient_id=id, quantity=quantity, unit=unit, cost=cost)
            flash(f"Acquired {quantity} {unit} of {ingredient.name}", "success")
            return redirect(url_for("main.ingredient_events", id=id))
        except InvalidQuantityError as e:
            flash(f"Invalid quantity: {e}", "error")
        except InvalidUnitError as e:
            flash(f"Invalid unit: {e}", "error")
        except InventoryEventError as e:
            flash(f"Error: {e}", "error")
        except IngredientNotFoundError:
            flash("Ingredient not found", "error")
        except Exception as e:
            db.session.rollback()
            flash(f"Error recording acquisition: {e}", "error")

    categories = db.session.query(InventoryCategory).order_by(InventoryCategory.name).all()
    return render_template("acquire_form.html", ingredient=ingredient, categories=categories)


@bp.route("/ingredients/<int:id>/consume", methods=["GET", "POST"])
def ingredient_consume(id):
    """Record consumption for an ingredient."""
    from dinner_persistence import db
    from dinner_persistence.models import Ingredient, InventoryCategory
    from dinner_spinner.application.inventory_events import (
        record_consumption, InvalidQuantityError, InvalidUnitError,
        InsufficientInventoryError, IngredientNotFoundError
    )

    ingredient = db.session.get(Ingredient, id)
    if not ingredient:
        flash("Ingredient not found", "error")
        return redirect(url_for("main.ingredients"))

    if request.method == "POST":
        quantity = float(request.form.get("quantity", 0) or 0)
        unit = request.form.get("unit", "").strip()

        try:
            record_consumption(db.session, ingredient_id=id, quantity=quantity, unit=unit)
            flash(f"Consumed {quantity} {unit} of {ingredient.name}", "success")
            return redirect(url_for("main.ingredient_events", id=id))
        except InvalidQuantityError as e:
            flash(f"Invalid quantity: {e}", "error")
        except InvalidUnitError as e:
            flash(f"Invalid unit: {e}", "error")
        except InsufficientInventoryError as e:
            flash(f"Insufficient inventory: {e}", "error")
        except IngredientNotFoundError:
            flash("Ingredient not found", "error")
        except Exception as e:
            db.session.rollback()
            flash(f"Error recording consumption: {e}", "error")

    categories = db.session.query(InventoryCategory).order_by(InventoryCategory.name).all()
    return render_template("consume_form.html", ingredient=ingredient, categories=categories)


@bp.route("/ingredients/<int:id>/waste", methods=["GET", "POST"])
def ingredient_waste(id):
    """Record waste for an ingredient."""
    from dinner_persistence import db
    from dinner_persistence.models import Ingredient, InventoryCategory
    from dinner_spinner.application.inventory_events import (
        record_waste, InvalidQuantityError, InvalidUnitError,
        InsufficientInventoryError, IngredientNotFoundError
    )

    ingredient = db.session.get(Ingredient, id)
    if not ingredient:
        flash("Ingredient not found", "error")
        return redirect(url_for("main.ingredients"))

    if request.method == "POST":
        quantity = float(request.form.get("quantity", 0) or 0)
        unit = request.form.get("unit", "").strip()

        try:
            record_waste(db.session, ingredient_id=id, quantity=quantity, unit=unit)
            flash(f"Wasted {quantity} {unit} of {ingredient.name}", "success")
            return redirect(url_for("main.ingredient_events", id=id))
        except InvalidQuantityError as e:
            flash(f"Invalid quantity: {e}", "error")
        except InvalidUnitError as e:
            flash(f"Invalid unit: {e}", "error")
        except InsufficientInventoryError as e:
            flash(f"Insufficient inventory: {e}", "error")
        except IngredientNotFoundError:
            flash("Ingredient not found", "error")
        except Exception as e:
            db.session.rollback()
            flash(f"Error recording waste: {e}", "error")

    categories = db.session.query(InventoryCategory).order_by(InventoryCategory.name).all()
    return render_template("waste_form.html", ingredient=ingredient, categories=categories)


# =============================================================================
# Slice 3: Demand Routes
# =============================================================================

@bp.route("/demand")
def demand_index():
    """Demand overview - shows demand for the current week."""
    from dinner_persistence import db
    from dinner_spinner.application.demand import get_demand_for_week
    from datetime import datetime, timedelta

    today = datetime.now().date()
    week_start = int((today - timedelta(days=today.weekday())).strftime("%Y%m%d"))

    demands = get_demand_for_week(db.session, week_start)

    return render_template("demand_index.html", demands=demands, week_start=week_start)


@bp.route("/demand/<int:week_start>")
def demand_week(week_start):
    """Demand view for a specific week."""
    from dinner_persistence import db
    from dinner_spinner.application.demand import get_demand_for_week

    demands = get_demand_for_week(db.session, week_start)

    return render_template("demand_index.html", demands=demands, week_start=week_start)


# =============================================================================
# Slice 4: Inventory Requirement Routes
# =============================================================================

@bp.route("/requirements")
def requirements_index():
    """Inventory requirements overview - shows requirements for the current week."""
    from dinner_persistence import db
    from dinner_spinner.application.inventory_requirements import get_inventory_requirements_for_week
    from datetime import datetime, timedelta

    today = datetime.now().date()
    week_start = int((today - timedelta(days=today.weekday())).strftime("%Y%m%d"))

    requirements = get_inventory_requirements_for_week(db.session, week_start)

    return render_template("requirements_index.html", requirements=requirements, week_start=week_start)


@bp.route("/requirements/<int:week_start>")
def requirements_week(week_start):
    """Requirements view for a specific week."""
    from dinner_persistence import db
    from dinner_spinner.application.inventory_requirements import get_inventory_requirements_for_week

    requirements = get_inventory_requirements_for_week(db.session, week_start)

    return render_template("requirements_index.html", requirements=requirements, week_start=week_start)