from collections import defaultdict
from functools import cmp_to_key
from typing import Any, Dict, List, Union, cast

from ...type import (
    GraphQLAbstractType,
    GraphQLInterfaceType,
    GraphQLObjectType,
    GraphQLOutputType,
    GraphQLSchema,
    is_abstract_type,
    is_interface_type,
    is_object_type,
)
from ...error import GraphQLError
from ...language import FieldNode
from ...pyutils import did_you_mean, natural_comparison_key, suggestion_list
from . import ValidationRule

__all__ = ["FieldsOnCorrectTypeRule"]


class FieldsOnCorrectTypeRule(ValidationRule):
    """Fields on correct type

    A GraphQL document is only valid if all fields selected are defined by the parent
    type, or are an allowed meta field such as ``__typename``.

    See https://spec.graphql.org/draft/#sec-Field-Selections
    """

    def enter_field(self, node: FieldNode, *_args: Any) -> None:
        type_ = self.context.get_parent_type()
        if not type_:
            return
        field_def = self.context.get_field_def()
        if field_def:
            return
        # This field doesn't exist, lets look for suggestions.
        schema = self.context.schema
        field_name = node.name.value

        # First determine if there are any suggested types to condition on.
        suggestion = did_you_mean(
            get_suggested_type_names(schema, type_, field_name),
            "to use an inline fragment on",
        )

        # If there are no suggested types, then perhaps this was a typo?
        if not suggestion:
            suggestion = did_you_mean(get_suggested_field_names(type_, field_name))

        # Report an error, including helpful suggestions.
        self.report_error(
            GraphQLError(
                f"Cannot query field '{field_name}' on type '{type_}'." + suggestion,
                node,
            )
        )


def get_suggested_type_names(
    schema: GraphQLSchema, type_: GraphQLOutputType, field_name: str
) -> List[str]:
    """
    Get a list of suggested type names.

    Go through all of the implementations of type, as well as the interfaces
    that they implement. If any of those types include the provided field,
    suggest them, sorted by how often the type is referenced.
    """
    if not is_abstract_type(type_):
        # Must be an Object type, which does not have possible fields.
        return []

    type_ = cast(GraphQLAbstractType, type_)
    # Use a dict instead of a set for stable sorting when usage counts are the same
    suggested_types: Dict[Union[GraphQLObjectType, GraphQLInterfaceType], None] = {}
    usage_count: Dict[str, int] = defaultdict(int)
    for possible_type in schema.get_possible_types(type_):
        if field_name not in possible_type.fields:
            continue

        # This object type defines this field.
        suggested_types[possible_type] = None
        usage_count[possible_type.name] = 1

        for possible_interface in possible_type.interfaces:
            if field_name not in possible_interface.fields:
                continue

            # This interface type defines this field.
            suggested_types[possible_interface] = None
            usage_count[possible_interface.name] += 1

    def cmp(
        type_a: Union[GraphQLObjectType, GraphQLInterfaceType],
        type_b: Union[GraphQLObjectType, GraphQLInterfaceType],
    ) -> int:  # pragma: no cover
        # Suggest both interface and object types based on how common they are.
        usage_count_diff = usage_count[type_b.name] - usage_count[type_a.name]
        if usage_count_diff:
            return usage_count_diff

        # Suggest super types first followed by subtypes
        if is_interface_type(type_a) and schema.is_sub_type(
            cast(GraphQLInterfaceType, type_a), type_b
        ):
            return -1
        if is_interface_type(type_b) and schema.is_sub_type(
            cast(GraphQLInterfaceType, type_b), type_a
        ):
            return 1

        name_a = natural_comparison_key(type_a.name)
        name_b = natural_comparison_key(type_b.name)
        if name_a > name_b:
            return 1
        if name_a < name_b:
            return -1
        return 0

    return [type_.name for type_ in sorted(suggested_types, key=cmp_to_key(cmp))]


def get_suggested_field_names(type_: GraphQLOutputType, field_name: str) -> List[str]:
    """Get a list of suggested field names.

    For the field name provided, determine if there are any similar field names that may
    be the result of a typo.
    """
    if is_object_type(type_) or is_interface_type(type_):
        possible_field_names = list(type_.fields)  # type: ignore
        return suggestion_list(field_name, possible_field_names)
    # Otherwise, must be a Union type, which does not define fields.
    return []
