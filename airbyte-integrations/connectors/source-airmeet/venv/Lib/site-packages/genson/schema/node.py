from .strategies import BASIC_SCHEMA_STRATEGIES, Typeless


class SchemaGenerationError(RuntimeError):
    pass


class SchemaNode:
    """
    Basic schema generator class. SchemaNode objects can be loaded
    up with existing schemas and objects before being serialized.
    """
    STRATEGIES = BASIC_SCHEMA_STRATEGIES

    def __init__(self):
        self._active_strategies = []

    def add_schema(self, schema):
        """
        Merges in an existing schema.

        arguments:
        * `schema` (required - `dict` or `SchemaNode`):
          an existing JSON Schema to merge.
        """

        # serialize instances of SchemaNode before parsing
        if isinstance(schema, SchemaNode):
            schema = schema.to_schema()

        for subschema in self._get_subschemas(schema):
            # delegate to SchemaType object
            active_strategy = self._get_strategy_for_schema(subschema)
            active_strategy.add_schema(subschema)

        # return self for easy method chaining
        return self

    def add_object(self, obj):
        """
        Modify the schema to accommodate an object.

        arguments:
        * `obj` (required - `dict`):
          a JSON object to use in generating the schema.
        """

        # delegate to SchemaType object
        active_strategy = self._get_strategy_for_object(obj)
        active_strategy.add_object(obj)

        # return self for easy method chaining
        return self

    def to_schema(self):
        """
        Convert the current schema to a `dict`.
        """
        types = set()
        generated_schemas = []
        for active_strategy in self._active_strategies:
            generated_schema = active_strategy.to_schema()
            if len(generated_schema) == 1 and 'type' in generated_schema:
                types.add(generated_schema['type'])
            else:
                generated_schemas.append(generated_schema)

        if types:
            if len(types) == 1:
                (types,) = types
            else:
                types = sorted(types)
            generated_schemas = [{'type': types}] + generated_schemas
        if len(generated_schemas) == 1:
            (result_schema,) = generated_schemas
        elif generated_schemas:
            result_schema = {'anyOf': generated_schemas}
        else:
            result_schema = {}

        return result_schema

    def __len__(self):
        return len(self._active_strategies)

    def __eq__(self, other):
        """ Required for SchemaBuilder.__eq__ to work properly """
        return (isinstance(other, self.__class__)
                and self.__dict__ == other.__dict__)

    # private methods

    def _get_subschemas(self, schema):
        if 'anyOf' in schema:
            return [subschema for anyof in schema['anyOf']
                    for subschema in self._get_subschemas(anyof)]
        elif isinstance(schema.get('type'), list):
            other_keys = dict(schema)
            del other_keys['type']
            return [dict(type=tipe, **other_keys) for tipe in schema['type']]
        else:
            return [schema]

    def _get_strategy_for_schema(self, schema):
        return self._get_strategy_for_('schema', schema)

    def _get_strategy_for_object(self, obj):
        return self._get_strategy_for_('object', obj)

    def _get_strategy_for_(self, kind, schema_or_obj):
        # check existing types
        for active_strategy in self._active_strategies:
            if getattr(active_strategy, 'match_' + kind)(schema_or_obj):
                return active_strategy

        # check all potential types
        for strategy in self.STRATEGIES:
            if getattr(strategy, 'match_' + kind)(schema_or_obj):
                active_strategy = strategy(self.__class__)

                # incorporate typeless strategy if it exists
                if self._active_strategies and \
                        isinstance(self._active_strategies[-1], Typeless):
                    typeless = self._active_strategies.pop()
                    active_strategy.add_schema(typeless.to_schema())

                self._active_strategies.append(active_strategy)
                return active_strategy

        # no match found, if typeless add to first strategy
        if kind == 'schema' and Typeless.match_schema(schema_or_obj):
            if not self._active_strategies:
                self._active_strategies.append(Typeless(self.__class__))
            active_strategy = self._active_strategies[0]
            return active_strategy

        # no match found, raise an error
        raise SchemaGenerationError(
            'Could not find matching schema type for {0}: {1!r}'.format(
                kind, schema_or_obj))
