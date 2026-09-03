class InventoryCategory:
    """An organizational classification used to group Ingredients for inventory presentation."""

    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name

    def __eq__(self, other):
        if not isinstance(other, InventoryCategory):
            return NotImplemented
        return self.id == other.id and self.name == other.name

    def __repr__(self):
        return f"<InventoryCategory id={self.id} name={self.name!r}>"

    def __hash__(self):
        return hash((self.id, self.name))