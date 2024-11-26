from math import nan
from typing import Any, Callable, Dict, Optional, Union

from ..language import (
    ValueNode,
    BooleanValueNode,
    EnumValueNode,
    FloatValueNode,
    IntValueNode,
    ListValueNode,
    NullValueNode,
    ObjectValueNode,
    StringValueNode,
    VariableNode,
)

from ..pyutils import inspect, Undefined

__all__ = ["value_from_ast_untyped"]


def value_from_ast_untyped(
    value_node: ValueNode, variables: Optional[Dict[str, Any]] = None
) -> Any:
    """Produce a Python value given a GraphQL Value AST.

    Unlike :func:`~graphql.utilities.value_from_ast`, no type is provided.
    The resulting Python value will reflect the provided GraphQL value AST.

    =================== ============== ================
       GraphQL Value      JSON Value     Python Value
    =================== ============== ================
       Input Object       Object         dict
       List               Array          list
       Boolean            Boolean        bool
       String / Enum      String         str
       Int / Float        Number         int / float
       Null               null           None
    =================== ============== ================

    """
    func = _value_from_kind_functions.get(value_node.kind)
    if func:
        return func(value_node, variables)

    # Not reachable. All possible value nodes have been considered.
    raise TypeError(  # pragma: no cover
        f"Unexpected value node: {inspect(value_node)}."
    )


def value_from_null(_value_node: NullValueNode, _variables: Any) -> Any:
    return None


def value_from_int(value_node: IntValueNode, _variables: Any) -> Any:
    try:
        return int(value_node.value)
    except ValueError:
        return nan


def value_from_float(value_node: FloatValueNode, _variables: Any) -> Any:
    try:
        return float(value_node.value)
    except ValueError:
        return nan


def value_from_string(
    value_node: Union[BooleanValueNode, EnumValueNode, StringValueNode], _variables: Any
) -> Any:
    return value_node.value


def value_from_list(
    value_node: ListValueNode, variables: Optional[Dict[str, Any]]
) -> Any:
    return [value_from_ast_untyped(node, variables) for node in value_node.values]


def value_from_object(
    value_node: ObjectValueNode, variables: Optional[Dict[str, Any]]
) -> Any:
    return {
        field.name.value: value_from_ast_untyped(field.value, variables)
        for field in value_node.fields
    }


def value_from_variable(
    value_node: VariableNode, variables: Optional[Dict[str, Any]]
) -> Any:
    variable_name = value_node.name.value
    if not variables:
        return Undefined
    return variables.get(variable_name, Undefined)


_value_from_kind_functions: Dict[str, Callable] = {
    "null_value": value_from_null,
    "int_value": value_from_int,
    "float_value": value_from_float,
    "string_value": value_from_string,
    "enum_value": value_from_string,
    "boolean_value": value_from_string,
    "list_value": value_from_list,
    "object_value": value_from_object,
    "variable": value_from_variable,
}
