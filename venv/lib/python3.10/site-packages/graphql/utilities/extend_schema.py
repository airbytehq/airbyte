from collections import defaultdict
from typing import (
    Any,
    Callable,
    Collection,
    DefaultDict,
    Dict,
    List,
    Mapping,
    Optional,
    Union,
    cast,
)

from ..language import (
    DirectiveDefinitionNode,
    DirectiveLocation,
    DocumentNode,
    EnumTypeDefinitionNode,
    EnumTypeExtensionNode,
    EnumValueDefinitionNode,
    FieldDefinitionNode,
    InputObjectTypeDefinitionNode,
    InputObjectTypeExtensionNode,
    InputValueDefinitionNode,
    InterfaceTypeDefinitionNode,
    InterfaceTypeExtensionNode,
    ListTypeNode,
    NamedTypeNode,
    NonNullTypeNode,
    ObjectTypeDefinitionNode,
    ObjectTypeExtensionNode,
    OperationType,
    ScalarTypeDefinitionNode,
    ScalarTypeExtensionNode,
    SchemaExtensionNode,
    SchemaDefinitionNode,
    TypeDefinitionNode,
    TypeExtensionNode,
    TypeNode,
    UnionTypeDefinitionNode,
    UnionTypeExtensionNode,
)
from ..pyutils import inspect, merge_kwargs
from ..type import (
    GraphQLArgument,
    GraphQLArgumentMap,
    GraphQLDeprecatedDirective,
    GraphQLDirective,
    GraphQLEnumType,
    GraphQLEnumValue,
    GraphQLEnumValueMap,
    GraphQLField,
    GraphQLFieldMap,
    GraphQLInputField,
    GraphQLInputObjectType,
    GraphQLInputType,
    GraphQLInputFieldMap,
    GraphQLInterfaceType,
    GraphQLList,
    GraphQLNamedType,
    GraphQLNonNull,
    GraphQLNullableType,
    GraphQLObjectType,
    GraphQLOutputType,
    GraphQLScalarType,
    GraphQLSchema,
    GraphQLSchemaKwargs,
    GraphQLSpecifiedByDirective,
    GraphQLType,
    GraphQLUnionType,
    assert_schema,
    is_enum_type,
    is_input_object_type,
    is_interface_type,
    is_list_type,
    is_non_null_type,
    is_object_type,
    is_scalar_type,
    is_union_type,
    is_introspection_type,
    is_specified_scalar_type,
    introspection_types,
    specified_scalar_types,
)
from .value_from_ast import value_from_ast

__all__ = [
    "extend_schema",
    "extend_schema_impl",
]


def extend_schema(
    schema: GraphQLSchema,
    document_ast: DocumentNode,
    assume_valid: bool = False,
    assume_valid_sdl: bool = False,
) -> GraphQLSchema:
    """Extend the schema with extensions from a given document.

    Produces a new schema given an existing schema and a document which may contain
    GraphQL type extensions and definitions. The original schema will remain unaltered.

    Because a schema represents a graph of references, a schema cannot be extended
    without effectively making an entire copy. We do not know until it's too late if
    subgraphs remain unchanged.

    This algorithm copies the provided schema, applying extensions while producing the
    copy. The original schema remains unaltered.

    When extending a schema with a known valid extension, it might be safe to assume the
    schema is valid. Set ``assume_valid`` to ``True`` to assume the produced schema is
    valid. Set ``assume_valid_sdl`` to ``True`` to assume it is already a valid SDL
    document.
    """
    assert_schema(schema)

    if not isinstance(document_ast, DocumentNode):
        raise TypeError("Must provide valid Document AST.")

    if not (assume_valid or assume_valid_sdl):
        from ..validation.validate import assert_valid_sdl_extension

        assert_valid_sdl_extension(document_ast, schema)

    schema_kwargs = schema.to_kwargs()
    extended_kwargs = extend_schema_impl(schema_kwargs, document_ast, assume_valid)
    return (
        schema if schema_kwargs is extended_kwargs else GraphQLSchema(**extended_kwargs)
    )


def extend_schema_impl(
    schema_kwargs: GraphQLSchemaKwargs,
    document_ast: DocumentNode,
    assume_valid: bool = False,
) -> GraphQLSchemaKwargs:
    """Extend the given schema arguments with extensions from a given document.

    For internal use only.
    """
    # Note: schema_kwargs should become a TypedDict once we require Python 3.8

    # Collect the type definitions and extensions found in the document.
    type_defs: List[TypeDefinitionNode] = []
    type_extensions_map: DefaultDict[str, Any] = defaultdict(list)

    # New directives and types are separate because a directives and types can have the
    # same name. For example, a type named "skip".
    directive_defs: List[DirectiveDefinitionNode] = []

    schema_def: Optional[SchemaDefinitionNode] = None
    # Schema extensions are collected which may add additional operation types.
    schema_extensions: List[SchemaExtensionNode] = []

    for def_ in document_ast.definitions:
        if isinstance(def_, SchemaDefinitionNode):
            schema_def = def_
        elif isinstance(def_, SchemaExtensionNode):
            schema_extensions.append(def_)
        elif isinstance(def_, TypeDefinitionNode):
            type_defs.append(def_)
        elif isinstance(def_, TypeExtensionNode):
            extended_type_name = def_.name.value
            type_extensions_map[extended_type_name].append(def_)
        elif isinstance(def_, DirectiveDefinitionNode):
            directive_defs.append(def_)

    # If this document contains no new types, extensions, or directives then return the
    # same unmodified GraphQLSchema instance.
    if (
        not type_extensions_map
        and not type_defs
        and not directive_defs
        and not schema_extensions
        and not schema_def
    ):
        return schema_kwargs

    # Below are functions used for producing this schema that have closed over this
    # scope and have access to the schema, cache, and newly defined types.

    # noinspection PyTypeChecker,PyUnresolvedReferences
    def replace_type(type_: GraphQLType) -> GraphQLType:
        if is_list_type(type_):
            return GraphQLList(replace_type(type_.of_type))  # type: ignore
        if is_non_null_type(type_):
            return GraphQLNonNull(replace_type(type_.of_type))  # type: ignore
        return replace_named_type(type_)  # type: ignore

    def replace_named_type(type_: GraphQLNamedType) -> GraphQLNamedType:
        # Note: While this could make early assertions to get the correctly
        # typed values below, that would throw immediately while type system
        # validation with validate_schema() will produce more actionable results.
        return type_map[type_.name]

    # noinspection PyShadowingNames
    def replace_directive(directive: GraphQLDirective) -> GraphQLDirective:
        kwargs = directive.to_kwargs()
        return GraphQLDirective(
            **merge_kwargs(
                kwargs,
                args={name: extend_arg(arg) for name, arg in kwargs["args"].items()},
            )
        )

    def extend_named_type(type_: GraphQLNamedType) -> GraphQLNamedType:
        if is_introspection_type(type_) or is_specified_scalar_type(type_):
            # Builtin types are not extended.
            return type_
        if is_scalar_type(type_):
            type_ = cast(GraphQLScalarType, type_)
            return extend_scalar_type(type_)
        if is_object_type(type_):
            type_ = cast(GraphQLObjectType, type_)
            return extend_object_type(type_)
        if is_interface_type(type_):
            type_ = cast(GraphQLInterfaceType, type_)
            return extend_interface_type(type_)
        if is_union_type(type_):
            type_ = cast(GraphQLUnionType, type_)
            return extend_union_type(type_)
        if is_enum_type(type_):
            type_ = cast(GraphQLEnumType, type_)
            return extend_enum_type(type_)
        if is_input_object_type(type_):
            type_ = cast(GraphQLInputObjectType, type_)
            return extend_input_object_type(type_)

        # Not reachable. All possible types have been considered.
        raise TypeError(f"Unexpected type: {inspect(type_)}.")  # pragma: no cover

    # noinspection PyShadowingNames
    def extend_input_object_type(
        type_: GraphQLInputObjectType,
    ) -> GraphQLInputObjectType:
        kwargs = type_.to_kwargs()
        extensions = tuple(type_extensions_map[kwargs["name"]])

        return GraphQLInputObjectType(
            **merge_kwargs(
                kwargs,
                fields=lambda: {
                    **{
                        name: GraphQLInputField(
                            **merge_kwargs(
                                field.to_kwargs(),
                                type_=replace_type(field.type),
                            )
                        )
                        for name, field in kwargs["fields"].items()
                    },
                    **build_input_field_map(extensions),
                },
                extension_ast_nodes=kwargs["extension_ast_nodes"] + extensions,
            )
        )

    def extend_enum_type(type_: GraphQLEnumType) -> GraphQLEnumType:
        kwargs = type_.to_kwargs()
        extensions = tuple(type_extensions_map[kwargs["name"]])

        return GraphQLEnumType(
            **merge_kwargs(
                kwargs,
                values={**kwargs["values"], **build_enum_value_map(extensions)},
                extension_ast_nodes=kwargs["extension_ast_nodes"] + extensions,
            )
        )

    def extend_scalar_type(type_: GraphQLScalarType) -> GraphQLScalarType:
        kwargs = type_.to_kwargs()
        extensions = tuple(type_extensions_map[kwargs["name"]])

        specified_by_url = kwargs["specified_by_url"]
        for extension_node in extensions:
            specified_by_url = get_specified_by_url(extension_node) or specified_by_url

        return GraphQLScalarType(
            **merge_kwargs(
                kwargs,
                specified_by_url=specified_by_url,
                extension_ast_nodes=kwargs["extension_ast_nodes"] + extensions,
            )
        )

    # noinspection PyShadowingNames
    def extend_object_type(type_: GraphQLObjectType) -> GraphQLObjectType:
        kwargs = type_.to_kwargs()
        extensions = tuple(type_extensions_map[kwargs["name"]])

        return GraphQLObjectType(
            **merge_kwargs(
                kwargs,
                interfaces=lambda: [
                    cast(GraphQLInterfaceType, replace_named_type(interface))
                    for interface in kwargs["interfaces"]
                ]
                + build_interfaces(extensions),
                fields=lambda: {
                    **{
                        name: extend_field(field)
                        for name, field in kwargs["fields"].items()
                    },
                    **build_field_map(extensions),
                },
                extension_ast_nodes=kwargs["extension_ast_nodes"] + extensions,
            )
        )

    # noinspection PyShadowingNames
    def extend_interface_type(type_: GraphQLInterfaceType) -> GraphQLInterfaceType:
        kwargs = type_.to_kwargs()
        extensions = tuple(type_extensions_map[kwargs["name"]])

        return GraphQLInterfaceType(
            **merge_kwargs(
                kwargs,
                interfaces=lambda: [
                    cast(GraphQLInterfaceType, replace_named_type(interface))
                    for interface in kwargs["interfaces"]
                ]
                + build_interfaces(extensions),
                fields=lambda: {
                    **{
                        name: extend_field(field)
                        for name, field in kwargs["fields"].items()
                    },
                    **build_field_map(extensions),
                },
                extension_ast_nodes=kwargs["extension_ast_nodes"] + extensions,
            )
        )

    def extend_union_type(type_: GraphQLUnionType) -> GraphQLUnionType:
        kwargs = type_.to_kwargs()
        extensions = tuple(type_extensions_map[kwargs["name"]])

        return GraphQLUnionType(
            **merge_kwargs(
                kwargs,
                types=lambda: [
                    cast(GraphQLObjectType, replace_named_type(member_type))
                    for member_type in kwargs["types"]
                ]
                + build_union_types(extensions),
                extension_ast_nodes=kwargs["extension_ast_nodes"] + extensions,
            )
        )

    # noinspection PyShadowingNames
    def extend_field(field: GraphQLField) -> GraphQLField:
        return GraphQLField(
            **merge_kwargs(
                field.to_kwargs(),
                type_=replace_type(field.type),
                args={name: extend_arg(arg) for name, arg in field.args.items()},
            )
        )

    def extend_arg(arg: GraphQLArgument) -> GraphQLArgument:
        return GraphQLArgument(
            **merge_kwargs(
                arg.to_kwargs(),
                type_=replace_type(arg.type),
            )
        )

    # noinspection PyShadowingNames
    def get_operation_types(
        nodes: Collection[Union[SchemaDefinitionNode, SchemaExtensionNode]]
    ) -> Dict[OperationType, GraphQLNamedType]:
        # Note: While this could make early assertions to get the correctly
        # typed values below, that would throw immediately while type system
        # validation with validate_schema() will produce more actionable results.
        return {
            operation_type.operation: get_named_type(operation_type.type)
            for node in nodes
            for operation_type in node.operation_types or []
        }

    # noinspection PyShadowingNames
    def get_named_type(node: NamedTypeNode) -> GraphQLNamedType:
        name = node.name.value
        type_ = std_type_map.get(name) or type_map.get(name)

        if not type_:
            raise TypeError(f"Unknown type: '{name}'.")
        return type_

    def get_wrapped_type(node: TypeNode) -> GraphQLType:
        if isinstance(node, ListTypeNode):
            return GraphQLList(get_wrapped_type(node.type))
        if isinstance(node, NonNullTypeNode):
            return GraphQLNonNull(
                cast(GraphQLNullableType, get_wrapped_type(node.type))
            )
        return get_named_type(cast(NamedTypeNode, node))

    def build_directive(node: DirectiveDefinitionNode) -> GraphQLDirective:
        locations = [DirectiveLocation[node.value] for node in node.locations]

        return GraphQLDirective(
            name=node.name.value,
            description=node.description.value if node.description else None,
            locations=locations,
            is_repeatable=node.repeatable,
            args=build_argument_map(node.arguments),
            ast_node=node,
        )

    def build_field_map(
        nodes: Collection[
            Union[
                InterfaceTypeDefinitionNode,
                InterfaceTypeExtensionNode,
                ObjectTypeDefinitionNode,
                ObjectTypeExtensionNode,
            ]
        ],
    ) -> GraphQLFieldMap:
        field_map: GraphQLFieldMap = {}
        for node in nodes:
            for field in node.fields or []:
                # Note: While this could make assertions to get the correctly typed
                # value, that would throw immediately while type system validation
                # with validate_schema() will produce more actionable results.
                field_map[field.name.value] = GraphQLField(
                    type_=cast(GraphQLOutputType, get_wrapped_type(field.type)),
                    description=field.description.value if field.description else None,
                    args=build_argument_map(field.arguments),
                    deprecation_reason=get_deprecation_reason(field),
                    ast_node=field,
                )
        return field_map

    def build_argument_map(
        args: Optional[Collection[InputValueDefinitionNode]],
    ) -> GraphQLArgumentMap:
        arg_map: GraphQLArgumentMap = {}
        for arg in args or []:
            # Note: While this could make assertions to get the correctly typed
            # value, that would throw immediately while type system validation
            # with validate_schema() will produce more actionable results.
            type_ = cast(GraphQLInputType, get_wrapped_type(arg.type))
            arg_map[arg.name.value] = GraphQLArgument(
                type_=type_,
                description=arg.description.value if arg.description else None,
                default_value=value_from_ast(arg.default_value, type_),
                deprecation_reason=get_deprecation_reason(arg),
                ast_node=arg,
            )
        return arg_map

    def build_input_field_map(
        nodes: Collection[
            Union[InputObjectTypeDefinitionNode, InputObjectTypeExtensionNode]
        ],
    ) -> GraphQLInputFieldMap:
        input_field_map: GraphQLInputFieldMap = {}
        for node in nodes:
            for field in node.fields or []:
                # Note: While this could make assertions to get the correctly typed
                # value, that would throw immediately while type system validation
                # with validate_schema() will produce more actionable results.
                type_ = cast(GraphQLInputType, get_wrapped_type(field.type))
                input_field_map[field.name.value] = GraphQLInputField(
                    type_=type_,
                    description=field.description.value if field.description else None,
                    default_value=value_from_ast(field.default_value, type_),
                    deprecation_reason=get_deprecation_reason(field),
                    ast_node=field,
                )
        return input_field_map

    def build_enum_value_map(
        nodes: Collection[Union[EnumTypeDefinitionNode, EnumTypeExtensionNode]]
    ) -> GraphQLEnumValueMap:
        enum_value_map: GraphQLEnumValueMap = {}
        for node in nodes:
            for value in node.values or []:
                # Note: While this could make assertions to get the correctly typed
                # value, that would throw immediately while type system validation
                # with validate_schema() will produce more actionable results.
                value_name = value.name.value
                enum_value_map[value_name] = GraphQLEnumValue(
                    value=value_name,
                    description=value.description.value if value.description else None,
                    deprecation_reason=get_deprecation_reason(value),
                    ast_node=value,
                )
        return enum_value_map

    def build_interfaces(
        nodes: Collection[
            Union[
                InterfaceTypeDefinitionNode,
                InterfaceTypeExtensionNode,
                ObjectTypeDefinitionNode,
                ObjectTypeExtensionNode,
            ]
        ],
    ) -> List[GraphQLInterfaceType]:
        interfaces: List[GraphQLInterfaceType] = []
        for node in nodes:
            for type_ in node.interfaces or []:
                # Note: While this could make assertions to get the correctly typed
                # value, that would throw immediately while type system validation
                # with validate_schema() will produce more actionable results.
                interfaces.append(cast(GraphQLInterfaceType, get_named_type(type_)))
        return interfaces

    def build_union_types(
        nodes: Collection[Union[UnionTypeDefinitionNode, UnionTypeExtensionNode]],
    ) -> List[GraphQLObjectType]:
        types: List[GraphQLObjectType] = []
        for node in nodes:
            for type_ in node.types or []:
                # Note: While this could make assertions to get the correctly typed
                # value, that would throw immediately while type system validation
                # with validate_schema() will produce more actionable results.
                types.append(cast(GraphQLObjectType, get_named_type(type_)))
        return types

    def build_object_type(ast_node: ObjectTypeDefinitionNode) -> GraphQLObjectType:
        extension_nodes = type_extensions_map[ast_node.name.value]
        all_nodes: List[Union[ObjectTypeDefinitionNode, ObjectTypeExtensionNode]] = [
            ast_node,
            *extension_nodes,
        ]
        return GraphQLObjectType(
            name=ast_node.name.value,
            description=ast_node.description.value if ast_node.description else None,
            interfaces=lambda: build_interfaces(all_nodes),
            fields=lambda: build_field_map(all_nodes),
            ast_node=ast_node,
            extension_ast_nodes=extension_nodes,
        )

    def build_interface_type(
        ast_node: InterfaceTypeDefinitionNode,
    ) -> GraphQLInterfaceType:
        extension_nodes = type_extensions_map[ast_node.name.value]
        all_nodes: List[
            Union[InterfaceTypeDefinitionNode, InterfaceTypeExtensionNode]
        ] = [ast_node, *extension_nodes]
        return GraphQLInterfaceType(
            name=ast_node.name.value,
            description=ast_node.description.value if ast_node.description else None,
            interfaces=lambda: build_interfaces(all_nodes),
            fields=lambda: build_field_map(all_nodes),
            ast_node=ast_node,
            extension_ast_nodes=extension_nodes,
        )

    def build_enum_type(ast_node: EnumTypeDefinitionNode) -> GraphQLEnumType:
        extension_nodes = type_extensions_map[ast_node.name.value]
        all_nodes: List[Union[EnumTypeDefinitionNode, EnumTypeExtensionNode]] = [
            ast_node,
            *extension_nodes,
        ]
        return GraphQLEnumType(
            name=ast_node.name.value,
            description=ast_node.description.value if ast_node.description else None,
            values=build_enum_value_map(all_nodes),
            ast_node=ast_node,
            extension_ast_nodes=extension_nodes,
        )

    def build_union_type(ast_node: UnionTypeDefinitionNode) -> GraphQLUnionType:
        extension_nodes = type_extensions_map[ast_node.name.value]
        all_nodes: List[Union[UnionTypeDefinitionNode, UnionTypeExtensionNode]] = [
            ast_node,
            *extension_nodes,
        ]
        return GraphQLUnionType(
            name=ast_node.name.value,
            description=ast_node.description.value if ast_node.description else None,
            types=lambda: build_union_types(all_nodes),
            ast_node=ast_node,
            extension_ast_nodes=extension_nodes,
        )

    def build_scalar_type(ast_node: ScalarTypeDefinitionNode) -> GraphQLScalarType:
        extension_nodes = type_extensions_map[ast_node.name.value]
        return GraphQLScalarType(
            name=ast_node.name.value,
            description=ast_node.description.value if ast_node.description else None,
            specified_by_url=get_specified_by_url(ast_node),
            ast_node=ast_node,
            extension_ast_nodes=extension_nodes,
        )

    def build_input_object_type(
        ast_node: InputObjectTypeDefinitionNode,
    ) -> GraphQLInputObjectType:
        extension_nodes = type_extensions_map[ast_node.name.value]
        all_nodes: List[
            Union[InputObjectTypeDefinitionNode, InputObjectTypeExtensionNode]
        ] = [ast_node, *extension_nodes]
        return GraphQLInputObjectType(
            name=ast_node.name.value,
            description=ast_node.description.value if ast_node.description else None,
            fields=lambda: build_input_field_map(all_nodes),
            ast_node=ast_node,
            extension_ast_nodes=extension_nodes,
        )

    build_type_for_kind = cast(
        Dict[str, Callable[[TypeDefinitionNode], GraphQLNamedType]],
        {
            "object_type_definition": build_object_type,
            "interface_type_definition": build_interface_type,
            "enum_type_definition": build_enum_type,
            "union_type_definition": build_union_type,
            "scalar_type_definition": build_scalar_type,
            "input_object_type_definition": build_input_object_type,
        },
    )

    def build_type(ast_node: TypeDefinitionNode) -> GraphQLNamedType:
        try:
            # object_type_definition_node is built with _build_object_type etc.
            build_function = build_type_for_kind[ast_node.kind]
        except KeyError:  # pragma: no cover
            # Not reachable. All possible type definition nodes have been considered.
            raise TypeError(  # pragma: no cover
                f"Unexpected type definition node: {inspect(ast_node)}."
            )
        else:
            return build_function(ast_node)

    type_map: Dict[str, GraphQLNamedType] = {}
    for existing_type in schema_kwargs["types"] or ():
        type_map[existing_type.name] = extend_named_type(existing_type)
    for type_node in type_defs:
        name = type_node.name.value
        type_map[name] = std_type_map.get(name) or build_type(type_node)

    # Get the extended root operation types.
    operation_types: Dict[OperationType, GraphQLNamedType] = {}
    for operation_type in OperationType:
        original_type = schema_kwargs[operation_type.value]
        if original_type:
            operation_types[operation_type] = replace_named_type(original_type)
    # Then, incorporate schema definition and all schema extensions.
    if schema_def:
        operation_types.update(get_operation_types([schema_def]))
    if schema_extensions:
        operation_types.update(get_operation_types(schema_extensions))

    # Then produce and return the kwargs for a Schema with these types.
    get_operation = operation_types.get
    return GraphQLSchemaKwargs(
        query=get_operation(OperationType.QUERY),  # type: ignore
        mutation=get_operation(OperationType.MUTATION),  # type: ignore
        subscription=get_operation(OperationType.SUBSCRIPTION),  # type: ignore
        types=tuple(type_map.values()),
        directives=tuple(
            replace_directive(directive) for directive in schema_kwargs["directives"]
        )
        + tuple(build_directive(directive) for directive in directive_defs),
        description=schema_def.description.value
        if schema_def and schema_def.description
        else None,
        extensions={},
        ast_node=schema_def or schema_kwargs["ast_node"],
        extension_ast_nodes=schema_kwargs["extension_ast_nodes"]
        + tuple(schema_extensions),
        assume_valid=assume_valid,
    )


std_type_map: Mapping[str, Union[GraphQLNamedType, GraphQLObjectType]] = {
    **specified_scalar_types,
    **introspection_types,
}


def get_deprecation_reason(
    node: Union[EnumValueDefinitionNode, FieldDefinitionNode, InputValueDefinitionNode]
) -> Optional[str]:
    """Given a field or enum value node, get deprecation reason as string."""
    from ..execution import get_directive_values

    deprecated = get_directive_values(GraphQLDeprecatedDirective, node)
    return deprecated["reason"] if deprecated else None


def get_specified_by_url(
    node: Union[ScalarTypeDefinitionNode, ScalarTypeExtensionNode]
) -> Optional[str]:
    """Given a scalar node, return the string value for the specifiedByURL."""
    from ..execution import get_directive_values

    specified_by_url = get_directive_values(GraphQLSpecifiedByDirective, node)
    return specified_by_url["url"] if specified_by_url else None
