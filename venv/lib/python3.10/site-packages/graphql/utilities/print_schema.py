from typing import Any, Callable, Dict, List, Optional, Union, cast

from ..language import print_ast, StringValueNode
from ..language.block_string import is_printable_as_block_string
from ..pyutils import inspect
from ..type import (
    DEFAULT_DEPRECATION_REASON,
    GraphQLArgument,
    GraphQLDirective,
    GraphQLEnumType,
    GraphQLEnumValue,
    GraphQLInputObjectType,
    GraphQLInputType,
    GraphQLInterfaceType,
    GraphQLNamedType,
    GraphQLObjectType,
    GraphQLScalarType,
    GraphQLSchema,
    GraphQLUnionType,
    is_enum_type,
    is_input_object_type,
    is_interface_type,
    is_introspection_type,
    is_object_type,
    is_scalar_type,
    is_specified_directive,
    is_specified_scalar_type,
    is_union_type,
)
from .ast_from_value import ast_from_value

__all__ = ["print_schema", "print_introspection_schema", "print_type", "print_value"]


def print_schema(schema: GraphQLSchema) -> str:
    return print_filtered_schema(
        schema, lambda n: not is_specified_directive(n), is_defined_type
    )


def print_introspection_schema(schema: GraphQLSchema) -> str:
    return print_filtered_schema(schema, is_specified_directive, is_introspection_type)


def is_defined_type(type_: GraphQLNamedType) -> bool:
    return not is_specified_scalar_type(type_) and not is_introspection_type(type_)


def print_filtered_schema(
    schema: GraphQLSchema,
    directive_filter: Callable[[GraphQLDirective], bool],
    type_filter: Callable[[GraphQLNamedType], bool],
) -> str:
    directives = filter(directive_filter, schema.directives)
    types = filter(type_filter, schema.type_map.values())

    return "\n\n".join(
        (
            *filter(None, (print_schema_definition(schema),)),
            *map(print_directive, directives),
            *map(print_type, types),
        )
    )


def print_schema_definition(schema: GraphQLSchema) -> Optional[str]:
    if schema.description is None and is_schema_of_common_names(schema):
        return None

    operation_types = []

    query_type = schema.query_type
    if query_type:
        operation_types.append(f"  query: {query_type.name}")

    mutation_type = schema.mutation_type
    if mutation_type:
        operation_types.append(f"  mutation: {mutation_type.name}")

    subscription_type = schema.subscription_type
    if subscription_type:
        operation_types.append(f"  subscription: {subscription_type.name}")

    return print_description(schema) + "schema {\n" + "\n".join(operation_types) + "\n}"


def is_schema_of_common_names(schema: GraphQLSchema) -> bool:
    """Check whether this schema uses the common naming convention.

    GraphQL schema define root types for each type of operation. These types are the
    same as any other type and can be named in any manner, however there is a common
    naming convention:

    schema {
      query: Query
      mutation: Mutation
      subscription: Subscription
    }

    When using this naming convention, the schema description can be omitted.
    """
    query_type = schema.query_type
    if query_type and query_type.name != "Query":
        return False

    mutation_type = schema.mutation_type
    if mutation_type and mutation_type.name != "Mutation":
        return False

    subscription_type = schema.subscription_type
    return not subscription_type or subscription_type.name == "Subscription"


def print_type(type_: GraphQLNamedType) -> str:
    if is_scalar_type(type_):
        type_ = cast(GraphQLScalarType, type_)
        return print_scalar(type_)
    if is_object_type(type_):
        type_ = cast(GraphQLObjectType, type_)
        return print_object(type_)
    if is_interface_type(type_):
        type_ = cast(GraphQLInterfaceType, type_)
        return print_interface(type_)
    if is_union_type(type_):
        type_ = cast(GraphQLUnionType, type_)
        return print_union(type_)
    if is_enum_type(type_):
        type_ = cast(GraphQLEnumType, type_)
        return print_enum(type_)
    if is_input_object_type(type_):
        type_ = cast(GraphQLInputObjectType, type_)
        return print_input_object(type_)

    # Not reachable. All possible types have been considered.
    raise TypeError(f"Unexpected type: {inspect(type_)}.")


def print_scalar(type_: GraphQLScalarType) -> str:
    return (
        print_description(type_)
        + f"scalar {type_.name}"
        + print_specified_by_url(type_)
    )


def print_implemented_interfaces(
    type_: Union[GraphQLObjectType, GraphQLInterfaceType]
) -> str:
    interfaces = type_.interfaces
    return " implements " + " & ".join(i.name for i in interfaces) if interfaces else ""


def print_object(type_: GraphQLObjectType) -> str:
    return (
        print_description(type_)
        + f"type {type_.name}"
        + print_implemented_interfaces(type_)
        + print_fields(type_)
    )


def print_interface(type_: GraphQLInterfaceType) -> str:
    return (
        print_description(type_)
        + f"interface {type_.name}"
        + print_implemented_interfaces(type_)
        + print_fields(type_)
    )


def print_union(type_: GraphQLUnionType) -> str:
    types = type_.types
    possible_types = " = " + " | ".join(t.name for t in types) if types else ""
    return print_description(type_) + f"union {type_.name}" + possible_types


def print_enum(type_: GraphQLEnumType) -> str:
    values = [
        print_description(value, "  ", not i)
        + f"  {name}"
        + print_deprecated(value.deprecation_reason)
        for i, (name, value) in enumerate(type_.values.items())
    ]
    return print_description(type_) + f"enum {type_.name}" + print_block(values)


def print_input_object(type_: GraphQLInputObjectType) -> str:
    fields = [
        print_description(field, "  ", not i) + "  " + print_input_value(name, field)
        for i, (name, field) in enumerate(type_.fields.items())
    ]
    return print_description(type_) + f"input {type_.name}" + print_block(fields)


def print_fields(type_: Union[GraphQLObjectType, GraphQLInterfaceType]) -> str:
    fields = [
        print_description(field, "  ", not i)
        + f"  {name}"
        + print_args(field.args, "  ")
        + f": {field.type}"
        + print_deprecated(field.deprecation_reason)
        for i, (name, field) in enumerate(type_.fields.items())
    ]
    return print_block(fields)


def print_block(items: List[str]) -> str:
    return " {\n" + "\n".join(items) + "\n}" if items else ""


def print_args(args: Dict[str, GraphQLArgument], indentation: str = "") -> str:
    if not args:
        return ""

    # If every arg does not have a description, print them on one line.
    if not any(arg.description for arg in args.values()):
        return (
            "("
            + ", ".join(print_input_value(name, arg) for name, arg in args.items())
            + ")"
        )

    return (
        "(\n"
        + "\n".join(
            print_description(arg, f"  {indentation}", not i)
            + f"  {indentation}"
            + print_input_value(name, arg)
            for i, (name, arg) in enumerate(args.items())
        )
        + f"\n{indentation})"
    )


def print_input_value(name: str, arg: GraphQLArgument) -> str:
    default_ast = ast_from_value(arg.default_value, arg.type)
    arg_decl = f"{name}: {arg.type}"
    if default_ast:
        arg_decl += f" = {print_ast(default_ast)}"
    return arg_decl + print_deprecated(arg.deprecation_reason)


def print_directive(directive: GraphQLDirective) -> str:
    return (
        print_description(directive)
        + f"directive @{directive.name}"
        + print_args(directive.args)
        + (" repeatable" if directive.is_repeatable else "")
        + " on "
        + " | ".join(location.name for location in directive.locations)
    )


def print_deprecated(reason: Optional[str]) -> str:
    if reason is None:
        return ""
    if reason != DEFAULT_DEPRECATION_REASON:
        ast_value = print_ast(StringValueNode(value=reason))
        return f" @deprecated(reason: {ast_value})"
    return " @deprecated"


def print_specified_by_url(scalar: GraphQLScalarType) -> str:
    if scalar.specified_by_url is None:
        return ""
    ast_value = print_ast(StringValueNode(value=scalar.specified_by_url))
    return f" @specifiedBy(url: {ast_value})"


def print_description(
    def_: Union[
        GraphQLArgument,
        GraphQLDirective,
        GraphQLEnumValue,
        GraphQLNamedType,
        GraphQLSchema,
    ],
    indentation: str = "",
    first_in_block: bool = True,
) -> str:
    description = def_.description
    if description is None:
        return ""

    block_string = print_ast(
        StringValueNode(
            value=description, block=is_printable_as_block_string(description)
        )
    )

    prefix = "\n" + indentation if indentation and not first_in_block else indentation

    return prefix + block_string.replace("\n", "\n" + indentation) + "\n"


def print_value(value: Any, type_: GraphQLInputType) -> str:
    """@deprecated: Convenience function for printing a Python value"""
    return print_ast(ast_from_value(value, type_))  # type: ignore
