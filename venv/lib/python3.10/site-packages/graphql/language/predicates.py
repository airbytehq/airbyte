from .ast import (
    Node,
    DefinitionNode,
    ExecutableDefinitionNode,
    ListValueNode,
    ObjectValueNode,
    SchemaExtensionNode,
    SelectionNode,
    TypeDefinitionNode,
    TypeExtensionNode,
    TypeNode,
    TypeSystemDefinitionNode,
    ValueNode,
    VariableNode,
)

__all__ = [
    "is_definition_node",
    "is_executable_definition_node",
    "is_selection_node",
    "is_value_node",
    "is_const_value_node",
    "is_type_node",
    "is_type_system_definition_node",
    "is_type_definition_node",
    "is_type_system_extension_node",
    "is_type_extension_node",
]


def is_definition_node(node: Node) -> bool:
    """Check whether the given node represents a definition."""
    return isinstance(node, DefinitionNode)


def is_executable_definition_node(node: Node) -> bool:
    """Check whether the given node represents an executable definition."""
    return isinstance(node, ExecutableDefinitionNode)


def is_selection_node(node: Node) -> bool:
    """Check whether the given node represents a selection."""
    return isinstance(node, SelectionNode)


def is_value_node(node: Node) -> bool:
    """Check whether the given node represents a value."""
    return isinstance(node, ValueNode)


def is_const_value_node(node: Node) -> bool:
    """Check whether the given node represents a constant value."""
    return is_value_node(node) and (
        any(is_const_value_node(value) for value in node.values)
        if isinstance(node, ListValueNode)
        else any(is_const_value_node(field.value) for field in node.fields)
        if isinstance(node, ObjectValueNode)
        else not isinstance(node, VariableNode)
    )


def is_type_node(node: Node) -> bool:
    """Check whether the given node represents a type."""
    return isinstance(node, TypeNode)


def is_type_system_definition_node(node: Node) -> bool:
    """Check whether the given node represents a type system definition."""
    return isinstance(node, TypeSystemDefinitionNode)


def is_type_definition_node(node: Node) -> bool:
    """Check whether the given node represents a type definition."""
    return isinstance(node, TypeDefinitionNode)


def is_type_system_extension_node(node: Node) -> bool:
    """Check whether the given node represents a type system extension."""
    return isinstance(node, (SchemaExtensionNode, TypeExtensionNode))


def is_type_extension_node(node: Node) -> bool:
    """Check whether the given node represents a type extension."""
    return isinstance(node, TypeExtensionNode)
