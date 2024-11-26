from operator import attrgetter, itemgetter
from typing import (
    Any,
    Collection,
    Dict,
    List,
    Optional,
    Set,
    Tuple,
    Union,
    cast,
)

from ..error import GraphQLError
from ..pyutils import inspect
from ..language import (
    DirectiveNode,
    InputValueDefinitionNode,
    NamedTypeNode,
    Node,
    OperationType,
    SchemaDefinitionNode,
    SchemaExtensionNode,
)
from .definition import (
    GraphQLEnumType,
    GraphQLInputField,
    GraphQLInputObjectType,
    GraphQLInterfaceType,
    GraphQLObjectType,
    GraphQLUnionType,
    is_enum_type,
    is_input_object_type,
    is_input_type,
    is_interface_type,
    is_named_type,
    is_non_null_type,
    is_object_type,
    is_output_type,
    is_union_type,
    is_required_argument,
    is_required_input_field,
)
from ..utilities.type_comparators import is_equal_type, is_type_sub_type_of
from .directives import is_directive, GraphQLDeprecatedDirective
from .introspection import is_introspection_type
from .schema import GraphQLSchema, assert_schema

__all__ = ["validate_schema", "assert_valid_schema"]


def validate_schema(schema: GraphQLSchema) -> List[GraphQLError]:
    """Validate a GraphQL schema.

    Implements the "Type Validation" sub-sections of the specification's "Type System"
    section.

    Validation runs synchronously, returning a list of encountered errors, or an empty
    list if no errors were encountered and the Schema is valid.
    """
    # First check to ensure the provided value is in fact a GraphQLSchema.
    assert_schema(schema)

    # If this Schema has already been validated, return the previous results.
    # noinspection PyProtectedMember
    errors = schema._validation_errors
    if errors is None:

        # Validate the schema, producing a list of errors.
        context = SchemaValidationContext(schema)
        context.validate_root_types()
        context.validate_directives()
        context.validate_types()

        # Persist the results of validation before returning to ensure validation does
        # not run multiple times for this schema.
        errors = context.errors
        schema._validation_errors = errors

    return errors


def assert_valid_schema(schema: GraphQLSchema) -> None:
    """Utility function which asserts a schema is valid.

    Throws a TypeError if the schema is invalid.
    """
    errors = validate_schema(schema)
    if errors:
        raise TypeError("\n\n".join(error.message for error in errors))


class SchemaValidationContext:
    """Utility class providing a context for schema validation."""

    errors: List[GraphQLError]
    schema: GraphQLSchema

    def __init__(self, schema: GraphQLSchema):
        self.errors = []
        self.schema = schema

    def report_error(
        self,
        message: str,
        nodes: Union[Optional[Node], Collection[Optional[Node]]] = None,
    ) -> None:
        if nodes and not isinstance(nodes, Node):
            nodes = [node for node in nodes if node]
        nodes = cast(Optional[Collection[Node]], nodes)
        self.errors.append(GraphQLError(message, nodes))

    def validate_root_types(self) -> None:
        schema = self.schema
        query_type = schema.query_type
        if not query_type:
            self.report_error("Query root type must be provided.", schema.ast_node)
        elif not is_object_type(query_type):
            self.report_error(
                f"Query root type must be Object type, it cannot be {query_type}.",
                get_operation_type_node(schema, OperationType.QUERY)
                or query_type.ast_node,
            )

        mutation_type = schema.mutation_type
        if mutation_type and not is_object_type(mutation_type):
            self.report_error(
                "Mutation root type must be Object type if provided,"
                f" it cannot be {mutation_type}.",
                get_operation_type_node(schema, OperationType.MUTATION)
                or mutation_type.ast_node,
            )

        subscription_type = schema.subscription_type
        if subscription_type and not is_object_type(subscription_type):
            self.report_error(
                "Subscription root type must be Object type if provided,"
                f" it cannot be {subscription_type}.",
                get_operation_type_node(schema, OperationType.SUBSCRIPTION)
                or subscription_type.ast_node,
            )

    def validate_directives(self) -> None:
        directives = self.schema.directives
        for directive in directives:
            # Ensure all directives are in fact GraphQL directives.
            if not is_directive(directive):
                self.report_error(
                    f"Expected directive but got: {inspect(directive)}.",
                    getattr(directive, "ast_node", None),
                )
                continue

            # Ensure they are named correctly.
            self.validate_name(directive)

            # Ensure the arguments are valid.
            for arg_name, arg in directive.args.items():
                # Ensure they are named correctly.
                self.validate_name(arg, arg_name)

                # Ensure the type is an input type.
                if not is_input_type(arg.type):
                    self.report_error(
                        f"The type of @{directive.name}({arg_name}:)"
                        f" must be Input Type but got: {inspect(arg.type)}.",
                        arg.ast_node,
                    )

                if is_required_argument(arg) and arg.deprecation_reason is not None:
                    self.report_error(
                        f"Required argument @{directive.name}({arg_name}:)"
                        " cannot be deprecated.",
                        [
                            get_deprecated_directive_node(arg.ast_node),
                            arg.ast_node and arg.ast_node.type,
                        ],
                    )

    def validate_name(self, node: Any, name: Optional[str] = None) -> None:
        # Ensure names are valid, however introspection types opt out.
        try:
            if not name:
                name = node.name
            name = cast(str, name)
            ast_node = node.ast_node
        except AttributeError:  # pragma: no cover
            pass
        else:
            if name.startswith("__"):
                self.report_error(
                    f"Name {name!r} must not begin with '__',"
                    " which is reserved by GraphQL introspection.",
                    ast_node,
                )

    def validate_types(self) -> None:
        validate_input_object_circular_refs = InputObjectCircularRefsValidator(self)
        for type_ in self.schema.type_map.values():

            # Ensure all provided types are in fact GraphQL type.
            if not is_named_type(type_):
                self.report_error(
                    f"Expected GraphQL named type but got: {inspect(type_)}.",
                    type_.ast_node if is_named_type(type_) else None,
                )
                continue

            # Ensure it is named correctly (excluding introspection types).
            if not is_introspection_type(type_):
                self.validate_name(type_)

            if is_object_type(type_):
                type_ = cast(GraphQLObjectType, type_)
                # Ensure fields are valid
                self.validate_fields(type_)

                # Ensure objects implement the interfaces they claim to.
                self.validate_interfaces(type_)
            elif is_interface_type(type_):
                type_ = cast(GraphQLInterfaceType, type_)
                # Ensure fields are valid.
                self.validate_fields(type_)

                # Ensure interfaces implement the interfaces they claim to.
                self.validate_interfaces(type_)
            elif is_union_type(type_):
                type_ = cast(GraphQLUnionType, type_)
                # Ensure Unions include valid member types.
                self.validate_union_members(type_)
            elif is_enum_type(type_):
                type_ = cast(GraphQLEnumType, type_)
                # Ensure Enums have valid values.
                self.validate_enum_values(type_)
            elif is_input_object_type(type_):
                type_ = cast(GraphQLInputObjectType, type_)
                # Ensure Input Object fields are valid.
                self.validate_input_fields(type_)

                # Ensure Input Objects do not contain non-nullable circular references
                validate_input_object_circular_refs(type_)

    def validate_fields(
        self, type_: Union[GraphQLObjectType, GraphQLInterfaceType]
    ) -> None:
        fields = type_.fields

        # Objects and Interfaces both must define one or more fields.
        if not fields:
            self.report_error(
                f"Type {type_.name} must define one or more fields.",
                [type_.ast_node, *type_.extension_ast_nodes],
            )

        for field_name, field in fields.items():

            # Ensure they are named correctly.
            self.validate_name(field, field_name)

            # Ensure the type is an output type
            if not is_output_type(field.type):
                self.report_error(
                    f"The type of {type_.name}.{field_name}"
                    f" must be Output Type but got: {inspect(field.type)}.",
                    field.ast_node and field.ast_node.type,
                )

            # Ensure the arguments are valid.
            for arg_name, arg in field.args.items():
                # Ensure they are named correctly.
                self.validate_name(arg, arg_name)

                # Ensure the type is an input type.
                if not is_input_type(arg.type):
                    self.report_error(
                        f"The type of {type_.name}.{field_name}({arg_name}:)"
                        f" must be Input Type but got: {inspect(arg.type)}.",
                        arg.ast_node and arg.ast_node.type,
                    )

                if is_required_argument(arg) and arg.deprecation_reason is not None:
                    self.report_error(
                        f"Required argument {type_.name}.{field_name}({arg_name}:)"
                        " cannot be deprecated.",
                        [
                            get_deprecated_directive_node(arg.ast_node),
                            arg.ast_node and arg.ast_node.type,
                        ],
                    )

    def validate_interfaces(
        self, type_: Union[GraphQLObjectType, GraphQLInterfaceType]
    ) -> None:
        iface_type_names: Set[str] = set()
        for iface in type_.interfaces:
            if not is_interface_type(iface):
                self.report_error(
                    f"Type {type_.name} must only implement Interface"
                    f" types, it cannot implement {inspect(iface)}.",
                    get_all_implements_interface_nodes(type_, iface),
                )
                continue

            if type_ is iface:
                self.report_error(
                    f"Type {type_.name} cannot implement itself"
                    " because it would create a circular reference.",
                    get_all_implements_interface_nodes(type_, iface),
                )

            if iface.name in iface_type_names:
                self.report_error(
                    f"Type {type_.name} can only implement {iface.name} once.",
                    get_all_implements_interface_nodes(type_, iface),
                )
                continue

            iface_type_names.add(iface.name)

            self.validate_type_implements_ancestors(type_, iface)
            self.validate_type_implements_interface(type_, iface)

    def validate_type_implements_interface(
        self,
        type_: Union[GraphQLObjectType, GraphQLInterfaceType],
        iface: GraphQLInterfaceType,
    ) -> None:
        type_fields, iface_fields = type_.fields, iface.fields

        # Assert each interface field is implemented.
        for field_name, iface_field in iface_fields.items():
            type_field = type_fields.get(field_name)

            # Assert interface field exists on object.
            if not type_field:
                self.report_error(
                    f"Interface field {iface.name}.{field_name}"
                    f" expected but {type_.name} does not provide it.",
                    [
                        iface_field.ast_node,
                        type_.ast_node,
                        *type_.extension_ast_nodes,
                    ],
                )
                continue

            # Assert interface field type is satisfied by type field type, by being
            # a valid subtype (covariant).
            if not is_type_sub_type_of(self.schema, type_field.type, iface_field.type):
                self.report_error(
                    f"Interface field {iface.name}.{field_name}"
                    f" expects type {iface_field.type}"
                    f" but {type_.name}.{field_name}"
                    f" is type {type_field.type}.",
                    [
                        iface_field.ast_node and iface_field.ast_node.type,
                        type_field.ast_node and type_field.ast_node.type,
                    ],
                )

            # Assert each interface field arg is implemented.
            for arg_name, iface_arg in iface_field.args.items():
                type_arg = type_field.args.get(arg_name)

                # Assert interface field arg exists on object field.
                if not type_arg:
                    self.report_error(
                        "Interface field argument"
                        f" {iface.name}.{field_name}({arg_name}:)"
                        f" expected but {type_.name}.{field_name}"
                        " does not provide it.",
                        [iface_arg.ast_node, type_field.ast_node],
                    )
                    continue

                # Assert interface field arg type matches object field arg type
                # (invariant).
                if not is_equal_type(iface_arg.type, type_arg.type):
                    self.report_error(
                        "Interface field argument"
                        f" {iface.name}.{field_name}({arg_name}:)"
                        f" expects type {iface_arg.type}"
                        f" but {type_.name}.{field_name}({arg_name}:)"
                        f" is type {type_arg.type}.",
                        [
                            iface_arg.ast_node and iface_arg.ast_node.type,
                            type_arg.ast_node and type_arg.ast_node.type,
                        ],
                    )

            # Assert additional arguments must not be required.
            for arg_name, type_arg in type_field.args.items():
                iface_arg = iface_field.args.get(arg_name)
                if not iface_arg and is_required_argument(type_arg):
                    self.report_error(
                        f"Object field {type_.name}.{field_name} includes"
                        f" required argument {arg_name} that is missing from"
                        f" the Interface field {iface.name}.{field_name}.",
                        [type_arg.ast_node, iface_field.ast_node],
                    )

    def validate_type_implements_ancestors(
        self,
        type_: Union[GraphQLObjectType, GraphQLInterfaceType],
        iface: GraphQLInterfaceType,
    ) -> None:
        type_interfaces, iface_interfaces = type_.interfaces, iface.interfaces
        for transitive in iface_interfaces:
            if transitive not in type_interfaces:
                self.report_error(
                    f"Type {type_.name} cannot implement {iface.name}"
                    " because it would create a circular reference."
                    if transitive is type_
                    else f"Type {type_.name} must implement {transitive.name}"
                    f" because it is implemented by {iface.name}.",
                    get_all_implements_interface_nodes(iface, transitive)
                    + get_all_implements_interface_nodes(type_, iface),
                )

    def validate_union_members(self, union: GraphQLUnionType) -> None:
        member_types = union.types

        if not member_types:
            self.report_error(
                f"Union type {union.name} must define one or more member types.",
                [union.ast_node, *union.extension_ast_nodes],
            )

        included_type_names: Set[str] = set()
        for member_type in member_types:
            if is_object_type(member_type):
                if member_type.name in included_type_names:
                    self.report_error(
                        f"Union type {union.name} can only include type"
                        f" {member_type.name} once.",
                        get_union_member_type_nodes(union, member_type.name),
                    )
                else:
                    included_type_names.add(member_type.name)
            else:
                self.report_error(
                    f"Union type {union.name} can only include Object types,"
                    f" it cannot include {inspect(member_type)}.",
                    get_union_member_type_nodes(union, str(member_type)),
                )

    def validate_enum_values(self, enum_type: GraphQLEnumType) -> None:
        enum_values = enum_type.values

        if not enum_values:
            self.report_error(
                f"Enum type {enum_type.name} must define one or more values.",
                [enum_type.ast_node, *enum_type.extension_ast_nodes],
            )

        for value_name, enum_value in enum_values.items():
            # Ensure valid name.
            self.validate_name(enum_value, value_name)

    def validate_input_fields(self, input_obj: GraphQLInputObjectType) -> None:
        fields = input_obj.fields

        if not fields:
            self.report_error(
                f"Input Object type {input_obj.name}"
                " must define one or more fields.",
                [input_obj.ast_node, *input_obj.extension_ast_nodes],
            )

        # Ensure the arguments are valid
        for field_name, field in fields.items():

            # Ensure they are named correctly.
            self.validate_name(field, field_name)

            # Ensure the type is an input type.
            if not is_input_type(field.type):
                self.report_error(
                    f"The type of {input_obj.name}.{field_name}"
                    f" must be Input Type but got: {inspect(field.type)}.",
                    field.ast_node.type if field.ast_node else None,
                )

            if is_required_input_field(field) and field.deprecation_reason is not None:
                self.report_error(
                    f"Required input field {input_obj.name}.{field_name}"
                    " cannot be deprecated.",
                    [
                        get_deprecated_directive_node(field.ast_node),
                        field.ast_node and field.ast_node.type,
                    ],
                )


def get_operation_type_node(
    schema: GraphQLSchema, operation: OperationType
) -> Optional[Node]:
    ast_node: Optional[Union[SchemaDefinitionNode, SchemaExtensionNode]]
    for ast_node in [schema.ast_node, *(schema.extension_ast_nodes or ())]:
        if ast_node:
            operation_types = ast_node.operation_types
            if operation_types:  # pragma: no cover else
                for operation_type in operation_types:
                    if operation_type.operation == operation:
                        return operation_type.type
    return None


class InputObjectCircularRefsValidator:
    """Modified copy of algorithm from validation.rules.NoFragmentCycles"""

    def __init__(self, context: SchemaValidationContext):
        self.context = context
        # Tracks already visited types to maintain O(N) and to ensure that cycles
        # are not redundantly reported.
        self.visited_types: Set[str] = set()
        # Array of input fields used to produce meaningful errors
        self.field_path: List[Tuple[str, GraphQLInputField]] = []
        # Position in the type path
        self.field_path_index_by_type_name: Dict[str, int] = {}

    def __call__(self, input_obj: GraphQLInputObjectType) -> None:
        """Detect cycles recursively."""
        # This does a straight-forward DFS to find cycles.
        # It does not terminate when a cycle was found but continues to explore
        # the graph to find all possible cycles.
        name = input_obj.name
        if name in self.visited_types:
            return

        self.visited_types.add(name)
        self.field_path_index_by_type_name[name] = len(self.field_path)

        for field_name, field in input_obj.fields.items():
            if is_non_null_type(field.type) and is_input_object_type(
                field.type.of_type
            ):
                field_type = cast(GraphQLInputObjectType, field.type.of_type)
                cycle_index = self.field_path_index_by_type_name.get(field_type.name)

                self.field_path.append((field_name, field))
                if cycle_index is None:
                    self(field_type)
                else:
                    cycle_path = self.field_path[cycle_index:]
                    field_names = map(itemgetter(0), cycle_path)
                    self.context.report_error(
                        f"Cannot reference Input Object '{field_type.name}'"
                        " within itself through a series of non-null fields:"
                        f" '{'.'.join(field_names)}'.",
                        cast(
                            Collection[Node],
                            map(attrgetter("ast_node"), map(itemgetter(1), cycle_path)),
                        ),
                    )
                self.field_path.pop()

        del self.field_path_index_by_type_name[name]


def get_all_implements_interface_nodes(
    type_: Union[GraphQLObjectType, GraphQLInterfaceType], iface: GraphQLInterfaceType
) -> List[NamedTypeNode]:
    ast_node = type_.ast_node
    nodes = type_.extension_ast_nodes
    if ast_node is not None:
        nodes = [ast_node, *nodes]  # type: ignore
    implements_nodes: List[NamedTypeNode] = []
    for node in nodes:
        iface_nodes = node.interfaces
        if iface_nodes:  # pragma: no cover else
            implements_nodes.extend(
                iface_node
                for iface_node in iface_nodes
                if iface_node.name.value == iface.name
            )
    return implements_nodes


def get_union_member_type_nodes(
    union: GraphQLUnionType, type_name: str
) -> List[NamedTypeNode]:
    ast_node = union.ast_node
    nodes = union.extension_ast_nodes
    if ast_node is not None:
        nodes = [ast_node, *nodes]  # type: ignore
    member_type_nodes: List[NamedTypeNode] = []
    for node in nodes:
        type_nodes = node.types
        if type_nodes:  # pragma: no cover else
            member_type_nodes.extend(
                type_node
                for type_node in type_nodes
                if type_node.name.value == type_name
            )
    return member_type_nodes


def get_deprecated_directive_node(
    definition_node: Optional[Union[InputValueDefinitionNode]],
) -> Optional[DirectiveNode]:
    directives = definition_node and definition_node.directives
    if directives:
        for directive in directives:
            if (
                directive.name.value == GraphQLDeprecatedDirective.name
            ):  # pragma: no cover else
                return directive
    return None  # pragma: no cover
