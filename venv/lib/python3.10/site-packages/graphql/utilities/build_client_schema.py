from itertools import chain
from typing import cast, Callable, Collection, Dict, List, Union

from ..language import DirectiveLocation, parse_value
from ..pyutils import inspect, Undefined
from ..type import (
    GraphQLArgument,
    GraphQLDirective,
    GraphQLEnumType,
    GraphQLEnumValue,
    GraphQLField,
    GraphQLInputField,
    GraphQLInputObjectType,
    GraphQLInputType,
    GraphQLInterfaceType,
    GraphQLList,
    GraphQLNamedType,
    GraphQLNonNull,
    GraphQLObjectType,
    GraphQLOutputType,
    GraphQLScalarType,
    GraphQLSchema,
    GraphQLType,
    GraphQLUnionType,
    TypeKind,
    assert_interface_type,
    assert_nullable_type,
    assert_object_type,
    introspection_types,
    is_input_type,
    is_output_type,
    specified_scalar_types,
)
from .get_introspection_query import (
    IntrospectionDirective,
    IntrospectionEnumType,
    IntrospectionField,
    IntrospectionInterfaceType,
    IntrospectionInputObjectType,
    IntrospectionInputValue,
    IntrospectionObjectType,
    IntrospectionQuery,
    IntrospectionScalarType,
    IntrospectionType,
    IntrospectionTypeRef,
    IntrospectionUnionType,
)
from .value_from_ast import value_from_ast

__all__ = ["build_client_schema"]


def build_client_schema(
    introspection: IntrospectionQuery, assume_valid: bool = False
) -> GraphQLSchema:
    """Build a GraphQLSchema for use by client tools.

    Given the result of a client running the introspection query, creates and returns
    a GraphQLSchema instance which can be then used with all GraphQL-core 3 tools,
    but cannot be used to execute a query, as introspection does not represent the
    "resolver", "parse" or "serialize" functions or any other server-internal
    mechanisms.

    This function expects a complete introspection result. Don't forget to check the
    "errors" field of a server response before calling this function.
    """
    if not isinstance(introspection, dict) or not isinstance(
        introspection.get("__schema"), dict
    ):
        raise TypeError(
            "Invalid or incomplete introspection result. Ensure that you"
            " are passing the 'data' attribute of an introspection response"
            f" and no 'errors' were returned alongside: {inspect(introspection)}."
        )

    # Get the schema from the introspection result.
    schema_introspection = introspection["__schema"]

    # Given a type reference in introspection, return the GraphQLType instance,
    # preferring cached instances before building new instances.
    def get_type(type_ref: IntrospectionTypeRef) -> GraphQLType:
        kind = type_ref.get("kind")
        if kind == TypeKind.LIST.name:
            item_ref = type_ref.get("ofType")
            if not item_ref:
                raise TypeError("Decorated type deeper than introspection query.")
            item_ref = cast(IntrospectionTypeRef, item_ref)
            return GraphQLList(get_type(item_ref))
        if kind == TypeKind.NON_NULL.name:
            nullable_ref = type_ref.get("ofType")
            if not nullable_ref:
                raise TypeError("Decorated type deeper than introspection query.")
            nullable_ref = cast(IntrospectionTypeRef, nullable_ref)
            nullable_type = get_type(nullable_ref)
            return GraphQLNonNull(assert_nullable_type(nullable_type))
        type_ref = cast(IntrospectionType, type_ref)
        return get_named_type(type_ref)

    def get_named_type(type_ref: IntrospectionType) -> GraphQLNamedType:
        type_name = type_ref.get("name")
        if not type_name:
            raise TypeError(f"Unknown type reference: {inspect(type_ref)}.")

        type_ = type_map.get(type_name)
        if not type_:
            raise TypeError(
                f"Invalid or incomplete schema, unknown type: {type_name}."
                " Ensure that a full introspection query is used in order"
                " to build a client schema."
            )
        return type_

    def get_object_type(type_ref: IntrospectionObjectType) -> GraphQLObjectType:
        return assert_object_type(get_type(type_ref))

    def get_interface_type(
        type_ref: IntrospectionInterfaceType,
    ) -> GraphQLInterfaceType:
        return assert_interface_type(get_type(type_ref))

    # Given a type's introspection result, construct the correct GraphQLType instance.
    def build_type(type_: IntrospectionType) -> GraphQLNamedType:
        if type_ and "name" in type_ and "kind" in type_:
            builder = type_builders.get(type_["kind"])
            if builder:  # pragma: no cover else
                return builder(type_)
        raise TypeError(
            "Invalid or incomplete introspection result."
            " Ensure that a full introspection query is used in order"
            f" to build a client schema: {inspect(type_)}."
        )

    def build_scalar_def(
        scalar_introspection: IntrospectionScalarType,
    ) -> GraphQLScalarType:
        return GraphQLScalarType(
            name=scalar_introspection["name"],
            description=scalar_introspection.get("description"),
            specified_by_url=scalar_introspection.get("specifiedByURL"),
        )

    def build_implementations_list(
        implementing_introspection: Union[
            IntrospectionObjectType, IntrospectionInterfaceType
        ],
    ) -> List[GraphQLInterfaceType]:
        maybe_interfaces = implementing_introspection.get("interfaces")
        if maybe_interfaces is None:
            # Temporary workaround until GraphQL ecosystem will fully support
            # 'interfaces' on interface types
            if implementing_introspection["kind"] == TypeKind.INTERFACE.name:
                return []
            raise TypeError(
                "Introspection result missing interfaces:"
                f" {inspect(implementing_introspection)}."
            )
        interfaces = cast(Collection[IntrospectionInterfaceType], maybe_interfaces)
        return [get_interface_type(interface) for interface in interfaces]

    def build_object_def(
        object_introspection: IntrospectionObjectType,
    ) -> GraphQLObjectType:
        return GraphQLObjectType(
            name=object_introspection["name"],
            description=object_introspection.get("description"),
            interfaces=lambda: build_implementations_list(object_introspection),
            fields=lambda: build_field_def_map(object_introspection),
        )

    def build_interface_def(
        interface_introspection: IntrospectionInterfaceType,
    ) -> GraphQLInterfaceType:
        return GraphQLInterfaceType(
            name=interface_introspection["name"],
            description=interface_introspection.get("description"),
            interfaces=lambda: build_implementations_list(interface_introspection),
            fields=lambda: build_field_def_map(interface_introspection),
        )

    def build_union_def(
        union_introspection: IntrospectionUnionType,
    ) -> GraphQLUnionType:
        maybe_possible_types = union_introspection.get("possibleTypes")
        if maybe_possible_types is None:
            raise TypeError(
                "Introspection result missing possibleTypes:"
                f" {inspect(union_introspection)}."
            )
        possible_types = cast(Collection[IntrospectionObjectType], maybe_possible_types)
        return GraphQLUnionType(
            name=union_introspection["name"],
            description=union_introspection.get("description"),
            types=lambda: [get_object_type(type_) for type_ in possible_types],
        )

    def build_enum_def(enum_introspection: IntrospectionEnumType) -> GraphQLEnumType:
        if enum_introspection.get("enumValues") is None:
            raise TypeError(
                "Introspection result missing enumValues:"
                f" {inspect(enum_introspection)}."
            )
        return GraphQLEnumType(
            name=enum_introspection["name"],
            description=enum_introspection.get("description"),
            values={
                value_introspect["name"]: GraphQLEnumValue(
                    value=value_introspect["name"],
                    description=value_introspect.get("description"),
                    deprecation_reason=value_introspect.get("deprecationReason"),
                )
                for value_introspect in enum_introspection["enumValues"]
            },
        )

    def build_input_object_def(
        input_object_introspection: IntrospectionInputObjectType,
    ) -> GraphQLInputObjectType:
        if input_object_introspection.get("inputFields") is None:
            raise TypeError(
                "Introspection result missing inputFields:"
                f" {inspect(input_object_introspection)}."
            )
        return GraphQLInputObjectType(
            name=input_object_introspection["name"],
            description=input_object_introspection.get("description"),
            fields=lambda: build_input_value_def_map(
                input_object_introspection["inputFields"]
            ),
        )

    type_builders: Dict[str, Callable[[IntrospectionType], GraphQLNamedType]] = {
        TypeKind.SCALAR.name: build_scalar_def,  # type: ignore
        TypeKind.OBJECT.name: build_object_def,  # type: ignore
        TypeKind.INTERFACE.name: build_interface_def,  # type: ignore
        TypeKind.UNION.name: build_union_def,  # type: ignore
        TypeKind.ENUM.name: build_enum_def,  # type: ignore
        TypeKind.INPUT_OBJECT.name: build_input_object_def,  # type: ignore
    }

    def build_field_def_map(
        type_introspection: Union[IntrospectionObjectType, IntrospectionInterfaceType],
    ) -> Dict[str, GraphQLField]:
        if type_introspection.get("fields") is None:
            raise TypeError(
                f"Introspection result missing fields: {type_introspection}."
            )
        return {
            field_introspection["name"]: build_field(field_introspection)
            for field_introspection in type_introspection["fields"]
        }

    def build_field(field_introspection: IntrospectionField) -> GraphQLField:
        type_introspection = cast(IntrospectionType, field_introspection["type"])
        type_ = get_type(type_introspection)
        if not is_output_type(type_):
            raise TypeError(
                "Introspection must provide output type for fields,"
                f" but received: {inspect(type_)}."
            )
        type_ = cast(GraphQLOutputType, type_)

        args_introspection = field_introspection.get("args")
        if args_introspection is None:
            raise TypeError(
                "Introspection result missing field args:"
                f" {inspect(field_introspection)}."
            )

        return GraphQLField(
            type_,
            args=build_argument_def_map(args_introspection),
            description=field_introspection.get("description"),
            deprecation_reason=field_introspection.get("deprecationReason"),
        )

    def build_argument_def_map(
        argument_value_introspections: Collection[IntrospectionInputValue],
    ) -> Dict[str, GraphQLArgument]:
        return {
            argument_introspection["name"]: build_argument(argument_introspection)
            for argument_introspection in argument_value_introspections
        }

    def build_argument(
        argument_introspection: IntrospectionInputValue,
    ) -> GraphQLArgument:
        type_introspection = cast(IntrospectionType, argument_introspection["type"])
        type_ = get_type(type_introspection)
        if not is_input_type(type_):
            raise TypeError(
                "Introspection must provide input type for arguments,"
                f" but received: {inspect(type_)}."
            )
        type_ = cast(GraphQLInputType, type_)

        default_value_introspection = argument_introspection.get("defaultValue")
        default_value = (
            Undefined
            if default_value_introspection is None
            else value_from_ast(parse_value(default_value_introspection), type_)
        )
        return GraphQLArgument(
            type_,
            default_value=default_value,
            description=argument_introspection.get("description"),
            deprecation_reason=argument_introspection.get("deprecationReason"),
        )

    def build_input_value_def_map(
        input_value_introspections: Collection[IntrospectionInputValue],
    ) -> Dict[str, GraphQLInputField]:
        return {
            input_value_introspection["name"]: build_input_value(
                input_value_introspection
            )
            for input_value_introspection in input_value_introspections
        }

    def build_input_value(
        input_value_introspection: IntrospectionInputValue,
    ) -> GraphQLInputField:
        type_introspection = cast(IntrospectionType, input_value_introspection["type"])
        type_ = get_type(type_introspection)
        if not is_input_type(type_):
            raise TypeError(
                "Introspection must provide input type for input fields,"
                f" but received: {inspect(type_)}."
            )
        type_ = cast(GraphQLInputType, type_)

        default_value_introspection = input_value_introspection.get("defaultValue")
        default_value = (
            Undefined
            if default_value_introspection is None
            else value_from_ast(parse_value(default_value_introspection), type_)
        )
        return GraphQLInputField(
            type_,
            default_value=default_value,
            description=input_value_introspection.get("description"),
            deprecation_reason=input_value_introspection.get("deprecationReason"),
        )

    def build_directive(
        directive_introspection: IntrospectionDirective,
    ) -> GraphQLDirective:
        if directive_introspection.get("args") is None:
            raise TypeError(
                "Introspection result missing directive args:"
                f" {inspect(directive_introspection)}."
            )
        if directive_introspection.get("locations") is None:
            raise TypeError(
                "Introspection result missing directive locations:"
                f" {inspect(directive_introspection)}."
            )
        return GraphQLDirective(
            name=directive_introspection["name"],
            description=directive_introspection.get("description"),
            is_repeatable=directive_introspection.get("isRepeatable", False),
            locations=list(
                cast(
                    Collection[DirectiveLocation],
                    directive_introspection.get("locations"),
                )
            ),
            args=build_argument_def_map(directive_introspection["args"]),
        )

    # Iterate through all types, getting the type definition for each.
    type_map: Dict[str, GraphQLNamedType] = {
        type_introspection["name"]: build_type(type_introspection)
        for type_introspection in schema_introspection["types"]
    }

    # Include standard types only if they are used.
    for std_type_name, std_type in chain(
        specified_scalar_types.items(), introspection_types.items()
    ):
        if std_type_name in type_map:
            type_map[std_type_name] = std_type

    # Get the root Query, Mutation, and Subscription types.
    query_type_ref = schema_introspection.get("queryType")
    query_type = None if query_type_ref is None else get_object_type(query_type_ref)
    mutation_type_ref = schema_introspection.get("mutationType")
    mutation_type = (
        None if mutation_type_ref is None else get_object_type(mutation_type_ref)
    )
    subscription_type_ref = schema_introspection.get("subscriptionType")
    subscription_type = (
        None
        if subscription_type_ref is None
        else get_object_type(subscription_type_ref)
    )

    # Get the directives supported by Introspection, assuming empty-set if directives
    # were not queried for.
    directive_introspections = schema_introspection.get("directives")
    directives = (
        [
            build_directive(directive_introspection)
            for directive_introspection in directive_introspections
        ]
        if directive_introspections
        else []
    )

    # Then produce and return a Schema with these types.
    return GraphQLSchema(
        query=query_type,
        mutation=mutation_type,
        subscription=subscription_type,
        types=list(type_map.values()),
        directives=directives,
        description=schema_introspection.get("description"),
        assume_valid=assume_valid,
    )
