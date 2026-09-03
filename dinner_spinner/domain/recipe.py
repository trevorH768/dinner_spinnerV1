class Recipe:
    """A user-defined preparation specification that identifies a dish or food
    preparation by name, defines its base serving yield and preparation
    instructions, and identifies the Ingredients and quantities required to
    produce that yield.

    Recipe does not represent inventory, purchasing, a meal plan, or demand.
    It does not contain product, package, store, brand, barcode, or availability
    data.
    """

    def __init__(self, id: int, name: str, servings: int, instructions: str | None = None):
        if not name or not name.strip():
            raise ValueError("Recipe name is required")
        if servings is None or servings <= 0:
            raise ValueError("Recipe servings must be greater than zero")
        self.id = id
        self.name = name.strip()
        self.servings = servings
        self.instructions = instructions.strip() if instructions else None
        self.created_at = None  # will be set by persistence layer

    def __eq__(self, other):
        if not isinstance(other, Recipe):
            return NotImplemented
        return (self.id == other.id and self.name == other.name
                and self.servings == other.servings
                and self.instructions == other.instructions)

    def __repr__(self):
        return f"<Recipe id={self.id} name={self.name!r} servings={self.servings}>"

    def __hash__(self):
        return hash((self.id, self.name, self.servings))