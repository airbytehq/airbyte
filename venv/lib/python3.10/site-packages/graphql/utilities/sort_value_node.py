from copy import copy
from typing import Tuple

from ..language import ListValueNode, ObjectFieldNode, ObjectValueNode, ValueNode
from ..pyutils import natural_comparison_key

__all__ = ["sort_value_node"]


def sort_value_node(value_node: ValueNode) -> ValueNode:
    """Sort ValueNode.

    This function returns a sorted copy of the given ValueNode

    For internal use only.
    """
    if isinstance(value_node, ObjectValueNode):
        value_node = copy(value_node)
        value_node.fields = sort_fields(value_node.fields)
    elif isinstance(value_node, ListValueNode):
        value_node = copy(value_node)
        value_node.values = tuple(sort_value_node(value) for value in value_node.values)
    return value_node


def sort_field(field: ObjectFieldNode) -> ObjectFieldNode:
    field = copy(field)
    field.value = sort_value_node(field.value)
    return field


def sort_fields(fields: Tuple[ObjectFieldNode, ...]) -> Tuple[ObjectFieldNode, ...]:
    return tuple(
        sorted(
            (sort_field(field) for field in fields),
            key=lambda field: natural_comparison_key(field.name.value),
        )
    )
