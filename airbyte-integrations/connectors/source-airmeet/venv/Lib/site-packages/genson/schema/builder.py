import json
from warnings import warn
from .node import SchemaNode
from .strategies import BASIC_SCHEMA_STRATEGIES


class _MetaSchemaBuilder(type):
    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)

        if 'EXTRA_STRATEGIES' in attrs:
            schema_strategies = list(attrs['EXTRA_STRATEGIES'])
            # add in all strategies inherited from base classes
            for base in bases:
                schema_strategies += list(getattr(base, 'STRATEGIES', []))

            unique_schema_strategies = []
            for schema_strategy in schema_strategies:
                if schema_strategy not in unique_schema_strategies:
                    unique_schema_strategies.append(schema_strategy)

            cls.STRATEGIES = tuple(unique_schema_strategies)

        # create a version of SchemaNode loaded with the custom strategies
        cls.NODE_CLASS = type('%sSchemaNode' % name, (SchemaNode,),
                              {'STRATEGIES': cls.STRATEGIES})


class SchemaBuilder(metaclass=_MetaSchemaBuilder):
    """
    ``SchemaBuilder`` is the basic schema generator class.
    ``SchemaBuilder`` instances can be loaded up with existing schemas
    and objects before being serialized.
    """
    DEFAULT_URI = 'http://json-schema.org/schema#'
    NULL_URI = 'NULL'
    NODE_CLASS = SchemaNode
    STRATEGIES = BASIC_SCHEMA_STRATEGIES

    def __init__(self, schema_uri='DEFAULT'):
        """
        :param schema_uri: value of the ``$schema`` keyword. If not
          given, it will use the value of the first available
          ``$schema`` keyword on an added schema or else the default:
          ``'http://json-schema.org/schema#'``. A value of ``False`` or
          ``None`` will direct GenSON to leave out the ``"$schema"``
          keyword.
        """
        if schema_uri is None or schema_uri is False:
            self.schema_uri = self.NULL_URI
        elif schema_uri == 'DEFAULT':
            self.schema_uri = None
        else:
            self.schema_uri = schema_uri

        if not issubclass(self.NODE_CLASS, SchemaNode):
            raise TypeError("NODE_CLASS %r is not a subclass of SchemaNode"
                            % self.NODE_CLASS)
        self._root_node = self.NODE_CLASS()

    def add_schema(self, schema):
        """
        Merge in a JSON schema. This can be a ``dict`` or another
        ``SchemaBuilder``

        :param schema: a JSON Schema

        .. note::
            There is no schema validation. If you pass in a bad schema,
            you might get back a bad schema.
        """
        if isinstance(schema, SchemaBuilder):
            schema_uri = schema.schema_uri
            schema = schema.to_schema()
            if schema_uri is None:
                del schema['$schema']
        elif isinstance(schema, SchemaNode):
            schema = schema.to_schema()

        if '$schema' in schema:
            self.schema_uri = self.schema_uri or schema['$schema']
            schema = dict(schema)
            del schema['$schema']
        self._root_node.add_schema(schema)

    def add_object(self, obj):
        """
        Modify the schema to accommodate an object.

        :param obj: any object or scalar that can be serialized in JSON
        """
        self._root_node.add_object(obj)

    def to_schema(self):
        """
        Generate a schema based on previous inputs.

        :rtype: ``dict``
        """
        schema = self._base_schema()
        schema.update(self._root_node.to_schema())
        return schema

    def to_json(self, *args, **kwargs):
        """
        Generate a schema and convert it directly to serialized JSON.

        :rtype: ``str``
        """
        return json.dumps(self.to_schema(), *args, **kwargs)

    def __len__(self):
        """
        Number of ``SchemaStrategy``s at the top level. This is used
        mostly to check for emptiness.
        """
        return len(self._root_node)

    def __eq__(self, other):
        """
        Check for equality with another ``SchemaBuilder`` object.

        :param other: another ``SchemaBuilder`` object. Other types are
          accepted, but will always return ``False``
        """
        if other is self:
            return True
        if not isinstance(other, self.__class__):
            return False

        # use _base_schema to get proper comparison for $schema keyword
        return (self._base_schema() == other._base_schema()
                and self._root_node == other._root_node)

    def _base_schema(self):
        if self.schema_uri == self.NULL_URI:
            return {}
        else:
            return {'$schema': self.schema_uri or self.DEFAULT_URI}


class Schema(SchemaBuilder):

    def __init__(self):
        warn('genson.Schema is deprecated in v1.0, and it may be '
             'removed in future versions. Use genson.SchemaBuilder'
             'instead.',
             PendingDeprecationWarning)
        super().__init__(schema_uri=SchemaBuilder.NULL_URI)

    def to_dict(self, recurse='DEPRECATED'):
        warn('#to_dict is deprecated in v1.0, and it may be removed in '
             'future versions. Use #to_schema instead.',
             PendingDeprecationWarning)
        if recurse != 'DEPRECATED':
            warn('the `recurse` option for #to_dict does nothing in v1.0',
                 DeprecationWarning)
        return self.to_schema()
