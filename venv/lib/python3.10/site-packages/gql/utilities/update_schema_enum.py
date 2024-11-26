from enum import Enum
from typing import Any, Dict, Mapping, Type, Union, cast

from graphql import GraphQLEnumType, GraphQLSchema


def update_schema_enum(
    schema: GraphQLSchema,
    name: str,
    values: Union[Dict[str, Any], Type[Enum]],
    use_enum_values: bool = False,
):
    """Update in the schema the GraphQLEnumType corresponding to the given name.

    Example::

        from enum import Enum

        class Color(Enum):
            RED = 0
            GREEN = 1
            BLUE = 2

        update_schema_enum(schema, 'Color', Color)

    :param schema: a GraphQL Schema already containing the GraphQLEnumType type.
    :param name: the name of the enum in the GraphQL schema
    :param values: Either a Python Enum or a dict of values. The keys of the provided
        values should correspond to the keys of the existing enum in the schema.
    :param use_enum_values: By default, we configure the GraphQLEnumType to serialize
        to enum instances (ie: .parse_value() returns Color.RED).
        If use_enum_values is set to True, then .parse_value() returns 0.
        use_enum_values=True is the defaut behaviour when passing an Enum
        to a GraphQLEnumType.
    """

    # Convert Enum values to Dict
    if isinstance(values, type):
        if issubclass(values, Enum):
            values = cast(Type[Enum], values)
            if use_enum_values:
                values = {enum.name: enum.value for enum in values}
            else:
                values = {enum.name: enum for enum in values}

    if not isinstance(values, Mapping):
        raise TypeError(f"Invalid type for enum values: {type(values)}")

    # Find enum type in schema
    schema_enum = schema.get_type(name)

    if schema_enum is None:
        raise KeyError(f"Enum {name} not found in schema!")

    if not isinstance(schema_enum, GraphQLEnumType):
        raise TypeError(
            f'The type "{name}" is not a GraphQLEnumType, it is a {type(schema_enum)}'
        )

    # Replace all enum values
    for enum_name, enum_value in schema_enum.values.items():
        try:
            enum_value.value = values[enum_name]
        except KeyError:
            raise KeyError(f'Enum key "{enum_name}" not found in provided values!')

    # Delete the _value_lookup cached property
    if "_value_lookup" in schema_enum.__dict__:
        del schema_enum.__dict__["_value_lookup"]
