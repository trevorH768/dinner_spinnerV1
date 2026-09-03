# Dinner Spinner V1 — OpenCode Project Instructions

## Project Authority

`V1_ARCHITECTURE.md` is the authoritative architecture and domain contract for Dinner Spinner V1.

When implementation, tests, documentation, or assumptions conflict with `V1_ARCHITECTURE.md`, the architecture document wins.

Do not invent missing requirements.

Do not add functionality merely because it seems useful, conventional, scalable, or likely to be needed later.

Before introducing a new entity, field, relationship, service, abstraction, or subsystem, identify the domain responsibility it satisfies and the specific V1 requirement that requires it.

If the requirement is not established, stop and ask.

---

## Project Goal

Dinner Spinner V1 is a meal-planning and food-inventory application.

The current V1 foundation establishes:

- Inventory categories
- Ingredients as physical inventory holdings
- Recipes
- Recipe ingredients
- Meal plans
- A centralized unit-conversion system
- Persistence
- Flask presentation
- Database migrations

Future architecture is explicitly defined in `V1_ARCHITECTURE.md`.

Do not prematurely implement future slices.

In particular, do not introduce future concepts such as:

- Products
- Packages
- Stores
- Brands
- Barcodes
- Prices or price estimates
- Shopping lists
- Demand entities
- Acquisition events
- Consumption events
- Waste events
- Inventory event history

unless the current task explicitly calls for the corresponding architecture slice.

---

## Architecture Boundaries

Dinner Spinner uses a layered architecture:

### Domain

Domain code must remain framework-independent.

Domain modules must not depend on:

- Flask
- SQLAlchemy
- HTTP/request objects
- Templates
- Database sessions
- Persistence models
- External food/product providers

Domain logic belongs in the domain layer when it expresses business rules or calculations.

### Persistence

Persistence code is responsible for:

- Database models
- Relationships
- Foreign keys
- Database constraints
- Mapping between persistence and domain representations
- Schema migrations

Database invariants must not rely solely on presentation-layer behavior.

### Presentation

Presentation code is responsible for:

- HTTP routes
- Forms
- Templates
- User-facing validation and error handling
- Translating user input into valid domain operations

Do not duplicate domain rules in presentation code when doing so creates inconsistent behavior.

---

## V1 Domain Rules

Treat the following as hard invariants.

### Ingredient

An Ingredient represents a user-defined physical inventory holding.

It has:

- `id`
- `name`
- optional inventory category
- current non-negative quantity
- recognized unit

Rules:

- Quantity may be zero.
- Quantity may be decimal.
- Quantity may never be negative.
- Separate Ingredient identities must never be automatically merged.
- An Ingredient must not be recreated or deleted merely because its quantity reaches zero.
- There is no separate Container entity in V1.
- An Ingredient referenced by a RecipeIngredient cannot be deleted.
- Changing an Ingredient's unit must preserve the represented physical quantity through a valid conversion.
- Incompatible conversions must be rejected.
- Density must never be invented or assumed.

### Recipe

A Recipe represents a user-defined preparation specification.

It has:

- `id`
- `name`
- `servings`
- `instructions`
- `created_at`

Rules:

- Servings must be a positive integer.
- Deleting a Recipe deletes its RecipeIngredients.
- Deleting a Recipe must not delete Ingredients.
- Deleting a Recipe must not delete MealPlans.
- MealPlans referencing a deleted Recipe must remain and have `recipe_id = NULL`.

### RecipeIngredient

A RecipeIngredient represents a recipe-specific ingredient requirement.

Rules:

- Quantity must be greater than zero.
- Decimal quantities are valid.
- Unit must be recognized.
- RecipeIngredient units do not need to match the corresponding Ingredient inventory unit.
- Original quantity and unit must be preserved.
- Normalization occurs only when required for calculation.
- A Recipe may contain a given Ingredient only once.
- Deleting a RecipeIngredient must not modify the Ingredient or Recipe.
- Deleting a Recipe cascades to its RecipeIngredients.

### MealPlan

A MealPlan represents a planned recipe assignment for a specific meal slot.

Rules:

- `recipe_id` is nullable.
- Empty meal slots are valid.
- Servings must be a positive integer.
- `(week_start, day, meal_type)` must be unique.
- MealPlans do not contain ingredient quantities.
- MealPlans do not directly modify inventory.
- MealPlans do not store a separate Demand entity.

---

## Unit System

Unit conversion is centralized in the unit system.

Do not create independent conversion tables, helper functions, or ad-hoc conversion logic elsewhere in the application.

The system distinguishes:

- MASS
- VOLUME
- COUNT

Same-category conversions are valid.

Cross-category conversions require explicit valid information.

Never invent density or other missing conversion information.

Do not introduce a universal base unit merely for implementation convenience.

---

## Database Invariants

Important domain invariants must be enforced at the persistence/database level where appropriate, not merely by UI behavior.

Pay particular attention to:

- non-negative Ingredient quantity
- positive Recipe servings
- positive RecipeIngredient quantity
- positive MealPlan servings
- RecipeIngredient uniqueness per Recipe/Ingredient
- MealPlan uniqueness per week/day/meal type
- Recipe deletion semantics
- Ingredient deletion semantics
- MealPlan preservation when Recipes are deleted
- Ingredient preservation when Recipes are deleted
- category deletion behavior
- foreign-key behavior

SQLite-specific behavior must be verified rather than assumed.

---

## Testing Requirements

Tests must prove behavior, not merely reproduce object construction.

When an architecture requirement concerns persistence, relationships, constraints, deletion, or foreign keys, write a persistence/integration test that actually exercises the database behavior.

Do not label a unit test as proving a database invariant if it never interacts with the database.

Tests should cover:

1. Domain validation
2. Unit conversion
3. Persistence constraints
4. Relationship integrity
5. Deletion behavior
6. Domain/persistence boundaries
7. Relevant presentation behavior

When fixing a bug:

1. Reproduce the failure.
2. Add or identify the test that proves the failure.
3. Make the smallest appropriate change.
4. Run the focused test.
5. Run the complete test suite.
6. Inspect the final diff.

---

## Development Workflow

Prefer small, independently verifiable changes.

For architectural work:

1. Read `V1_ARCHITECTURE.md`.
2. Inspect the relevant implementation.
3. Inspect existing tests.
4. Identify the exact invariant or requirement involved.
5. Plan the smallest compliant change.
6. Implement.
7. Add or update tests.
8. Run focused verification.
9. Run the full test suite.
10. Review the diff for unintended changes.

Do not combine unrelated refactors with a bug fix.

Do not perform broad cleanup merely because nearby code could be improved.

Do not change working behavior without identifying the requirement that necessitates the change.

---

## Slice Discipline

The current development target is the **Slice 1 hardening pass**.

Slice 1 hardening means making the existing foundational architecture correct, internally consistent, and verifiable.

The purpose is not to begin implementing Slice 2.

Do not implement future functionality as part of hardening unless it is necessary to correct an existing Slice 1 boundary or invariant.

When uncertain whether a proposed change belongs in Slice 1, explain why before implementing it.

---

## AI Development Rules

The human developer controls scope and architectural decisions.

OpenCode is expected to:

- investigate thoroughly
- identify concrete problems
- explain reasoning
- propose small plans
- implement approved work
- write appropriate tests
- verify its changes

OpenCode must not:

- silently reinterpret requirements
- invent domain concepts
- expand scope
- redesign the architecture
- add speculative abstractions
- implement future slices early
- remove architectural constraints because they are inconvenient
- substitute framework conventions for explicit project requirements

When the architecture appears ambiguous or contradictory, report the ambiguity rather than guessing.

When implementation conflicts with the architecture, adapt the implementation to the architecture unless the human developer explicitly approves changing the architecture document.

---

## Git Discipline

Do not create commits unless explicitly instructed.

Do not push to GitHub unless explicitly instructed.

Before any commit, report:

- what changed
- why it changed
- tests run
- test results
- any remaining concerns

The working tree should remain understandable and reviewable.

---

## Current Hardening Priorities

During the Slice 1 hardening pass, investigate and resolve concrete issues in roughly this order:

1. Application/database session wiring
2. ORM relationship and deletion semantics
3. SQLite foreign-key enforcement
4. Recipe deletion behavior
5. Ingredient deletion behavior
6. Category deletion behavior
7. Ingredient unit-change conversion
8. Domain/persistence/presentation boundary violations
9. Migration/schema authority
10. Persistence tests proving database invariants
11. Full-suite verification
12. Final architecture compliance review

This ordering is a guide, not permission to implement unrelated work.

---

## Definition of Done

Slice 1 hardening is complete only when:

- The implementation conforms to `V1_ARCHITECTURE.md`.
- Foundational domain entities and relationships behave according to the contract.
- Database constraints enforce required invariants.
- Deletion behavior matches the architecture.
- Unit changes preserve represented quantity.
- SQLite foreign-key behavior is verified.
- Persistence tests prove the important database invariants.
- Existing architecture tests remain valid.
- The complete test suite passes.
- No future-slice concepts have been introduced.
- The final diff contains no unrelated changes.
- Any remaining ambiguity or technical debt has been explicitly identified rather than silently ignored.