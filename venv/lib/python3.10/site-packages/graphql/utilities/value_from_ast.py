from typing import Any, Dict, List, Optional, cast

from ..language import (
    ListValueNode,
    NullValueNode,
    ObjectValueNode,
    ValueNode,
    VariableNode,
)
from ..pyutils import inspect, Undefined
from ..type import (
    GraphQLInputObjectType,
    GraphQLInputType,
    GraphQLList,
    GraphQLNonNull,
    GraphQLScalarType,
    is_input_object_type,
    is_leaf_type,
    is_list_type,
    is_non_null_type,
)

__all__ = ["value_from_ast"]


def value_from_ast(
    value_node: Optional[ValueNode],
    type_: GraphQLInputType,
    variables: Optional[Dict[str, Any]] = None,
) -> Any:
    """Produce a Python value given a GraphQL Value AST.

    A GraphQL type must be provided, which will be used to interpret different GraphQL
    Value literals.

    Returns ``Undefined`` when the value could not be validly coerced according
    to the provided type.

    =================== ============== ================
       GraphQL Value      JSON Value     Python Value
    =================== ============== ================
       Input Object       Object         dict
       List               Array          list
       Boolean            Boolean        bool
       String             String         str
       Int / Float        Number         int / float
       Enum Value         Mixed          Any
       NullValue          null           None
    =================== ============== ================

    """
    if not value_node:
        # When there is no node, then there is also no value.
        # Importantly, this is different from returning the value null.
        return Undefined

    if isinstance(value_node, VariableNode):
        variable_name = value_node.name.value
        if not variables:
            return Undefined
        variable_value = variables.get(variable_name, Undefined)
        if variable_value is None and is_non_null_type(type_):
            return Undefined
        # Note: This does no further checking that this variable is correct.
        # This assumes that this query has been validated and the variable usage here
        # is of the correct type.
        return variable_value

    if is_non_null_type(type_):
        if isinstance(value_node, NullValueNode):
            return Undefined
        type_ = cast(GraphQLNonNull, type_)
        return value_from_ast(value_node, type_.of_type, variables)

    if isinstance(value_node, NullValueNode):
        return None  # This is explicitly returning the value None.

    if is_list_type(type_):
        type_ = cast(GraphQLList, type_)
        item_type = type_.of_type
        if isinstance(value_node, ListValueNode):
            coerced_values: List[Any] = []
            append_value = coerced_values.append
            for item_node in value_node.values:
                if is_missing_variable(item_node, variables):
                    # If an array contains a missing variable, it is either coerced to
                    # None or if the item type is non-null, it is considered invalid.
                    if is_non_null_type(item_type):
                        return Undefined
                    append_value(None)
                else:
                    item_value = value_from_ast(item_node, item_type, variables)
                    if item_value is Undefined:
                        return Undefined
                    append_value(item_value)
            return coerced_values
        coerced_value = value_from_ast(value_node, item_type, variables)
        if coerced_value is Undefined:
            return Undefined
        return [coerced_value]

    if is_input_object_type(type_):
        if not isinstance(value_node, ObjectValueNode):
            return Undefined
        type_ = cast(GraphQLInputObjectType, type_)
        coerced_obj: Dict[str, Any] = {}
        fields = type_.fields
        field_nodes = {field.name.value: field for field in value_node.fields}
        for field_name, field in fields.items():
            field_node = field_nodes.get(field_name)
            if not field_node or is_missing_variable(field_node.value, variables):
                if field.default_value is not Undefined:
                    # Use out name as name if it exists (extension of GraphQL.js).
                    coerced_obj[field.out_name or field_name] = field.default_value
                elif is_non_null_type(field.type):  # pragma: no cover else
                    return Undefined
                continue
            field_value = value_from_ast(field_node.value, field.type, variables)
            if field_value is Undefined:
                return Undefined
            coerced_obj[field.out_name or field_name] = field_value

        return type_.out_type(coerced_obj)

    if is_leaf_type(type_):
        # Scalars fulfill parsing a literal value via `parse_literal()`. Invalid values
        # represent a failure to parse correctly, in which case Undefined is returned.
        type_ = cast(GraphQLScalarType, type_)
        # noinspection PyBroadException
        try:
            if variables:
                result = type_.parse_literal(value_node, variables)
            else:
                result = type_.parse_literal(value_node)
        except Exception:
            return Undefined
        return result

    # Not reachable. All possible input types have been considered.
    raise TypeError(f"Unexpected input type: {inspect(type_)}.")


def is_missing_variable(
    value_node: ValueNode, variables: Optional[Dict[str, Any]] = None
) -> bool:
    """Check if ``value_node`` is a variable not defined in the ``variables`` dict."""
    return isinstance(value_node, VariableNode) and (
        not variables or variables.get(value_node.name.value, Undefined) is Undefined
    )
