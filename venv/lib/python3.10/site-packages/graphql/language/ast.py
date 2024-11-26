from copy import copy, deepcopy
from enum import Enum
from typing import Any, Dict, List, Tuple, Optional, Union

from .source import Source
from .token_kind import TokenKind
from ..pyutils import camel_to_snake

__all__ = [
    "Location",
    "Token",
    "Node",
    "NameNode",
    "DocumentNode",
    "DefinitionNode",
    "ExecutableDefinitionNode",
    "OperationDefinitionNode",
    "VariableDefinitionNode",
    "SelectionSetNode",
    "SelectionNode",
    "FieldNode",
    "ArgumentNode",
    "ConstArgumentNode",
    "FragmentSpreadNode",
    "InlineFragmentNode",
    "FragmentDefinitionNode",
    "ValueNode",
    "ConstValueNode",
    "VariableNode",
    "IntValueNode",
    "FloatValueNode",
    "StringValueNode",
    "BooleanValueNode",
    "NullValueNode",
    "EnumValueNode",
    "ListValueNode",
    "ConstListValueNode",
    "ObjectValueNode",
    "ConstObjectValueNode",
    "ObjectFieldNode",
    "ConstObjectFieldNode",
    "DirectiveNode",
    "ConstDirectiveNode",
    "TypeNode",
    "NamedTypeNode",
    "ListTypeNode",
    "NonNullTypeNode",
    "TypeSystemDefinitionNode",
    "SchemaDefinitionNode",
    "OperationType",
    "OperationTypeDefinitionNode",
    "TypeDefinitionNode",
    "ScalarTypeDefinitionNode",
    "ObjectTypeDefinitionNode",
    "FieldDefinitionNode",
    "InputValueDefinitionNode",
    "InterfaceTypeDefinitionNode",
    "UnionTypeDefinitionNode",
    "EnumTypeDefinitionNode",
    "EnumValueDefinitionNode",
    "InputObjectTypeDefinitionNode",
    "DirectiveDefinitionNode",
    "SchemaExtensionNode",
    "TypeExtensionNode",
    "TypeSystemExtensionNode",
    "ScalarTypeExtensionNode",
    "ObjectTypeExtensionNode",
    "InterfaceTypeExtensionNode",
    "UnionTypeExtensionNode",
    "EnumTypeExtensionNode",
    "InputObjectTypeExtensionNode",
    "QUERY_DOCUMENT_KEYS",
]


class Token:
    """AST Token

    Represents a range of characters represented by a lexical token within a Source.
    """

    __slots__ = "kind", "start", "end", "line", "column", "prev", "next", "value"

    kind: TokenKind  # the kind of token
    start: int  # the character offset at which this Node begins
    end: int  # the character offset at which this Node ends
    line: int  # the 1-indexed line number on which this Token appears
    column: int  # the 1-indexed column number at which this Token begins
    # for non-punctuation tokens, represents the interpreted value of the token:
    value: Optional[str]
    # Tokens exist as nodes in a double-linked-list amongst all tokens including
    # ignored tokens. <SOF> is always the first node and <EOF> the last.
    prev: Optional["Token"]
    next: Optional["Token"]

    def __init__(
        self,
        kind: TokenKind,
        start: int,
        end: int,
        line: int,
        column: int,
        value: Optional[str] = None,
    ) -> None:
        self.kind = kind
        self.start, self.end = start, end
        self.line, self.column = line, column
        self.value = value
        self.prev = self.next = None

    def __str__(self) -> str:
        return self.desc

    def __repr__(self) -> str:
        """Print a simplified form when appearing in repr() or inspect()."""
        return f"<Token {self.desc} {self.line}:{self.column}>"

    def __inspect__(self) -> str:
        return repr(self)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Token):
            return (
                self.kind == other.kind
                and self.start == other.start
                and self.end == other.end
                and self.line == other.line
                and self.column == other.column
                and self.value == other.value
            )
        elif isinstance(other, str):
            return other == self.desc
        return False

    def __hash__(self) -> int:
        return hash(
            (self.kind, self.start, self.end, self.line, self.column, self.value)
        )

    def __copy__(self) -> "Token":
        """Create a shallow copy of the token"""
        token = self.__class__(
            self.kind,
            self.start,
            self.end,
            self.line,
            self.column,
            self.value,
        )
        token.prev = self.prev
        return token

    def __deepcopy__(self, memo: Dict) -> "Token":
        """Allow only shallow copies to avoid recursion."""
        return copy(self)

    def __getstate__(self) -> Dict[str, Any]:
        """Remove the links when pickling.

        Keeping the links would make pickling a schema too expensive.
        """
        return {
            key: getattr(self, key)
            for key in self.__slots__
            if key not in {"prev", "next"}
        }

    def __setstate__(self, state: Dict[str, Any]) -> None:
        """Reset the links when un-pickling."""
        for key, value in state.items():
            setattr(self, key, value)
        self.prev = self.next = None

    @property
    def desc(self) -> str:
        """A helper property to describe a token as a string for debugging"""
        kind, value = self.kind.value, self.value
        return f"{kind} {value!r}" if value else kind


class Location:
    """AST Location

    Contains a range of UTF-8 character offsets and token references that identify the
    region of the source from which the AST derived.
    """

    __slots__ = (
        "start",
        "end",
        "start_token",
        "end_token",
        "source",
    )

    start: int  # character offset at which this Node begins
    end: int  # character offset at which this Node ends
    start_token: Token  # Token at which this Node begins
    end_token: Token  # Token at which this Node ends.
    source: Source  # Source document the AST represents

    def __init__(self, start_token: Token, end_token: Token, source: Source) -> None:
        self.start = start_token.start
        self.end = end_token.end
        self.start_token = start_token
        self.end_token = end_token
        self.source = source

    def __str__(self) -> str:
        return f"{self.start}:{self.end}"

    def __repr__(self) -> str:
        """Print a simplified form when appearing in repr() or inspect()."""
        return f"<Location {self.start}:{self.end}>"

    def __inspect__(self) -> str:
        return repr(self)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Location):
            return self.start == other.start and self.end == other.end
        elif isinstance(other, (list, tuple)) and len(other) == 2:
            return self.start == other[0] and self.end == other[1]
        return False

    def __ne__(self, other: Any) -> bool:
        return not self == other

    def __hash__(self) -> int:
        return hash((self.start, self.end))


class OperationType(Enum):

    QUERY = "query"
    MUTATION = "mutation"
    SUBSCRIPTION = "subscription"


# Default map from node kinds to their node attributes (internal)
QUERY_DOCUMENT_KEYS: Dict[str, Tuple[str, ...]] = {
    "name": (),
    "document": ("definitions",),
    "operation_definition": (
        "name",
        "variable_definitions",
        "directives",
        "selection_set",
    ),
    "variable_definition": ("variable", "type", "default_value", "directives"),
    "variable": ("name",),
    "selection_set": ("selections",),
    "field": ("alias", "name", "arguments", "directives", "selection_set"),
    "argument": ("name", "value"),
    "fragment_spread": ("name", "directives"),
    "inline_fragment": ("type_condition", "directives", "selection_set"),
    "fragment_definition": (
        # Note: fragment variable definitions are deprecated and will be removed in v3.3
        "name",
        "variable_definitions",
        "type_condition",
        "directives",
        "selection_set",
    ),
    "list_value": ("values",),
    "object_value": ("fields",),
    "object_field": ("name", "value"),
    "directive": ("name", "arguments"),
    "named_type": ("name",),
    "list_type": ("type",),
    "non_null_type": ("type",),
    "schema_definition": ("description", "directives", "operation_types"),
    "operation_type_definition": ("type",),
    "scalar_type_definition": ("description", "name", "directives"),
    "object_type_definition": (
        "description",
        "name",
        "interfaces",
        "directives",
        "fields",
    ),
    "field_definition": ("description", "name", "arguments", "type", "directives"),
    "input_value_definition": (
        "description",
        "name",
        "type",
        "default_value",
        "directives",
    ),
    "interface_type_definition": (
        "description",
        "name",
        "interfaces",
        "directives",
        "fields",
    ),
    "union_type_definition": ("description", "name", "directives", "types"),
    "enum_type_definition": ("description", "name", "directives", "values"),
    "enum_value_definition": ("description", "name", "directives"),
    "input_object_type_definition": ("description", "name", "directives", "fields"),
    "directive_definition": ("description", "name", "arguments", "locations"),
    "schema_extension": ("directives", "operation_types"),
    "scalar_type_extension": ("name", "directives"),
    "object_type_extension": ("name", "interfaces", "directives", "fields"),
    "interface_type_extension": ("name", "interfaces", "directives", "fields"),
    "union_type_extension": ("name", "directives", "types"),
    "enum_type_extension": ("name", "directives", "values"),
    "input_object_type_extension": ("name", "directives", "fields"),
}


# Base AST Node


class Node:
    """AST nodes"""

    # allow custom attributes and weak references (not used internally)
    __slots__ = "__dict__", "__weakref__", "loc", "_hash"

    loc: Optional[Location]

    kind: str = "ast"  # the kind of the node as a snake_case string
    keys: Tuple[str, ...] = ("loc",)  # the names of the attributes of this node

    def __init__(self, **kwargs: Any) -> None:
        """Initialize the node with the given keyword arguments."""
        for key in self.keys:
            value = kwargs.get(key)
            if isinstance(value, list):
                value = tuple(value)
            setattr(self, key, value)

    def __repr__(self) -> str:
        """Get a simple representation of the node."""
        name, loc = self.__class__.__name__, getattr(self, "loc", None)
        return f"{name} at {loc}" if loc else name

    def __eq__(self, other: Any) -> bool:
        """Test whether two nodes are equal (recursively)."""
        return (
            isinstance(other, Node)
            and self.__class__ == other.__class__
            and all(getattr(self, key) == getattr(other, key) for key in self.keys)
        )

    def __hash__(self) -> int:
        """Get a cached hash value for the node."""
        # Caching the hash values improves the performance of AST validators
        hashed = getattr(self, "_hash", None)
        if hashed is None:
            self._hash = id(self)  # avoid recursion
            hashed = hash(tuple(getattr(self, key) for key in self.keys))
            self._hash = hashed
        return hashed

    def __setattr__(self, key: str, value: Any) -> None:
        # reset cashed hash value if attributes are changed
        if hasattr(self, "_hash") and key in self.keys:
            del self._hash
        super().__setattr__(key, value)

    def __copy__(self) -> "Node":
        """Create a shallow copy of the node."""
        return self.__class__(**{key: getattr(self, key) for key in self.keys})

    def __deepcopy__(self, memo: Dict) -> "Node":
        """Create a deep copy of the node"""
        # noinspection PyArgumentList
        return self.__class__(
            **{key: deepcopy(getattr(self, key), memo) for key in self.keys}
        )

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        name = cls.__name__
        try:
            name = name.removeprefix("Const").removesuffix("Node")
        except AttributeError:  # pragma: no cover (Python < 3.9)
            if name.startswith("Const"):
                name = name[5:]
            if name.endswith("Node"):
                name = name[:-4]
        cls.kind = camel_to_snake(name)
        keys: List[str] = []
        for base in cls.__bases__:
            # noinspection PyUnresolvedReferences
            keys.extend(base.keys)  # type: ignore
        keys.extend(cls.__slots__)
        cls.keys = tuple(keys)

    def to_dict(self, locations: bool = False) -> Dict:
        from ..utilities import ast_to_dict

        return ast_to_dict(self, locations)


# Name


class NameNode(Node):
    __slots__ = ("value",)

    value: str


# Document


class DocumentNode(Node):
    __slots__ = ("definitions",)

    definitions: Tuple["DefinitionNode", ...]


class DefinitionNode(Node):
    __slots__ = ()


class ExecutableDefinitionNode(DefinitionNode):
    __slots__ = "name", "directives", "variable_definitions", "selection_set"

    name: Optional[NameNode]
    directives: Tuple["DirectiveNode", ...]
    variable_definitions: Tuple["VariableDefinitionNode", ...]
    selection_set: "SelectionSetNode"


class OperationDefinitionNode(ExecutableDefinitionNode):
    __slots__ = ("operation",)

    operation: OperationType


class VariableDefinitionNode(Node):
    __slots__ = "variable", "type", "default_value", "directives"

    variable: "VariableNode"
    type: "TypeNode"
    default_value: Optional["ConstValueNode"]
    directives: Tuple["ConstDirectiveNode", ...]


class SelectionSetNode(Node):
    __slots__ = ("selections",)

    selections: Tuple["SelectionNode", ...]


class SelectionNode(Node):
    __slots__ = ("directives",)

    directives: Tuple["DirectiveNode", ...]


class FieldNode(SelectionNode):
    __slots__ = "alias", "name", "arguments", "selection_set"

    alias: Optional[NameNode]
    name: NameNode
    arguments: Tuple["ArgumentNode", ...]
    selection_set: Optional[SelectionSetNode]


class ArgumentNode(Node):
    __slots__ = "name", "value"

    name: NameNode
    value: "ValueNode"


class ConstArgumentNode(ArgumentNode):

    value: "ConstValueNode"


# Fragments


class FragmentSpreadNode(SelectionNode):
    __slots__ = ("name",)

    name: NameNode


class InlineFragmentNode(SelectionNode):
    __slots__ = "type_condition", "selection_set"

    type_condition: "NamedTypeNode"
    selection_set: SelectionSetNode


class FragmentDefinitionNode(ExecutableDefinitionNode):
    __slots__ = ("type_condition",)

    name: NameNode
    type_condition: "NamedTypeNode"


# Values


class ValueNode(Node):
    __slots__ = ()


class VariableNode(ValueNode):
    __slots__ = ("name",)

    name: NameNode


class IntValueNode(ValueNode):
    __slots__ = ("value",)

    value: str


class FloatValueNode(ValueNode):
    __slots__ = ("value",)

    value: str


class StringValueNode(ValueNode):
    __slots__ = "value", "block"

    value: str
    block: Optional[bool]


class BooleanValueNode(ValueNode):
    __slots__ = ("value",)

    value: bool


class NullValueNode(ValueNode):
    __slots__ = ()


class EnumValueNode(ValueNode):
    __slots__ = ("value",)

    value: str


class ListValueNode(ValueNode):
    __slots__ = ("values",)

    values: Tuple[ValueNode, ...]


class ConstListValueNode(ListValueNode):

    values: Tuple["ConstValueNode", ...]


class ObjectValueNode(ValueNode):
    __slots__ = ("fields",)

    fields: Tuple["ObjectFieldNode", ...]


class ConstObjectValueNode(ObjectValueNode):

    fields: Tuple["ConstObjectFieldNode", ...]


class ObjectFieldNode(Node):
    __slots__ = "name", "value"

    name: NameNode
    value: ValueNode


class ConstObjectFieldNode(ObjectFieldNode):

    value: "ConstValueNode"


ConstValueNode = Union[
    IntValueNode,
    FloatValueNode,
    StringValueNode,
    BooleanValueNode,
    NullValueNode,
    EnumValueNode,
    ConstListValueNode,
    ConstObjectValueNode,
]


# Directives


class DirectiveNode(Node):
    __slots__ = "name", "arguments"

    name: NameNode
    arguments: Tuple[ArgumentNode, ...]


class ConstDirectiveNode(DirectiveNode):

    arguments: Tuple[ConstArgumentNode, ...]


# Type Reference


class TypeNode(Node):
    __slots__ = ()


class NamedTypeNode(TypeNode):
    __slots__ = ("name",)

    name: NameNode


class ListTypeNode(TypeNode):
    __slots__ = ("type",)

    type: TypeNode


class NonNullTypeNode(TypeNode):
    __slots__ = ("type",)

    type: Union[NamedTypeNode, ListTypeNode]


# Type System Definition


class TypeSystemDefinitionNode(DefinitionNode):
    __slots__ = ()


class SchemaDefinitionNode(TypeSystemDefinitionNode):
    __slots__ = "description", "directives", "operation_types"

    description: Optional[StringValueNode]
    directives: Tuple[ConstDirectiveNode, ...]
    operation_types: Tuple["OperationTypeDefinitionNode", ...]


class OperationTypeDefinitionNode(Node):
    __slots__ = "operation", "type"

    operation: OperationType
    type: NamedTypeNode


# Type Definition


class TypeDefinitionNode(TypeSystemDefinitionNode):
    __slots__ = "description", "name", "directives"

    description: Optional[StringValueNode]
    name: NameNode
    directives: Tuple[DirectiveNode, ...]


class ScalarTypeDefinitionNode(TypeDefinitionNode):
    __slots__ = ()

    directives: Tuple[ConstDirectiveNode, ...]


class ObjectTypeDefinitionNode(TypeDefinitionNode):
    __slots__ = "interfaces", "fields"

    interfaces: Tuple[NamedTypeNode, ...]
    directives: Tuple[ConstDirectiveNode, ...]
    fields: Tuple["FieldDefinitionNode", ...]


class FieldDefinitionNode(DefinitionNode):
    __slots__ = "description", "name", "directives", "arguments", "type"

    description: Optional[StringValueNode]
    name: NameNode
    directives: Tuple[ConstDirectiveNode, ...]
    arguments: Tuple["InputValueDefinitionNode", ...]
    type: TypeNode


class InputValueDefinitionNode(DefinitionNode):
    __slots__ = "description", "name", "directives", "type", "default_value"

    description: Optional[StringValueNode]
    name: NameNode
    directives: Tuple[ConstDirectiveNode, ...]
    type: TypeNode
    default_value: Optional[ConstValueNode]


class InterfaceTypeDefinitionNode(TypeDefinitionNode):
    __slots__ = "fields", "interfaces"

    fields: Tuple["FieldDefinitionNode", ...]
    directives: Tuple[ConstDirectiveNode, ...]
    interfaces: Tuple[NamedTypeNode, ...]


class UnionTypeDefinitionNode(TypeDefinitionNode):
    __slots__ = ("types",)

    directives: Tuple[ConstDirectiveNode, ...]
    types: Tuple[NamedTypeNode, ...]


class EnumTypeDefinitionNode(TypeDefinitionNode):
    __slots__ = ("values",)

    directives: Tuple[ConstDirectiveNode, ...]
    values: Tuple["EnumValueDefinitionNode", ...]


class EnumValueDefinitionNode(DefinitionNode):
    __slots__ = "description", "name", "directives"

    description: Optional[StringValueNode]
    name: NameNode
    directives: Tuple[ConstDirectiveNode, ...]


class InputObjectTypeDefinitionNode(TypeDefinitionNode):
    __slots__ = ("fields",)

    directives: Tuple[ConstDirectiveNode, ...]
    fields: Tuple[InputValueDefinitionNode, ...]


# Directive Definitions


class DirectiveDefinitionNode(TypeSystemDefinitionNode):
    __slots__ = "description", "name", "arguments", "repeatable", "locations"

    description: Optional[StringValueNode]
    name: NameNode
    arguments: Tuple[InputValueDefinitionNode, ...]
    repeatable: bool
    locations: Tuple[NameNode, ...]


# Type System Extensions


class SchemaExtensionNode(Node):
    __slots__ = "directives", "operation_types"

    directives: Tuple[ConstDirectiveNode, ...]
    operation_types: Tuple[OperationTypeDefinitionNode, ...]


# Type Extensions


class TypeExtensionNode(TypeSystemDefinitionNode):
    __slots__ = "name", "directives"

    name: NameNode
    directives: Tuple[ConstDirectiveNode, ...]


TypeSystemExtensionNode = Union[SchemaExtensionNode, TypeExtensionNode]


class ScalarTypeExtensionNode(TypeExtensionNode):
    __slots__ = ()


class ObjectTypeExtensionNode(TypeExtensionNode):
    __slots__ = "interfaces", "fields"

    interfaces: Tuple[NamedTypeNode, ...]
    fields: Tuple[FieldDefinitionNode, ...]


class InterfaceTypeExtensionNode(TypeExtensionNode):
    __slots__ = "interfaces", "fields"

    interfaces: Tuple[NamedTypeNode, ...]
    fields: Tuple[FieldDefinitionNode, ...]


class UnionTypeExtensionNode(TypeExtensionNode):
    __slots__ = ("types",)

    types: Tuple[NamedTypeNode, ...]


class EnumTypeExtensionNode(TypeExtensionNode):
    __slots__ = ("values",)

    values: Tuple[EnumValueDefinitionNode, ...]


class InputObjectTypeExtensionNode(TypeExtensionNode):
    __slots__ = ("fields",)

    fields: Tuple[InputValueDefinitionNode, ...]
