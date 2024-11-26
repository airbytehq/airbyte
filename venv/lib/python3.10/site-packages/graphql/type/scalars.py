from math import isfinite
from typing import Any, Mapping

from ..error import GraphQLError
from ..pyutils import inspect
from ..language.ast import (
    BooleanValueNode,
    FloatValueNode,
    IntValueNode,
    StringValueNode,
    ValueNode,
)
from ..language.printer import print_ast
from .definition import GraphQLNamedType, GraphQLScalarType

__all__ = [
    "is_specified_scalar_type",
    "specified_scalar_types",
    "GraphQLInt",
    "GraphQLFloat",
    "GraphQLString",
    "GraphQLBoolean",
    "GraphQLID",
    "GRAPHQL_MAX_INT",
    "GRAPHQL_MIN_INT",
]

# As per the GraphQL Spec, Integers are only treated as valid
# when they can be represented as a 32-bit signed integer,
# providing the broadest support across platforms.
# n.b. JavaScript's numbers are safe between -(2^53 - 1) and 2^53 - 1
# because they are internally represented as IEEE 754 doubles,
# while Python's integers may be arbitrarily large.

GRAPHQL_MAX_INT = 2_147_483_647
"""Maximum possible Int value as per GraphQL Spec (32-bit signed integer)"""

GRAPHQL_MIN_INT = -2_147_483_648
"""Minimum possible Int value as per GraphQL Spec (32-bit signed integer)"""


def serialize_int(output_value: Any) -> int:
    if isinstance(output_value, bool):
        return 1 if output_value else 0
    try:
        if isinstance(output_value, int):
            num = output_value
        elif isinstance(output_value, float):
            num = int(output_value)
            if num != output_value:
                raise ValueError
        elif not output_value and isinstance(output_value, str):
            output_value = ""
            raise ValueError
        else:
            num = int(output_value)  # raises ValueError if not an integer
    except (OverflowError, ValueError, TypeError):
        raise GraphQLError(
            "Int cannot represent non-integer value: " + inspect(output_value)
        )
    if not GRAPHQL_MIN_INT <= num <= GRAPHQL_MAX_INT:
        raise GraphQLError(
            "Int cannot represent non 32-bit signed integer value: "
            + inspect(output_value)
        )
    return num


def coerce_int(input_value: Any) -> int:
    if not (
        isinstance(input_value, int) and not isinstance(input_value, bool)
    ) and not (
        isinstance(input_value, float)
        and isfinite(input_value)
        and int(input_value) == input_value
    ):
        raise GraphQLError(
            "Int cannot represent non-integer value: " + inspect(input_value)
        )
    if not GRAPHQL_MIN_INT <= input_value <= GRAPHQL_MAX_INT:
        raise GraphQLError(
            "Int cannot represent non 32-bit signed integer value: "
            + inspect(input_value)
        )
    return int(input_value)


def parse_int_literal(value_node: ValueNode, _variables: Any = None) -> int:
    """Parse an integer value node in the AST."""
    if not isinstance(value_node, IntValueNode):
        raise GraphQLError(
            "Int cannot represent non-integer value: " + print_ast(value_node),
            value_node,
        )
    num = int(value_node.value)
    if not GRAPHQL_MIN_INT <= num <= GRAPHQL_MAX_INT:
        raise GraphQLError(
            "Int cannot represent non 32-bit signed integer value: "
            + print_ast(value_node),
            value_node,
        )
    return num


GraphQLInt = GraphQLScalarType(
    name="Int",
    description="The `Int` scalar type represents"
    " non-fractional signed whole numeric values."
    " Int can represent values between -(2^31) and 2^31 - 1.",
    serialize=serialize_int,
    parse_value=coerce_int,
    parse_literal=parse_int_literal,
)


def serialize_float(output_value: Any) -> float:
    if isinstance(output_value, bool):
        return 1 if output_value else 0
    try:
        if not output_value and isinstance(output_value, str):
            output_value = ""
            raise ValueError
        num = output_value if isinstance(output_value, float) else float(output_value)
        if not isfinite(num):
            raise ValueError
    except (ValueError, TypeError):
        raise GraphQLError(
            "Float cannot represent non numeric value: " + inspect(output_value)
        )
    return num


def coerce_float(input_value: Any) -> float:
    if not (
        isinstance(input_value, int) and not isinstance(input_value, bool)
    ) and not (isinstance(input_value, float) and isfinite(input_value)):
        raise GraphQLError(
            "Float cannot represent non numeric value: " + inspect(input_value)
        )
    return float(input_value)


def parse_float_literal(value_node: ValueNode, _variables: Any = None) -> float:
    """Parse a float value node in the AST."""
    if not isinstance(value_node, (FloatValueNode, IntValueNode)):
        raise GraphQLError(
            "Float cannot represent non numeric value: " + print_ast(value_node),
            value_node,
        )
    return float(value_node.value)


GraphQLFloat = GraphQLScalarType(
    name="Float",
    description="The `Float` scalar type represents"
    " signed double-precision fractional values"
    " as specified by [IEEE 754]"
    "(https://en.wikipedia.org/wiki/IEEE_floating_point).",
    serialize=serialize_float,
    parse_value=coerce_float,
    parse_literal=parse_float_literal,
)


def serialize_string(output_value: Any) -> str:
    if isinstance(output_value, str):
        return output_value
    if isinstance(output_value, bool):
        return "true" if output_value else "false"
    if isinstance(output_value, int) or (
        isinstance(output_value, float) and isfinite(output_value)
    ):
        return str(output_value)
    # do not serialize builtin types as strings, but allow serialization of custom
    # types via their `__str__` method
    if type(output_value).__module__ == "builtins":
        raise GraphQLError("String cannot represent value: " + inspect(output_value))
    return str(output_value)


def coerce_string(input_value: Any) -> str:
    if not isinstance(input_value, str):
        raise GraphQLError(
            "String cannot represent a non string value: " + inspect(input_value)
        )
    return input_value


def parse_string_literal(value_node: ValueNode, _variables: Any = None) -> str:
    """Parse a string value node in the AST."""
    if not isinstance(value_node, StringValueNode):
        raise GraphQLError(
            "String cannot represent a non string value: " + print_ast(value_node),
            value_node,
        )
    return value_node.value


GraphQLString = GraphQLScalarType(
    name="String",
    description="The `String` scalar type represents textual data,"
    " represented as UTF-8 character sequences."
    " The String type is most often used by GraphQL"
    " to represent free-form human-readable text.",
    serialize=serialize_string,
    parse_value=coerce_string,
    parse_literal=parse_string_literal,
)


def serialize_boolean(output_value: Any) -> bool:
    if isinstance(output_value, bool):
        return output_value
    if isinstance(output_value, int) or (
        isinstance(output_value, float) and isfinite(output_value)
    ):
        return bool(output_value)
    raise GraphQLError(
        "Boolean cannot represent a non boolean value: " + inspect(output_value)
    )


def coerce_boolean(input_value: Any) -> bool:
    if not isinstance(input_value, bool):
        raise GraphQLError(
            "Boolean cannot represent a non boolean value: " + inspect(input_value)
        )
    return input_value


def parse_boolean_literal(value_node: ValueNode, _variables: Any = None) -> bool:
    """Parse a boolean value node in the AST."""
    if not isinstance(value_node, BooleanValueNode):
        raise GraphQLError(
            "Boolean cannot represent a non boolean value: " + print_ast(value_node),
            value_node,
        )
    return value_node.value


GraphQLBoolean = GraphQLScalarType(
    name="Boolean",
    description="The `Boolean` scalar type represents `true` or `false`.",
    serialize=serialize_boolean,
    parse_value=coerce_boolean,
    parse_literal=parse_boolean_literal,
)


def serialize_id(output_value: Any) -> str:
    if isinstance(output_value, str):
        return output_value
    if isinstance(output_value, int) and not isinstance(output_value, bool):
        return str(output_value)
    if (
        isinstance(output_value, float)
        and isfinite(output_value)
        and int(output_value) == output_value
    ):
        return str(int(output_value))
    # do not serialize builtin types as IDs, but allow serialization of custom types
    # via their `__str__` method
    if type(output_value).__module__ == "builtins":
        raise GraphQLError("ID cannot represent value: " + inspect(output_value))
    return str(output_value)


def coerce_id(input_value: Any) -> str:
    if isinstance(input_value, str):
        return input_value
    if isinstance(input_value, int) and not isinstance(input_value, bool):
        return str(input_value)
    if (
        isinstance(input_value, float)
        and isfinite(input_value)
        and int(input_value) == input_value
    ):
        return str(int(input_value))
    raise GraphQLError("ID cannot represent value: " + inspect(input_value))


def parse_id_literal(value_node: ValueNode, _variables: Any = None) -> str:
    """Parse an ID value node in the AST."""
    if not isinstance(value_node, (StringValueNode, IntValueNode)):
        raise GraphQLError(
            "ID cannot represent a non-string and non-integer value: "
            + print_ast(value_node),
            value_node,
        )
    return value_node.value


GraphQLID = GraphQLScalarType(
    name="ID",
    description="The `ID` scalar type represents a unique identifier,"
    " often used to refetch an object or as key for a cache."
    " The ID type appears in a JSON response as a String; however,"
    " it is not intended to be human-readable. When expected as an"
    ' input type, any string (such as `"4"`) or integer (such as'
    " `4`) input value will be accepted as an ID.",
    serialize=serialize_id,
    parse_value=coerce_id,
    parse_literal=parse_id_literal,
)


specified_scalar_types: Mapping[str, GraphQLScalarType] = {
    type_.name: type_
    for type_ in (
        GraphQLString,
        GraphQLInt,
        GraphQLFloat,
        GraphQLBoolean,
        GraphQLID,
    )
}


def is_specified_scalar_type(type_: GraphQLNamedType) -> bool:
    """Check whether the given named GraphQL type is a specified scalar type."""
    return type_.name in specified_scalar_types
