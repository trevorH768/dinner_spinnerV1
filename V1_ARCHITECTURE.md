---
title: Dinner Spinner — V1 Domain & Architecture Specification
updated: 2026-09-03 00:48:54Z
created: 2026-09-03 00:48:50Z
latitude: 53.53768090
longitude: -113.50817900
altitude: 0.0000
---

# Dinner Spinner — V1 Domain & Architecture Specification

**Status:** Authoritative V1 specification
**Audience:** Developers, coding agents, testers, and future maintainers
**Purpose:** Define the domain model, invariants, calculations, boundaries, and scope of Dinner Spinner V1.

---

# 1. V1 Purpose

Dinner Spinner is a household meal-planning and inventory-management application.

Its core purpose is to answer:

1. What food do we currently have?
2. What food is required by the meals we have planned?
3. Do we have enough?
4. What quantity needs to be acquired?

The core domain flow is:

```text
INGREDIENT
    ↓
RECIPE
    ↓
MEAL PLAN
    ↓
DEMAND
    ↓
AVAILABLE INVENTORY
    ↓
NET REQUIREMENT
    ↓
SHOPPING LIST
    ↓
HUMAN PURCHASE
    ↓
ACQUISITION
    ↓
INGREDIENT INVENTORY
```

Inventory changes occur through explicit historical events:

```text
ACQUISITION ─────► INGREDIENT (+)
CONSUMPTION ─────► INGREDIENT (-)
WASTE ───────────► INGREDIENT (-)
```

---

# 2. Architectural Principles

These principles are mandatory.

## 2.1 Domain first

The domain model and its rules define the application.

Database structure and implementation details must serve the domain rather than dictate it.

## 2.2 One entity, one job

Every domain entity must have a clearly defined responsibility.

Do not create entities merely because information exists.

Do not add fields to an entity merely because the information is related to it.

## 2.3 Identity is not state, observation, or event

A persistent entity identifies something.

A current-state field represents the current state of that entity.

A historical event records something that happened.

These concepts must not be conflated.

## 2.4 Derived concepts are calculated

Demand, Available Inventory, Net Requirement, Shopping List, and costing calculations are derived from authoritative data.

Do not persist derived values as authoritative state unless explicitly required by this specification.

## 2.5 Preserve user-entered units

User-entered quantities and units must be preserved.

Unit normalization is a calculation concern.

Do not silently rewrite a user's original quantity or unit merely to make calculations easier.

## 2.6 No speculative domain modeling

Do not introduce Product, Package, Store, Brand, Barcode, Location, Container, Transfer, InventoryEvent, PriceEstimate, or similar concepts unless explicitly added to the V1 specification.

Future extensibility must come from clean boundaries rather than speculative entities.

## 2.7 Deterministic calculations should be automated

The application should calculate deterministic requirements.

Human purchasing decisions remain human decisions.

Dinner Spinner determines:

> "You need 2 kg of flour."

It does not determine:

> "Buy this specific 2 kg package of Brand X from Store Y."

---

# 3. Authoritative Domain Entities

V1 contains exactly these authoritative domain entities:

```text
InventoryCategory
Ingredient
Recipe
RecipeIngredient
MealPlan
Acquisition
Consumption
Waste
```

Derived concepts:

```text
Demand
Available Inventory
Net Requirement
Cost Per Unit
Recipe Cost
Meal Cost
Shopping List
```

---

# 4. InventoryCategory

## Definition

**Inventory Category:** A user-assigned organizational classification used to group Ingredients for inventory presentation and management.

## Fields

```text
InventoryCategory
├── id
└── name
```

## Rules

* An Ingredient may belong to zero or one InventoryCategory.
* An InventoryCategory may contain zero or many Ingredients.
* Categories are assigned by the user.
* Categories have no effect on calculations.
* Categories have no hierarchy.
* Categories do not represent physical storage locations.
* Smart category detection is outside V1.

## Deletion

Deleting an InventoryCategory must:

```text
Ingredient.inventory_category_id = NULL
```

for all Ingredients assigned to it.

The category may then be deleted.

Deleting a category must not delete Ingredients.

---

# 5. Ingredient

## Definition

**Ingredient:** A user-defined, user-managed physical inventory holding identified by its own record. It has a name, current non-negative quantity, unit, and optional user-assigned Inventory Category. An Ingredient may be referenced by many Recipes but may appear only once within any individual Recipe. Zero quantity is valid. Ingredients are never automatically deleted, merged, categorized, or recreated. An Ingredient cannot be deleted while referenced by a Recipe.

## Fields

```text
Ingredient
├── id
├── name
├── inventory_category_id   # nullable
├── quantity
└── unit
```

## Responsibility

Ingredient represents the household's current inventory state.

The Ingredient itself is the inventory holding.

There is no separate Container entity in V1.

## Rules

* `name` is required.
* `unit` is required.
* `quantity` must be non-negative.
* Zero quantity is valid.
* Quantity may be decimal.
* Unit must be a recognized application unit.
* Ingredient records are independent identities.
* Multiple Ingredient records may represent separate physical holdings of the same general food.
* Ingredient records must never be automatically merged.
* Ingredient records must never be automatically recreated.
* Ingredient records must never be automatically deleted because quantity reaches zero.
* Inventory Category is optional.

## Quantity

`quantity` represents the current physical quantity available.

It is authoritative current state.

It is not reconstructed by replaying historical events.

## Unit changes

Changing an Ingredient's unit must preserve the represented quantity through a valid conversion.

An incompatible conversion must be rejected.

The application must not invent density or other information required for conversion.

## Deletion

An Ingredient may be deleted only when it is not referenced by any RecipeIngredient.

If an Ingredient is referenced by a Recipe, deletion must be rejected.

Deleting an Ingredient must never silently modify Recipes.

---

# 6. Recipe

## Definition

**Recipe:** A user-defined preparation specification that identifies a dish or food preparation by name, defines its base serving yield and preparation instructions, and identifies the Ingredients and quantities required to produce that yield.

## Fields

```text
Recipe
├── id
├── name
├── servings
├── instructions
└── created_at
```

## Responsibility

Recipe defines:

* what is being prepared;
* its base serving yield;
* how it is prepared;
* which Ingredients are required.

Recipe does not represent inventory.

Recipe does not represent purchasing.

Recipe does not represent a meal plan.

Recipe does not represent demand.

Recipe does not contain product, package, store, brand, barcode, or availability data.

## Rules

* `name` is required.
* `servings` must be greater than zero.
* V1 uses integer servings.
* Recipe base servings are independent of MealPlan planned servings.

## Deletion

Deleting a Recipe must cascade-delete its RecipeIngredients.

Deleting a Recipe must NOT delete its Ingredients.

Deleting a Recipe must NOT delete MealPlans.

MealPlans referencing the deleted Recipe must remain valid and become empty meal slots by setting:

```text
MealPlan.recipe_id = NULL
```

---

# 7. RecipeIngredient

## Definition

**RecipeIngredient:** A Recipe-specific requirement that identifies an Ingredient and specifies the positive quantity and unit of that Ingredient required to produce the Recipe's defined serving yield. A Recipe may reference a given Ingredient only once.

## Fields

```text
RecipeIngredient
├── id
├── recipe_id
├── ingredient_id
├── quantity
└── unit
```

## Responsibility

RecipeIngredient represents the relationship between a Recipe and an Ingredient.

It answers:

> "How much of this Ingredient does this Recipe require for its base serving yield?"

## Rules

* `quantity` must be greater than zero.
* Decimal quantities are allowed.
* `unit` must be recognized.
* RecipeIngredient unit does not need to match Ingredient inventory unit.
* Original quantity and unit must be preserved.
* Unit normalization occurs only during calculation.
* A Recipe may reference a given Ingredient only once.

Database/application integrity must enforce:

```text
UNIQUE(recipe_id, ingredient_id)
```

If an ingredient is required in multiple places in a recipe, its total requirement belongs in one RecipeIngredient record. Instructions may describe how it is divided or used.

## Deletion

Deleting a RecipeIngredient:

* does not modify the Ingredient;
* does not modify the Recipe itself.

Deleting a Recipe cascades its RecipeIngredients.

---

# 8. MealPlan

## Definition

**MealPlan:** A user-defined planning record that schedules a Recipe, or an intentionally empty meal slot, for a specific day and meal type within a defined planning week, and specifies the number of servings planned.

## Fields

```text
MealPlan
├── id
├── week_start
├── day
├── meal_type
├── recipe_id       # nullable
└── servings
```

## Rules

A MealPlan must have a unique combination of:

```text
week_start + day + meal_type
```

`recipe_id` is nullable.

An empty meal slot is valid.

A MealPlan may therefore represent:

```text
recipe_id = NULL
servings = positive value
```

Planned servings must be greater than zero.

V1 uses integer planned servings.

## Responsibility

MealPlan answers:

> "What are we planning to eat, when, and for how many people?"

MealPlan does not contain ingredient quantities.

MealPlan does not directly modify inventory.

MealPlan does not store Demand.

## Recipe deletion

If a Recipe is deleted:

```text
MealPlan.recipe_id = NULL
```

The MealPlan itself remains.

---

# 9. Acquisition

## Definition

**Acquisition:** A historical record of an event in which the household obtains a positive quantity of an Ingredient, optionally recording the actual amount paid for that acquisition. Recording an Acquisition increases the current quantity of the referenced Ingredient by the acquired quantity after valid unit conversion.

## Fields

```text
Acquisition
├── id
├── ingredient_id
├── quantity
├── unit
├── cost
└── acquired_at
```

## Rules

* Quantity must be greater than zero.
* Unit must be recognized.
* Unit must be compatible with the Ingredient's unit through a valid conversion.
* Cost may be zero.
* Cost represents the actual amount paid.
* Cost is not an estimate.
* Cost per unit is derived.
* Recording an Acquisition immediately increases current Ingredient quantity.
* Acquisition does not create an Ingredient.
* The user selects which Ingredient holding receives the acquisition.

## Historical semantics

Acquisition is a historical fact.

Once recorded, it is immutable in V1.

It cannot be edited or deleted.

If an error must be corrected, a compensating event must be recorded.

## Transaction

Recording an Acquisition must be atomic:

```text
BEGIN

validate acquisition
validate quantity
validate unit
validate conversion
create Acquisition
increase Ingredient.quantity

COMMIT
```

If any operation fails, the entire operation must roll back.

---

# 10. Consumption

## Definition

**Consumption:** A historical record of an event in which the household uses a positive quantity of an Ingredient, reducing the current quantity of that Ingredient by the consumed amount after valid unit conversion. A Consumption cannot reduce an Ingredient's quantity below zero.

## Fields

```text
Consumption
├── id
├── ingredient_id
├── quantity
├── unit
└── consumed_at
```

## Rules

* Quantity must be greater than zero.
* Unit must be recognized.
* Unit must be compatible through a valid conversion.
* Requested consumption may not exceed available quantity.
* Inventory may never become negative.
* Recording Consumption decreases current Ingredient quantity.
* Consumption does not modify Recipes.
* Consumption does not modify MealPlans.
* Consumption does not modify Demand.
* Consumption does not create or delete Ingredients.

## Historical semantics

Consumption is immutable in V1.

It cannot be edited or deleted.

Errors are corrected with compensating events.

## Transaction

```text
BEGIN

validate consumption
validate quantity
validate conversion
validate available quantity
create Consumption
decrease Ingredient.quantity

COMMIT
```

Any failure must roll back the entire operation.

---

# 11. Waste

## Definition

**Waste:** A historical record of an event in which a quantity of an Ingredient leaves household inventory without being consumed, reducing the current quantity of that Ingredient by the wasted amount after valid unit conversion. A Waste event cannot reduce an Ingredient's quantity below zero.

## Fields

```text
Waste
├── id
├── ingredient_id
├── quantity
├── unit
└── wasted_at
```

## Rules

Waste behaves like Consumption except for its semantic meaning.

* Quantity must be greater than zero.
* Unit must be recognized.
* Unit must be compatible through a valid conversion.
* Requested waste may not exceed available quantity.
* Inventory may never become negative.
* Recording Waste decreases current Ingredient quantity.
* Waste does not modify Recipes.
* Waste does not modify MealPlans.
* Waste does not modify Demand.
* Waste does not create or delete Ingredients.

## Historical semantics

Waste is immutable in V1.

It cannot be edited or deleted.

Errors are corrected with compensating events.

---

# 12. Historical Inventory Events

V1 deliberately does NOT define a generalized `InventoryEvent` entity.

The three historical event types are distinct:

```text
Acquisition
Consumption
Waste
```

They must remain separate domain concepts.

All historical inventory events are immutable.

Current Ingredient quantity is authoritative current state.

The application does NOT reconstruct current inventory by replaying:

```text
Acquisition - Consumption - Waste
```

Historical events record what happened.

Ingredient.quantity records what is currently true.

---

# 13. Unit System

The application must have one centralized unit/conversion system.

V1 recognizes these categories:

```text
MASS
    g
    kg
    oz
    lb

VOLUME
    ml
    l
    cup
    tbsp
    tsp

COUNT
    each
    piece
    pieces
    count
```

Exact canonical aliases may be defined by the implementation, but all user-facing units must resolve through the centralized conversion system.

## Rules

Same-category conversions are directly supported.

Examples:

```text
kg ↔ g
lb ↔ oz
l ↔ ml
cup ↔ tbsp
```

Cross-category conversions require sufficient information.

The system must never invent density.

For example:

```text
1 cup → grams
```

cannot be calculated generically without density.

Likewise:

```text
1 cup → pieces
```

cannot be calculated without appropriate item-specific information.

Invalid conversions must be rejected rather than guessed.

## Important architectural rule

Do not create a fake universal base unit that implies every unit can always be converted to every other unit.

Conversion must respect dimensional compatibility and required conversion information.

---

# 14. Demand

## Definition

**Demand:** The calculated quantity of an Ingredient required to fulfill the meals represented by a defined Meal Plan for its planning period. Demand is derived from planned recipes, RecipeIngredient quantities, and planned servings, with compatible units normalized for calculation and requirements aggregated by Ingredient. Demand represents planned consumption requirements only and does not represent inventory, purchasing, pricing, product selection, or availability.

Demand is derived.

It is not stored as authoritative state.

## Calculation

For each MealPlan containing a Recipe:

```text
Required Quantity =
    RecipeIngredient Quantity
    ×
    (MealPlan Planned Servings / Recipe Base Servings)
```

Example:

```text
Recipe:
    4 servings

RecipeIngredient:
    500 g flour

MealPlan:
    8 servings

Demand:
    1000 g flour
```

## Aggregation

Demand must aggregate by Ingredient identity after compatible unit normalization.

Conceptually:

```text
MealPlan
    ↓
Recipe
    ↓
RecipeIngredient
    ↓
Serving adjustment
    ↓
Unit normalization
    ↓
Aggregate by Ingredient
```

A MealPlan with `recipe_id = NULL` produces no Demand.

No zero-demand record needs to be created.

---

# 15. Available Inventory

## Definition

**Available Inventory:** The calculated quantity currently available to the household from the user's Ingredient records. Available Inventory is derived from the current quantity of each Ingredient and may aggregate quantities from multiple Ingredient records for calculation when their units are compatible. Ingredient records remain independent and are never merged by this calculation. Available Inventory does not represent historical events, demand, purchasing, pricing, or product selection.

## Rules

* Based on current Ingredient.quantity.
* Zero quantity contributes zero.
* Multiple Ingredient records may be aggregated for calculation.
* Compatible units may be normalized.
* Incompatible units cannot be aggregated without valid conversion information.
* Aggregation never merges Ingredient records.
* Available Inventory does not modify inventory.
* Available Inventory does not create or delete Ingredients.
* Available Inventory does not replay historical events.

---

# 16. Net Requirement

## Definition

**Net Requirement:** The calculated quantity of an Ingredient that must be acquired to satisfy Demand after subtracting Available Inventory, with quantities normalized to a compatible calculation unit.

## Formula

```text
Net Requirement =
    max(Demand - Available Inventory, 0)
```

## Rules

* Net Requirement is derived.
* It is not persisted as authoritative state.
* It can never be negative.
* It uses Demand and current Available Inventory.
* Compatible Ingredient holdings may be aggregated for calculation.
* It does not modify inventory.
* It does not create Ingredients.
* It does not select products or packages.
* It does not select stores.
* It does not make purchasing decisions.

---

# 17. Shopping List

## Definition

**Shopping List:** A calculated projection of the Net Requirements for the selected calendar month, presented as a user-facing list of Ingredients and quantities that need to be acquired.

## V1 behavior

There is NO persistent ShoppingList entity.

There is NO persistent ShoppingListItem entity.

The shopping list is a projection.

The user generates the shopping list for the calendar month corresponding to when the action is performed.

If the Meal Plan or inventory changes, the calculated Shopping List changes accordingly.

There are no stale stored shopping lists.

## Shopping List item

Conceptually:

```text
Ingredient
+
required quantity
+
calculation/display unit
```

## Rules

* Shopping List is derived from Net Requirements.
* Empty result is valid.
* Shopping List does not own requirements.
* Checking/completing a shopping-list item does not modify inventory.
* A shopping-list item does not represent an acquisition.
* No direct ShoppingList ↔ Acquisition relationship exists.
* Actual purchasing remains a human action.
* The actual acquisition is recorded separately through Acquisition.

---

# 18. Costing

V1 costing answers:

> "What did this quantity of this Ingredient cost us?"

Cost is based on actual Acquisition history.

## Acquisition example

```text
Ingredient:
    Robin Hood Flour

Acquisition:
    10 kg
    $10
```

Derived:

```text
$1 / kg
$0.001 / g
```

## Rules

* Cost is stored only on Acquisition.
* Ingredient does not contain a current price field.
* Ingredient does not contain package price.
* Ingredient does not contain estimated price.
* Cost per unit is derived.
* Recipe cost is derived.
* Meal cost is derived.
* No price estimate is generated.

## Recipe costing

If:

```text
Recipe requires:
    350 g flour

Historical acquisition cost:
    $0.001/g
```

then:

```text
Flour recipe cost = $0.35
```

Costing must use compatible units and valid conversions.

## Out of scope

Do not implement:

* market pricing;
* price prediction;
* estimated prices;
* store comparisons;
* package optimization;
* coupon optimization;
* product selection;
* availability lookup.

---

# 19. Application Architecture

The application should separate:

```text
DOMAIN
    authoritative entities and rules

CALCULATION
    Demand
    Available Inventory
    Net Requirement
    Cost calculations

PERSISTENCE
    database models and transactions

APPLICATION SERVICES
    orchestration of domain operations

PRESENTATION
    Flask routes/templates/UI
```

Exact implementation technology may differ, but domain responsibilities must remain separated.

## Important rule

Do not make Flask routes responsible for complex domain calculations.

Routes should orchestrate application behavior and presentation.

Core calculations should be testable independently of HTTP/UI concerns.

---

# 20. Transactional Inventory Operations

Acquisition, Consumption, and Waste must be implemented as transactional operations.

The invariant is:

```text
Historical Event Created
        +
Ingredient Quantity Updated
```

must succeed together or fail together.

Never allow:

```text
event exists but inventory wasn't changed
```

or:

```text
inventory changed but event wasn't recorded
```

---

# 21. Database Integrity Requirements

The database/application must enforce, at minimum:

```text
Ingredient.quantity >= 0

Recipe.servings > 0

RecipeIngredient.quantity > 0

MealPlan.servings > 0

Acquisition.quantity > 0

Consumption.quantity > 0

Waste.quantity > 0
```

Also enforce:

```text
UNIQUE(RecipeIngredient.recipe_id,
       RecipeIngredient.ingredient_id)
```

and:

```text
UNIQUE(MealPlan.week_start,
       MealPlan.day,
       MealPlan.meal_type)
```

Foreign-key behavior must preserve the domain deletion rules defined above.

---

# 22. Explicit Domain Boundaries

The following relationships are intentional:

```text
InventoryCategory
        ↓
    Ingredient
        ↑
RecipeIngredient
        ↑
     Recipe
        ↑
    MealPlan
        ↓
     Demand
        ↓
Net Requirement
        ↓
 Shopping List
        ↓
     HUMAN
        ↓
  Acquisition
        ↓
    Ingredient
```

Inventory events:

```text
Acquisition ──► Ingredient (+)
Consumption ─► Ingredient (-)
Waste ───────► Ingredient (-)
```

There is no:

```text
Ingredient → Product
Ingredient → Package
Ingredient → Store
Ingredient → Barcode
Ingredient → Nutrition
Ingredient → Price
Ingredient → Location
```

in V1.

There is no:

```text
MealPlan → Inventory
Recipe → Inventory
ShoppingList → Acquisition
ShoppingList → Product
```

in V1.

---

# 23. Explicitly Out of Scope for V1

The following must NOT be implemented as part of the V1 architecture unless this specification is explicitly amended.

## Food / Nutrition

* USDA FoodData Central
* Health Canada CNF
* Open Food Facts
* nutrition data
* nutrient calculations
* barcode lookup
* food databases
* food-provider integrations

## Commercial Product Modeling

* Product
* Package
* Brand
* Barcode
* SKU
* Store
* supplier
* product availability
* product selection
* package-size optimization

## Pricing

* estimated prices
* market prices
* price prediction
* store price comparison
* coupons
* sale prediction
* price scraping
* external pricing APIs

## Inventory Complexity

* Container entity
* Storage Location
* Warehouse
* Transfer
* generalized InventoryEvent
* inventory reconstruction from event history
* automatic merging
* automatic splitting
* automatic recreation
* expiry tracking
* lot/batch tracking

## Smart Features

* automatic categorization
* AI categorization
* automatic ingredient matching
* automatic product matching
* purchasing optimization
* recommendation engines

These may be considered later.

They must not influence V1 domain architecture.

---

# 24. Existing Code Migration

The current application may contain functionality that conflicts with this specification.

When existing code conflicts with this specification:

**This specification wins.**

Existing implementation details are not requirements.

The current UI may be preserved where practical, particularly:

* week planning;
* month planning;
* recipe management;
* ingredient management;
* navigation;
* existing useful templates.

However, preserving existing UI does NOT justify preserving incorrect domain architecture.

The implementation may be substantially rewritten.

---

# 25. Food Data Subsystem

The existing food-data subsystem is quarantined from the V1 domain.

It may remain in the repository temporarily.

It must not:

* define the V1 Ingredient model;
* add fields to Ingredient;
* create relationships required by V1;
* dictate persistence architecture;
* introduce pricing/package/nutrition requirements into V1;
* couple core domain code to external food providers.

The food subsystem is parked for future work.

---

# 26. V1 Implementation Strategy

Implementation should proceed in controlled vertical slices.

Do NOT attempt to implement the entire architecture in one uncontrolled change.

Recommended order:

### Slice 1 — Domain and Persistence

Implement:

```text
InventoryCategory
Ingredient
Recipe
RecipeIngredient
MealPlan
```

including:

* correct fields;
* relationships;
* constraints;
* deletion behavior;
* validation;
* unit representation;
* database integrity.

Do not implement new features in this slice.

### Slice 2 — Inventory Events

Implement:

```text
Acquisition
Consumption
Waste
```

including:

* immutable history;
* transactional updates;
* conversion;
* non-negative inventory invariant.

### Slice 3 — Demand

Implement pure Demand calculation.

### Slice 4 — Available Inventory and Net Requirement

Implement pure calculations:

```text
Available Inventory
Net Requirement
```

### Slice 5 — Shopping List

Implement the monthly Shopping List projection.

### Slice 6 — Costing

Implement:

```text
cost per unit
recipe cost
meal cost
```

from Acquisition history.

### Slice 7 — UI Integration

Update existing UI to consume the new domain/application services.

Only after the underlying behavior is correct should UI cleanup be performed.

---

# 27. Testing Requirements

Tests must verify domain invariants rather than merely implementation details.

At minimum, test:

## Ingredient

* quantity cannot be negative;
* zero quantity is valid;
* deletion blocked while referenced;
* deletion succeeds when unreferenced;
* category optional;
* category deletion nulls assignment.

## Recipe

* servings must be positive;
* deletion cascades RecipeIngredients;
* deletion preserves Ingredients;
* deletion nulls MealPlan.recipe_id.

## RecipeIngredient

* quantity must be positive;
* duplicate Ingredient within Recipe rejected;
* original quantity/unit preserved.

## MealPlan

* unique week/day/meal type;
* recipe nullable;
* positive servings;
* empty slots remain valid.

## Acquisition

* positive quantity;
* valid conversion;
* inventory increases;
* event recorded;
* operation is atomic;
* historical record immutable.

## Consumption

* positive quantity;
* inventory decreases;
* cannot exceed available inventory;
* event recorded;
* operation is atomic;
* historical record immutable.

## Waste

Same inventory and transactional guarantees as Consumption.

## Demand

* serving scaling;
* multiple MealPlans;
* aggregation by Ingredient;
* compatible units;
* empty meal slots produce no demand.

## Available Inventory

* current quantity;
* zero quantity;
* multiple holdings;
* compatible-unit aggregation;
* no identity merging.

## Net Requirement

* demand greater than inventory;
* inventory greater than demand;
* equal demand/inventory;
* multiple holdings;
* no negative results.

## Shopping List

* monthly projection;
* no persistent shopping-list state;
* reflects current MealPlan and inventory state.

## Unit Conversion

Test:

* mass ↔ mass;
* volume ↔ volume;
* count ↔ count;
* valid density-based conversions;
* invalid conversions;
* conversions requiring missing information;
* prevention of mathematically invalid volume/count and mass/count conversions.

---

# 28. Definition of Done for V1 Domain Rewrite

The V1 rewrite is architecturally complete when:

1. The authoritative entities match this specification.
2. Obsolete Ingredient fields are removed.
3. Food-data concerns are isolated from the core domain.
4. MealPlan supports empty slots.
5. Recipe deletion preserves MealPlans by nulling their Recipe reference.
6. Ingredient deletion respects Recipe references.
7. RecipeIngredient uniqueness is enforced.
8. Inventory events are immutable.
9. Inventory event operations are transactional.
10. Ingredient quantity never becomes negative.
11. Demand is derived rather than stored.
12. Available Inventory is derived rather than stored.
13. Net Requirement is derived rather than stored.
14. Shopping List is a projection rather than a persistent entity.
15. Costing is based on actual Acquisition history.
16. Unit conversion is centralized and mathematically valid.
17. Core calculations are independently testable.
18. Existing UI is adapted to the new domain rather than dictating it.
19. V1 does not depend on food databases, product databases, stores, packages, or price estimates.

---

# 29. Non-Negotiable Rule for AI-Assisted Development

When implementing this specification:

**Do not invent missing requirements.**

If the specification does not define behavior, stop and identify the ambiguity rather than silently creating a new domain concept or feature.

When existing code conflicts with this specification:

**Replace or adapt the existing code. Do not preserve incorrect architecture merely because it already exists.**

When a requested change appears to require a new entity or field, ask:

> "What domain responsibility does this entity/field own?"

If that responsibility is already represented elsewhere, do not duplicate it.

Before adding a field, ask:

> "Is this property intrinsic to this thing, or is this information about its relationship to something else?"

Before adding functionality, ask:

> "What V1 question does this answer?"

If it does not answer a required V1 question, it belongs in the parking lot.

---

# 30. Final Architectural Summary

Dinner Spinner V1 is intentionally small.

```text
                 ┌──────────────────┐
                 │ InventoryCategory │
                 └────────┬─────────┘
                          │
                          ▼
                   ┌─────────────┐
                   │  Ingredient │
                   │ current     │
                   │ inventory   │
                   └──────▲──────┘
                          │
                 ┌────────┴────────┐
                 │ RecipeIngredient│
                 └────────▲────────┘
                          │
                    ┌─────┴─────┐
                    │   Recipe  │
                    └─────▲─────┘
                          │
                    ┌─────┴─────┐
                    │ MealPlan  │
                    └─────┬─────┘
                          │
                          ▼
                      ┌───────┐
                      │Demand │
                      └───┬───┘
                          │
                          ▼
                 ┌─────────────────┐
                 │ Net Requirement │
                 └────────┬────────┘
                          │
                          ▼
                 ┌────────────────┐
                 │ Shopping List  │
                 │   projection   │
                 └───────┬────────┘
                         │
                       HUMAN
                         │
                         ▼
                  ┌─────────────┐
                  │ Acquisition │
                  └──────┬──────┘
                         │
                         ▼
                    Ingredient
```

Inventory changes:

```text
Acquisition ──► Ingredient.quantity (+)

Consumption ──► Ingredient.quantity (-)

Waste ────────► Ingredient.quantity (-)
```

The central architectural distinction is:

```text
RECIPE
    = what SHOULD be used

MEAL PLAN
    = what we PLAN to make

DEMAND
    = what the plan REQUIRES

INGREDIENT
    = what we CURRENTLY HAVE

ACQUISITION
    = what we ACTUALLY OBTAINED

CONSUMPTION
    = what we ACTUALLY USED

WASTE
    = what we ACTUALLY LOST

SHOPPING LIST
    = what we CURRENTLY NEED TO ACQUIRE
```

Everything else is either calculation, presentation, or future scope.
