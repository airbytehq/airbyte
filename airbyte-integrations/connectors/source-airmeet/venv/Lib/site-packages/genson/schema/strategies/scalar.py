from .base import SchemaStrategy, TypedSchemaStrategy


class Typeless(SchemaStrategy):
    """
    schema strategy for schemas with no type. This is only used when
    there is no other active strategy, and it will be merged into the
    first typed strategy that gets added.
    """

    @classmethod
    def match_schema(cls, schema):
        return 'type' not in schema

    @classmethod
    def match_object(cls, obj):
        return False


class Null(TypedSchemaStrategy):
    """
    strategy for null schemas
    """
    JS_TYPE = 'null'
    PYTHON_TYPE = type(None)


class Boolean(TypedSchemaStrategy):
    """
    strategy for boolean schemas
    """
    JS_TYPE = 'boolean'
    PYTHON_TYPE = bool


class String(TypedSchemaStrategy):
    """
    strategy for string schemas - works for ascii and unicode strings
    """
    JS_TYPE = 'string'
    PYTHON_TYPE = str


class Number(SchemaStrategy):
    """
    strategy for integer and number schemas. It automatically
    converts from `integer` to `number` when a float object or a
    number schema is added
    """
    JS_TYPES = ('integer', 'number')
    PYTHON_TYPES = (int, float)

    @classmethod
    def match_schema(cls, schema):
        return schema.get('type') in cls.JS_TYPES

    @classmethod
    def match_object(cls, obj):
        # cannot use isinstance() because boolean is a subtype of int
        return type(obj) in cls.PYTHON_TYPES

    def __init__(self, node_class):
        super().__init__(node_class)
        self._type = 'integer'

    def add_schema(self, schema):
        super().add_schema(schema)
        if schema.get('type') == 'number':
            self._type = 'number'

    def add_object(self, obj):
        if isinstance(obj, float):
            self._type = 'number'

    def to_schema(self):
        schema = super().to_schema()
        schema['type'] = self._type
        return schema
