from .base import SchemaStrategy


class BaseArray(SchemaStrategy):
    """
    abstract array schema strategy
    """
    KEYWORDS = ('type', 'items')

    @staticmethod
    def match_object(obj):
        return isinstance(obj, list)

    def to_schema(self):
        schema = super().to_schema()
        schema['type'] = 'array'
        if self._items:
            schema['items'] = self.items_to_schema()
        return schema


class List(BaseArray):
    """
    strategy for list-style array schemas. This is the default
    strategy for arrays.
    """
    @staticmethod
    def match_schema(schema):
        return schema.get('type') == 'array' \
            and isinstance(schema.get('items', {}), dict)

    def __init__(self, node_class):
        super().__init__(node_class)
        self._items = node_class()

    def add_schema(self, schema):
        super().add_schema(schema)
        if 'items' in schema:
            self._items.add_schema(schema['items'])

    def add_object(self, obj):
        for item in obj:
            self._items.add_object(item)

    def items_to_schema(self):
        return self._items.to_schema()


class Tuple(BaseArray):
    """
    strategy for tuple-style array schemas. These will always have
    an items key to preserve the fact that it's a tuple.
    """
    @staticmethod
    def match_schema(schema):
        return schema.get('type') == 'array' \
            and isinstance(schema.get('items'), list)

    def __init__(self, node_class):
        super().__init__(node_class)
        self._items = [node_class()]

    def add_schema(self, schema):
        super().add_schema(schema)
        if 'items' in schema:
            self._add(schema['items'], 'add_schema')

    def add_object(self, obj):
        self._add(obj, 'add_object')

    def _add(self, items, func):
        while len(self._items) < len(items):
            self._items.append(self.node_class())

        for subschema, item in zip(self._items, items):
            getattr(subschema, func)(item)

    def items_to_schema(self):
        return [item.to_schema() for item in self._items]
