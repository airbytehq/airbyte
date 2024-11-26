from enum import Enum
from typing import Any, Collection, Dict, List, NamedTuple, Union, cast

from ..language import print_ast
from ..pyutils import inspect, Undefined
from ..type import (
    GraphQLEnumType,
    GraphQLField,
    GraphQLList,
    GraphQLNamedType,
    GraphQLNonNull,
    GraphQLInputType,
    GraphQLInterfaceType,
    GraphQLObjectType,
    GraphQLSchema,
    GraphQLType,
    GraphQLUnionType,
    is_enum_type,
    is_input_object_type,
    is_interface_type,
    is_list_type,
    is_named_type,
    is_non_null_type,
    is_object_type,
    is_required_argument,
    is_required_input_field,
    is_scalar_type,
    is_specified_scalar_type,
    is_union_type,
)
from ..utilities.sort_value_node import sort_value_node
from .ast_from_value import ast_from_value

__all__ = [
    "BreakingChange",
    "BreakingChangeType",
    "DangerousChange",
    "DangerousChangeType",
    "find_breaking_changes",
    "find_dangerous_changes",
]


class BreakingChangeType(Enum):
    TYPE_REMOVED = 10
    TYPE_CHANGED_KIND = 11
    TYPE_REMOVED_FROM_UNION = 20
    VALUE_REMOVED_FROM_ENUM = 21
    REQUIRED_INPUT_FIELD_ADDED = 22
    IMPLEMENTED_INTERFACE_REMOVED = 23
    FIELD_REMOVED = 30
    FIELD_CHANGED_KIND = 31
    REQUIRED_ARG_ADDED = 40
    ARG_REMOVED = 41
    ARG_CHANGED_KIND = 42
    DIRECTIVE_REMOVED = 50
    DIRECTIVE_ARG_REMOVED = 51
    REQUIRED_DIRECTIVE_ARG_ADDED = 52
    DIRECTIVE_REPEATABLE_REMOVED = 53
    DIRECTIVE_LOCATION_REMOVED = 54


class DangerousChangeType(Enum):
    VALUE_ADDED_TO_ENUM = 60
    TYPE_ADDED_TO_UNION = 61
    OPTIONAL_INPUT_FIELD_ADDED = 62
    OPTIONAL_ARG_ADDED = 63
    IMPLEMENTED_INTERFACE_ADDED = 64
    ARG_DEFAULT_VALUE_CHANGE = 65


class BreakingChange(NamedTuple):
    type: BreakingChangeType
    description: str


class DangerousChange(NamedTuple):
    type: DangerousChangeType
    description: str


Change = Union[BreakingChange, DangerousChange]


def find_breaking_changes(
    old_schema: GraphQLSchema, new_schema: GraphQLSchema
) -> List[BreakingChange]:
    """Find breaking changes.

    Given two schemas, returns a list containing descriptions of all the types of
    breaking changes covered by the other functions down below.
    """
    return [
        change
        for change in find_schema_changes(old_schema, new_schema)
        if isinstance(change.type, BreakingChangeType)
    ]


def find_dangerous_changes(
    old_schema: GraphQLSchema, new_schema: GraphQLSchema
) -> List[DangerousChange]:
    """Find dangerous changes.

    Given two schemas, returns a list containing descriptions of all the types of
    potentially dangerous changes covered by the other functions down below.
    """
    return [
        change
        for change in find_schema_changes(old_schema, new_schema)
        if isinstance(change.type, DangerousChangeType)
    ]


def find_schema_changes(
    old_schema: GraphQLSchema, new_schema: GraphQLSchema
) -> List[Change]:
    return find_type_changes(old_schema, new_schema) + find_directive_changes(
        old_schema, new_schema
    )


def find_directive_changes(
    old_schema: GraphQLSchema, new_schema: GraphQLSchema
) -> List[Change]:
    schema_changes: List[Change] = []

    directives_diff = list_diff(old_schema.directives, new_schema.directives)

    for directive in directives_diff.removed:
        schema_changes.append(
            BreakingChange(
                BreakingChangeType.DIRECTIVE_REMOVED, f"{directive.name} was removed."
            )
        )

    for (old_directive, new_directive) in directives_diff.persisted:
        args_diff = dict_diff(old_directive.args, new_directive.args)

        for arg_name, new_arg in args_diff.added.items():
            if is_required_argument(new_arg):
                schema_changes.append(
                    BreakingChange(
                        BreakingChangeType.REQUIRED_DIRECTIVE_ARG_ADDED,
                        f"A required arg {arg_name} on directive"
                        f" {old_directive.name} was added.",
                    )
                )

        for arg_name in args_diff.removed:
            schema_changes.append(
                BreakingChange(
                    BreakingChangeType.DIRECTIVE_ARG_REMOVED,
                    f"{arg_name} was removed from {new_directive.name}.",
                )
            )

        if old_directive.is_repeatable and not new_directive.is_repeatable:
            schema_changes.append(
                BreakingChange(
                    BreakingChangeType.DIRECTIVE_REPEATABLE_REMOVED,
                    f"Repeatable flag was removed from {old_directive.name}.",
                )
            )

        for location in old_directive.locations:
            if location not in new_directive.locations:
                schema_changes.append(
                    BreakingChange(
                        BreakingChangeType.DIRECTIVE_LOCATION_REMOVED,
                        f"{location.name} was removed from {new_directive.name}.",
                    )
                )

    return schema_changes


def find_type_changes(
    old_schema: GraphQLSchema, new_schema: GraphQLSchema
) -> List[Change]:
    schema_changes: List[Change] = []
    types_diff = dict_diff(old_schema.type_map, new_schema.type_map)

    for type_name, old_type in types_diff.removed.items():
        schema_changes.append(
            BreakingChange(
                BreakingChangeType.TYPE_REMOVED,
                f"Standard scalar {type_name} was removed"
                " because it is not referenced anymore."
                if is_specified_scalar_type(old_type)
                else f"{type_name} was removed.",
            )
        )

    for type_name, (old_type, new_type) in types_diff.persisted.items():
        if is_enum_type(old_type) and is_enum_type(new_type):
            schema_changes.extend(find_enum_type_changes(old_type, new_type))
        elif is_union_type(old_type) and is_union_type(new_type):
            schema_changes.extend(find_union_type_changes(old_type, new_type))
        elif is_input_object_type(old_type) and is_input_object_type(new_type):
            schema_changes.extend(find_input_object_type_changes(old_type, new_type))
        elif is_object_type(old_type) and is_object_type(new_type):
            schema_changes.extend(find_field_changes(old_type, new_type))
            schema_changes.extend(
                find_implemented_interfaces_changes(old_type, new_type)
            )
        elif is_interface_type(old_type) and is_interface_type(new_type):
            schema_changes.extend(find_field_changes(old_type, new_type))
            schema_changes.extend(
                find_implemented_interfaces_changes(old_type, new_type)
            )
        elif old_type.__class__ is not new_type.__class__:
            schema_changes.append(
                BreakingChange(
                    BreakingChangeType.TYPE_CHANGED_KIND,
                    f"{type_name} changed from {type_kind_name(old_type)}"
                    f" to {type_kind_name(new_type)}.",
                )
            )

    return schema_changes


def find_input_object_type_changes(
    old_type: Union[GraphQLObjectType, GraphQLInterfaceType],
    new_type: Union[GraphQLObjectType, GraphQLInterfaceType],
) -> List[Change]:
    schema_changes: List[Change] = []
    fields_diff = dict_diff(old_type.fields, new_type.fields)

    for field_name, new_field in fields_diff.added.items():
        if is_required_input_field(new_field):
            schema_changes.append(
                BreakingChange(
                    BreakingChangeType.REQUIRED_INPUT_FIELD_ADDED,
                    f"A required field {field_name} on"
                    f" input type {old_type.name} was added.",
                )
            )
        else:
            schema_changes.append(
                DangerousChange(
                    DangerousChangeType.OPTIONAL_INPUT_FIELD_ADDED,
                    f"An optional field {field_name} on"
                    f" input type {old_type.name} was added.",
                )
            )

    for field_name in fields_diff.removed:
        schema_changes.append(
            BreakingChange(
                BreakingChangeType.FIELD_REMOVED,
                f"{old_type.name}.{field_name} was removed.",
            )
        )

    for field_name, (old_field, new_field) in fields_diff.persisted.items():
        is_safe = is_change_safe_for_input_object_field_or_field_arg(
            old_field.type, new_field.type
        )
        if not is_safe:
            schema_changes.append(
                BreakingChange(
                    BreakingChangeType.FIELD_CHANGED_KIND,
                    f"{old_type.name}.{field_name} changed type"
                    f" from {old_field.type} to {new_field.type}.",
                )
            )

    return schema_changes


def find_union_type_changes(
    old_type: GraphQLUnionType, new_type: GraphQLUnionType
) -> List[Change]:
    schema_changes: List[Change] = []
    possible_types_diff = list_diff(old_type.types, new_type.types)

    for possible_type in possible_types_diff.added:
        schema_changes.append(
            DangerousChange(
                DangerousChangeType.TYPE_ADDED_TO_UNION,
                f"{possible_type.name} was added" f" to union type {old_type.name}.",
            )
        )

    for possible_type in possible_types_diff.removed:
        schema_changes.append(
            BreakingChange(
                BreakingChangeType.TYPE_REMOVED_FROM_UNION,
                f"{possible_type.name} was removed from union type {old_type.name}.",
            )
        )

    return schema_changes


def find_enum_type_changes(
    old_type: GraphQLEnumType, new_type: GraphQLEnumType
) -> List[Change]:
    schema_changes: List[Change] = []
    values_diff = dict_diff(old_type.values, new_type.values)

    for value_name in values_diff.added:
        schema_changes.append(
            DangerousChange(
                DangerousChangeType.VALUE_ADDED_TO_ENUM,
                f"{value_name} was added to enum type {old_type.name}.",
            )
        )

    for value_name in values_diff.removed:
        schema_changes.append(
            BreakingChange(
                BreakingChangeType.VALUE_REMOVED_FROM_ENUM,
                f"{value_name} was removed from enum type {old_type.name}.",
            )
        )

    return schema_changes


def find_implemented_interfaces_changes(
    old_type: Union[GraphQLObjectType, GraphQLInterfaceType],
    new_type: Union[GraphQLObjectType, GraphQLInterfaceType],
) -> List[Change]:
    schema_changes: List[Change] = []
    interfaces_diff = list_diff(old_type.interfaces, new_type.interfaces)

    for interface in interfaces_diff.added:
        schema_changes.append(
            DangerousChange(
                DangerousChangeType.IMPLEMENTED_INTERFACE_ADDED,
                f"{interface.name} added to interfaces implemented by {old_type.name}.",
            )
        )

    for interface in interfaces_diff.removed:
        schema_changes.append(
            BreakingChange(
                BreakingChangeType.IMPLEMENTED_INTERFACE_REMOVED,
                f"{old_type.name} no longer implements interface {interface.name}.",
            )
        )

    return schema_changes


def find_field_changes(
    old_type: Union[GraphQLObjectType, GraphQLInterfaceType],
    new_type: Union[GraphQLObjectType, GraphQLInterfaceType],
) -> List[Change]:
    schema_changes: List[Change] = []
    fields_diff = dict_diff(old_type.fields, new_type.fields)

    for field_name in fields_diff.removed:
        schema_changes.append(
            BreakingChange(
                BreakingChangeType.FIELD_REMOVED,
                f"{old_type.name}.{field_name} was removed.",
            )
        )

    for field_name, (old_field, new_field) in fields_diff.persisted.items():
        schema_changes.extend(
            find_arg_changes(old_type, field_name, old_field, new_field)
        )
        is_safe = is_change_safe_for_object_or_interface_field(
            old_field.type, new_field.type
        )
        if not is_safe:
            schema_changes.append(
                BreakingChange(
                    BreakingChangeType.FIELD_CHANGED_KIND,
                    f"{old_type.name}.{field_name} changed type"
                    f" from {old_field.type} to {new_field.type}.",
                )
            )

    return schema_changes


def find_arg_changes(
    old_type: Union[GraphQLObjectType, GraphQLInterfaceType],
    field_name: str,
    old_field: GraphQLField,
    new_field: GraphQLField,
) -> List[Change]:
    schema_changes: List[Change] = []
    args_diff = dict_diff(old_field.args, new_field.args)

    for arg_name in args_diff.removed:
        schema_changes.append(
            BreakingChange(
                BreakingChangeType.ARG_REMOVED,
                f"{old_type.name}.{field_name} arg" f" {arg_name} was removed.",
            )
        )

    for arg_name, (old_arg, new_arg) in args_diff.persisted.items():
        is_safe = is_change_safe_for_input_object_field_or_field_arg(
            old_arg.type, new_arg.type
        )
        if not is_safe:
            schema_changes.append(
                BreakingChange(
                    BreakingChangeType.ARG_CHANGED_KIND,
                    f"{old_type.name}.{field_name} arg"
                    f" {arg_name} has changed type from"
                    f" {old_arg.type} to {new_arg.type}.",
                )
            )
        elif old_arg.default_value is not Undefined:
            if new_arg.default_value is Undefined:
                schema_changes.append(
                    DangerousChange(
                        DangerousChangeType.ARG_DEFAULT_VALUE_CHANGE,
                        f"{old_type.name}.{field_name} arg"
                        f" {arg_name} defaultValue was removed.",
                    )
                )
            else:
                # Since we are looking only for client's observable changes we should
                # compare default values in the same representation as they are
                # represented inside introspection.
                old_value_str = stringify_value(old_arg.default_value, old_arg.type)
                new_value_str = stringify_value(new_arg.default_value, new_arg.type)

                if old_value_str != new_value_str:
                    schema_changes.append(
                        DangerousChange(
                            DangerousChangeType.ARG_DEFAULT_VALUE_CHANGE,
                            f"{old_type.name}.{field_name} arg"
                            f" {arg_name} has changed defaultValue"
                            f" from {old_value_str} to {new_value_str}.",
                        )
                    )

    for arg_name, new_arg in args_diff.added.items():
        if is_required_argument(new_arg):
            schema_changes.append(
                BreakingChange(
                    BreakingChangeType.REQUIRED_ARG_ADDED,
                    f"A required arg {arg_name} on"
                    f" {old_type.name}.{field_name} was added.",
                )
            )
        else:
            schema_changes.append(
                DangerousChange(
                    DangerousChangeType.OPTIONAL_ARG_ADDED,
                    f"An optional arg {arg_name} on"
                    f" {old_type.name}.{field_name} was added.",
                )
            )

    return schema_changes


def is_change_safe_for_object_or_interface_field(
    old_type: GraphQLType, new_type: GraphQLType
) -> bool:
    if is_list_type(old_type):
        return (
            # if they're both lists, make sure underlying types are compatible
            is_list_type(new_type)
            and is_change_safe_for_object_or_interface_field(
                cast(GraphQLList, old_type).of_type, cast(GraphQLList, new_type).of_type
            )
        ) or (
            # moving from nullable to non-null of same underlying type is safe
            is_non_null_type(new_type)
            and is_change_safe_for_object_or_interface_field(
                old_type, cast(GraphQLNonNull, new_type).of_type
            )
        )

    if is_non_null_type(old_type):
        # if they're both non-null, make sure underlying types are compatible
        return is_non_null_type(
            new_type
        ) and is_change_safe_for_object_or_interface_field(
            cast(GraphQLNonNull, old_type).of_type,
            cast(GraphQLNonNull, new_type).of_type,
        )

    return (
        # if they're both named types, see if their names are equivalent
        is_named_type(new_type)
        and cast(GraphQLNamedType, old_type).name
        == cast(GraphQLNamedType, new_type).name
    ) or (
        # moving from nullable to non-null of same underlying type is safe
        is_non_null_type(new_type)
        and is_change_safe_for_object_or_interface_field(
            old_type, cast(GraphQLNonNull, new_type).of_type
        )
    )


def is_change_safe_for_input_object_field_or_field_arg(
    old_type: GraphQLType, new_type: GraphQLType
) -> bool:
    if is_list_type(old_type):

        return is_list_type(
            # if they're both lists, make sure underlying types are compatible
            new_type
        ) and is_change_safe_for_input_object_field_or_field_arg(
            cast(GraphQLList, old_type).of_type, cast(GraphQLList, new_type).of_type
        )

    if is_non_null_type(old_type):
        return (
            # if they're both non-null, make sure the underlying types are compatible
            is_non_null_type(new_type)
            and is_change_safe_for_input_object_field_or_field_arg(
                cast(GraphQLNonNull, old_type).of_type,
                cast(GraphQLNonNull, new_type).of_type,
            )
        ) or (
            # moving from non-null to nullable of same underlying type is safe
            not is_non_null_type(new_type)
            and is_change_safe_for_input_object_field_or_field_arg(
                cast(GraphQLNonNull, old_type).of_type, new_type
            )
        )

    return (
        # if they're both named types, see if their names are equivalent
        is_named_type(new_type)
        and cast(GraphQLNamedType, old_type).name
        == cast(GraphQLNamedType, new_type).name
    )


def type_kind_name(type_: GraphQLNamedType) -> str:
    if is_scalar_type(type_):
        return "a Scalar type"
    if is_object_type(type_):
        return "an Object type"
    if is_interface_type(type_):
        return "an Interface type"
    if is_union_type(type_):
        return "a Union type"
    if is_enum_type(type_):
        return "an Enum type"
    if is_input_object_type(type_):
        return "an Input type"

    # Not reachable. All possible output types have been considered.
    raise TypeError(f"Unexpected type {inspect(type)}")


def stringify_value(value: Any, type_: GraphQLInputType) -> str:
    ast = ast_from_value(value, type_)
    if ast is None:  # pragma: no cover
        raise TypeError(f"Invalid value: {inspect(value)}")
    return print_ast(sort_value_node(ast))


class ListDiff(NamedTuple):
    """Tuple with added, removed and persisted list items."""

    added: List
    removed: List
    persisted: List


def list_diff(old_list: Collection, new_list: Collection) -> ListDiff:
    """Get differences between two lists of named items."""
    added = []
    persisted = []
    removed = []

    old_set = {item.name for item in old_list}
    new_map = {item.name: item for item in new_list}

    for old_item in old_list:
        new_item = new_map.get(old_item.name)
        if new_item:
            persisted.append([old_item, new_item])
        else:
            removed.append(old_item)

    for new_item in new_list:
        if new_item.name not in old_set:
            added.append(new_item)

    return ListDiff(added, removed, persisted)


class DictDiff(NamedTuple):
    """Tuple with added, removed and persisted dict entries."""

    added: Dict
    removed: Dict
    persisted: Dict


def dict_diff(old_dict: Dict, new_dict: Dict) -> DictDiff:
    """Get differences between two dicts."""
    added = {}
    removed = {}
    persisted = {}

    for old_name, old_item in old_dict.items():
        new_item = new_dict.get(old_name)
        if new_item:
            persisted[old_name] = [old_item, new_item]
        else:
            removed[old_name] = old_item

    for new_name, new_item in new_dict.items():
        if new_name not in old_dict:
            added[new_name] = new_item

    return DictDiff(added, removed, persisted)
