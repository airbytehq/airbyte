from copy import copy
from warnings import warn


class SchemaStrategy:
    """
    base schema strategy. This contains the common interface for
    all subclasses:

    * match_schema
    * match_object
    * __init__
    * add_schema
    * add_object
    * to_schema
    * __eq__
    """
    KEYWORDS = ('type',)

    @classmethod
    def match_schema(cls, schema):
        raise NotImplementedError("'match_schema' not implemented")

    @classmethod
    def match_object(cls, obj):
        raise NotImplementedError("'match_object' not implemented")

    def __init__(self, node_class):
        self.node_class = node_class
        self._extra_keywords = {}

    def add_schema(self, schema):
        self._add_extra_keywords(schema)

    def _add_extra_keywords(self, schema):
        for keyword, value in schema.items():
            if keyword in self.KEYWORDS:
                continue
            elif keyword not in self._extra_keywords:
                self._extra_keywords[keyword] = value
            elif self._extra_keywords[keyword] != value:
                warn(('Schema incompatible. Keyword {0!r} has conflicting '
                      'values ({1!r} vs. {2!r}). Using {1!r}').format(
                          keyword, self._extra_keywords[keyword], value))

    def add_object(self, obj):
        pass

    def to_schema(self):
        return copy(self._extra_keywords)

    def __eq__(self, other):
        """ Required for SchemaBuilder.__eq__ to work properly """
        return (isinstance(other, self.__class__)
                and self.__dict__ == other.__dict__)


class TypedSchemaStrategy(SchemaStrategy):
    """
    base schema strategy class for scalar types. Subclasses define
    these two class constants:

    * `JS_TYPE`: a valid value of the `type` keyword
    * `PYTHON_TYPE`: Python type objects - can be a tuple of types
    """

    @classmethod
    def match_schema(cls, schema):
        return schema.get('type') == cls.JS_TYPE

    @classmethod
    def match_object(cls, obj):
        return isinstance(obj, cls.PYTHON_TYPE)

    def to_schema(self):
        schema = super().to_schema()
        schema['type'] = self.JS_TYPE
        return schema
