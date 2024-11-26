from enum import Enum

__all__ = ["DirectiveLocation"]


class DirectiveLocation(Enum):
    """The enum type representing the directive location values."""

    # Request Definitions
    QUERY = "query"
    MUTATION = "mutation"
    SUBSCRIPTION = "subscription"
    FIELD = "field"
    FRAGMENT_DEFINITION = "fragment definition"
    FRAGMENT_SPREAD = "fragment spread"
    VARIABLE_DEFINITION = "variable definition"
    INLINE_FRAGMENT = "inline fragment"

    # Type System Definitions
    SCHEMA = "schema"
    SCALAR = "scalar"
    OBJECT = "object"
    FIELD_DEFINITION = "field definition"
    ARGUMENT_DEFINITION = "argument definition"
    INTERFACE = "interface"
    UNION = "union"
    ENUM = "enum"
    ENUM_VALUE = "enum value"
    INPUT_OBJECT = "input object"
    INPUT_FIELD_DEFINITION = "input field definition"
