from collections import defaultdict
from re import search
from .base import SchemaStrategy


class Object(SchemaStrategy):
    """
    object schema strategy
    """
    KEYWORDS = ('type', 'properties', 'patternProperties', 'required')

    @staticmethod
    def match_schema(schema):
        return schema.get('type') == 'object'

    @staticmethod
    def match_object(obj):
        return isinstance(obj, dict)

    def __init__(self, node_class):
        super().__init__(node_class)

        self._properties = defaultdict(node_class)
        self._pattern_properties = defaultdict(node_class)
        self._required = None
        self._include_empty_required = False

    def add_schema(self, schema):
        super().add_schema(schema)
        if 'properties' in schema:
            for prop, subschema in schema['properties'].items():
                subnode = self._properties[prop]
                if subschema is not None:
                    subnode.add_schema(subschema)
        if 'patternProperties' in schema:
            for pattern, subschema in schema['patternProperties'].items():
                subnode = self._pattern_properties[pattern]
                if subschema is not None:
                    subnode.add_schema(subschema)
        if 'required' in schema:
            required = set(schema['required'])
            if not required:
                self._include_empty_required = True
            if self._required is None:
                self._required = required
            else:
                self._required &= required

    def add_object(self, obj):
        properties = set()
        for prop, subobj in obj.items():
            pattern = None

            if prop not in self._properties:
                pattern = self._matching_pattern(prop)

            if pattern is not None:
                self._pattern_properties[pattern].add_object(subobj)
            else:
                properties.add(prop)
                self._properties[prop].add_object(subobj)

        if self._required is None:
            self._required = properties
        else:
            self._required &= properties

    def _matching_pattern(self, prop):
        for pattern in self._pattern_properties.keys():
            if search(pattern, prop):
                return pattern

    def _add(self, items, func):
        while len(self._items) < len(items):
            self._items.append(self._schema_node_class())

        for subschema, item in zip(self._items, items):
            getattr(subschema, func)(item)

    def to_schema(self):
        schema = super().to_schema()
        schema['type'] = 'object'
        if self._properties:
            schema['properties'] = self._properties_to_schema(
                self._properties)
        if self._pattern_properties:
            schema['patternProperties'] = self._properties_to_schema(
                self._pattern_properties)
        if self._required or self._include_empty_required:
            schema['required'] = sorted(self._required)
        return schema

    def _properties_to_schema(self, properties):
        schema_properties = {}
        for prop, schema_node in properties.items():
            schema_properties[prop] = schema_node.to_schema()
        return schema_properties
