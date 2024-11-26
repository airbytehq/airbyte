from typing import Any, Callable, List, Optional, Union, cast

from ..language import (
    ArgumentNode,
    DirectiveNode,
    EnumValueNode,
    FieldNode,
    InlineFragmentNode,
    ListValueNode,
    Node,
    ObjectFieldNode,
    OperationDefinitionNode,
    SelectionSetNode,
    VariableDefinitionNode,
    Visitor,
)
from ..pyutils import Undefined
from ..type import (
    GraphQLArgument,
    GraphQLCompositeType,
    GraphQLDirective,
    GraphQLEnumType,
    GraphQLEnumValue,
    GraphQLField,
    GraphQLInputObjectType,
    GraphQLInputType,
    GraphQLInterfaceType,
    GraphQLList,
    GraphQLObjectType,
    GraphQLOutputType,
    GraphQLSchema,
    GraphQLType,
    is_composite_type,
    is_input_type,
    is_output_type,
    get_named_type,
    SchemaMetaFieldDef,
    TypeMetaFieldDef,
    TypeNameMetaFieldDef,
    is_object_type,
    is_interface_type,
    get_nullable_type,
    is_list_type,
    is_input_object_type,
    is_enum_type,
)
from .type_from_ast import type_from_ast

__all__ = ["TypeInfo", "TypeInfoVisitor"]


GetFieldDefFn = Callable[
    [GraphQLSchema, GraphQLType, FieldNode], Optional[GraphQLField]
]


class TypeInfo:
    """Utility class for keeping track of type definitions.

    TypeInfo is a utility class which, given a GraphQL schema, can keep track of the
    current field and type definitions at any point in a GraphQL document AST during
    a recursive descent by calling :meth:`enter(node) <.TypeInfo.enter>` and
    :meth:`leave(node) <.TypeInfo.leave>`.
    """

    def __init__(
        self,
        schema: GraphQLSchema,
        initial_type: Optional[GraphQLType] = None,
        get_field_def_fn: Optional[GetFieldDefFn] = None,
    ) -> None:
        """Initialize the TypeInfo for the given GraphQL schema.

        Initial type may be provided in rare cases to facilitate traversals beginning
        somewhere other than documents.

        The optional last parameter is deprecated and will be removed in v3.3.
        """
        self._schema = schema
        self._type_stack: List[Optional[GraphQLOutputType]] = []
        self._parent_type_stack: List[Optional[GraphQLCompositeType]] = []
        self._input_type_stack: List[Optional[GraphQLInputType]] = []
        self._field_def_stack: List[Optional[GraphQLField]] = []
        self._default_value_stack: List[Any] = []
        self._directive: Optional[GraphQLDirective] = None
        self._argument: Optional[GraphQLArgument] = None
        self._enum_value: Optional[GraphQLEnumValue] = None
        self._get_field_def: GetFieldDefFn = get_field_def_fn or get_field_def
        if initial_type:
            if is_input_type(initial_type):
                self._input_type_stack.append(cast(GraphQLInputType, initial_type))
            if is_composite_type(initial_type):
                self._parent_type_stack.append(cast(GraphQLCompositeType, initial_type))
            if is_output_type(initial_type):
                self._type_stack.append(cast(GraphQLOutputType, initial_type))

    def get_type(self) -> Optional[GraphQLOutputType]:
        if self._type_stack:
            return self._type_stack[-1]
        return None

    def get_parent_type(self) -> Optional[GraphQLCompositeType]:
        if self._parent_type_stack:
            return self._parent_type_stack[-1]
        return None

    def get_input_type(self) -> Optional[GraphQLInputType]:
        if self._input_type_stack:
            return self._input_type_stack[-1]
        return None

    def get_parent_input_type(self) -> Optional[GraphQLInputType]:
        if len(self._input_type_stack) > 1:
            return self._input_type_stack[-2]
        return None

    def get_field_def(self) -> Optional[GraphQLField]:
        if self._field_def_stack:
            return self._field_def_stack[-1]
        return None

    def get_default_value(self) -> Any:
        if self._default_value_stack:
            return self._default_value_stack[-1]
        return None

    def get_directive(self) -> Optional[GraphQLDirective]:
        return self._directive

    def get_argument(self) -> Optional[GraphQLArgument]:
        return self._argument

    def get_enum_value(self) -> Optional[GraphQLEnumValue]:
        return self._enum_value

    def enter(self, node: Node) -> None:
        method = getattr(self, "enter_" + node.kind, None)
        if method:
            method(node)

    def leave(self, node: Node) -> None:
        method = getattr(self, "leave_" + node.kind, None)
        if method:
            method()

    # noinspection PyUnusedLocal
    def enter_selection_set(self, node: SelectionSetNode) -> None:
        named_type = get_named_type(self.get_type())
        self._parent_type_stack.append(
            cast(GraphQLCompositeType, named_type)
            if is_composite_type(named_type)
            else None
        )

    def enter_field(self, node: FieldNode) -> None:
        parent_type = self.get_parent_type()
        if parent_type:
            field_def = self._get_field_def(self._schema, parent_type, node)
            field_type = field_def.type if field_def else None
        else:
            field_def = field_type = None
        self._field_def_stack.append(field_def)
        self._type_stack.append(field_type if is_output_type(field_type) else None)

    def enter_directive(self, node: DirectiveNode) -> None:
        self._directive = self._schema.get_directive(node.name.value)

    def enter_operation_definition(self, node: OperationDefinitionNode) -> None:
        root_type = self._schema.get_root_type(node.operation)
        self._type_stack.append(root_type if is_object_type(root_type) else None)

    def enter_inline_fragment(self, node: InlineFragmentNode) -> None:
        type_condition_ast = node.type_condition
        output_type = (
            type_from_ast(self._schema, type_condition_ast)
            if type_condition_ast
            else get_named_type(self.get_type())
        )
        self._type_stack.append(
            cast(GraphQLOutputType, output_type)
            if is_output_type(output_type)
            else None
        )

    enter_fragment_definition = enter_inline_fragment

    def enter_variable_definition(self, node: VariableDefinitionNode) -> None:
        input_type = type_from_ast(self._schema, node.type)
        self._input_type_stack.append(
            cast(GraphQLInputType, input_type) if is_input_type(input_type) else None
        )

    def enter_argument(self, node: ArgumentNode) -> None:
        field_or_directive = self.get_directive() or self.get_field_def()
        if field_or_directive:
            arg_def = field_or_directive.args.get(node.name.value)
            arg_type = arg_def.type if arg_def else None
        else:
            arg_def = arg_type = None
        self._argument = arg_def
        self._default_value_stack.append(
            arg_def.default_value if arg_def else Undefined
        )
        self._input_type_stack.append(arg_type if is_input_type(arg_type) else None)

    # noinspection PyUnusedLocal
    def enter_list_value(self, node: ListValueNode) -> None:
        list_type = get_nullable_type(self.get_input_type())  # type: ignore
        item_type = (
            cast(GraphQLList, list_type).of_type
            if is_list_type(list_type)
            else list_type
        )
        # List positions never have a default value.
        self._default_value_stack.append(Undefined)
        self._input_type_stack.append(item_type if is_input_type(item_type) else None)

    def enter_object_field(self, node: ObjectFieldNode) -> None:
        object_type = get_named_type(self.get_input_type())
        if is_input_object_type(object_type):
            input_field = cast(GraphQLInputObjectType, object_type).fields.get(
                node.name.value
            )
            input_field_type = input_field.type if input_field else None
        else:
            input_field = input_field_type = None
        self._default_value_stack.append(
            input_field.default_value if input_field else Undefined
        )
        self._input_type_stack.append(
            input_field_type if is_input_type(input_field_type) else None
        )

    def enter_enum_value(self, node: EnumValueNode) -> None:
        enum_type = get_named_type(self.get_input_type())
        if is_enum_type(enum_type):
            enum_value = cast(GraphQLEnumType, enum_type).values.get(node.value)
        else:
            enum_value = None
        self._enum_value = enum_value

    def leave_selection_set(self) -> None:
        del self._parent_type_stack[-1:]

    def leave_field(self) -> None:
        del self._field_def_stack[-1:]
        del self._type_stack[-1:]

    def leave_directive(self) -> None:
        self._directive = None

    def leave_operation_definition(self) -> None:
        del self._type_stack[-1:]

    leave_inline_fragment = leave_operation_definition
    leave_fragment_definition = leave_operation_definition

    def leave_variable_definition(self) -> None:
        del self._input_type_stack[-1:]

    def leave_argument(self) -> None:
        self._argument = None
        del self._default_value_stack[-1:]
        del self._input_type_stack[-1:]

    def leave_list_value(self) -> None:
        del self._default_value_stack[-1:]
        del self._input_type_stack[-1:]

    leave_object_field = leave_list_value

    def leave_enum_value(self) -> None:
        self._enum_value = None


def get_field_def(
    schema: GraphQLSchema, parent_type: GraphQLType, field_node: FieldNode
) -> Optional[GraphQLField]:
    """Get field definition.

    Not exactly the same as the executor's definition of
    :func:`graphql.execution.get_field_def`, in this statically evaluated environment
    we do not always have an Object type, and need to handle Interface and Union types.
    """
    name = field_node.name.value
    if name == "__schema" and schema.query_type is parent_type:
        return SchemaMetaFieldDef
    if name == "__type" and schema.query_type is parent_type:
        return TypeMetaFieldDef
    if name == "__typename" and is_composite_type(parent_type):
        return TypeNameMetaFieldDef
    if is_object_type(parent_type) or is_interface_type(parent_type):
        parent_type = cast(Union[GraphQLObjectType, GraphQLInterfaceType], parent_type)
        return parent_type.fields.get(name)
    return None


class TypeInfoVisitor(Visitor):
    """A visitor which maintains a provided TypeInfo."""

    def __init__(self, type_info: "TypeInfo", visitor: Visitor):
        super().__init__()
        self.type_info = type_info
        self.visitor = visitor

    def enter(self, node: Node, *args: Any) -> Any:
        self.type_info.enter(node)
        fn = self.visitor.get_enter_leave_for_kind(node.kind).enter
        if fn:
            result = fn(node, *args)
            if result is not None:
                self.type_info.leave(node)
                if isinstance(result, Node):
                    self.type_info.enter(result)
            return result

    def leave(self, node: Node, *args: Any) -> Any:
        fn = self.visitor.get_enter_leave_for_kind(node.kind).leave
        result = fn(node, *args) if fn else None
        self.type_info.leave(node)
        return result
