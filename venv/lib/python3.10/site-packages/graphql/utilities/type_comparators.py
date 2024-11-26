from typing import cast

from ..type import (
    GraphQLAbstractType,
    GraphQLCompositeType,
    GraphQLList,
    GraphQLNonNull,
    GraphQLObjectType,
    GraphQLSchema,
    GraphQLType,
    is_abstract_type,
    is_interface_type,
    is_list_type,
    is_non_null_type,
    is_object_type,
)

__all__ = ["is_equal_type", "is_type_sub_type_of", "do_types_overlap"]


def is_equal_type(type_a: GraphQLType, type_b: GraphQLType) -> bool:
    """Check whether two types are equal.

    Provided two types, return true if the types are equal (invariant)."""
    # Equivalent types are equal.
    if type_a is type_b:
        return True

    # If either type is non-null, the other must also be non-null.
    if is_non_null_type(type_a) and is_non_null_type(type_b):
        # noinspection PyUnresolvedReferences
        return is_equal_type(type_a.of_type, type_b.of_type)  # type:ignore

    # If either type is a list, the other must also be a list.
    if is_list_type(type_a) and is_list_type(type_b):
        # noinspection PyUnresolvedReferences
        return is_equal_type(type_a.of_type, type_b.of_type)  # type:ignore

    # Otherwise the types are not equal.
    return False


def is_type_sub_type_of(
    schema: GraphQLSchema, maybe_subtype: GraphQLType, super_type: GraphQLType
) -> bool:
    """Check whether a type is subtype of another type in a given schema.

    Provided a type and a super type, return true if the first type is either equal or
    a subset of the second super type (covariant).
    """
    # Equivalent type is a valid subtype
    if maybe_subtype is super_type:
        return True

    # If super_type is non-null, maybe_subtype must also be non-null.
    if is_non_null_type(super_type):
        if is_non_null_type(maybe_subtype):
            return is_type_sub_type_of(
                schema,
                cast(GraphQLNonNull, maybe_subtype).of_type,
                cast(GraphQLNonNull, super_type).of_type,
            )
        return False
    elif is_non_null_type(maybe_subtype):
        # If super_type is nullable, maybe_subtype may be non-null or nullable.
        return is_type_sub_type_of(
            schema, cast(GraphQLNonNull, maybe_subtype).of_type, super_type
        )

    # If super_type type is a list, maybeSubType type must also be a list.
    if is_list_type(super_type):
        if is_list_type(maybe_subtype):
            return is_type_sub_type_of(
                schema,
                cast(GraphQLList, maybe_subtype).of_type,
                cast(GraphQLList, super_type).of_type,
            )
        return False
    elif is_list_type(maybe_subtype):
        # If super_type is not a list, maybe_subtype must also be not a list.
        return False

    # If super_type type is abstract, check if it is super type of maybe_subtype.
    # Otherwise, the child type is not a valid subtype of the parent type.
    return (
        is_abstract_type(super_type)
        and (is_interface_type(maybe_subtype) or is_object_type(maybe_subtype))
        and schema.is_sub_type(
            cast(GraphQLAbstractType, super_type),
            cast(GraphQLObjectType, maybe_subtype),
        )
    )


def do_types_overlap(
    schema: GraphQLSchema, type_a: GraphQLCompositeType, type_b: GraphQLCompositeType
) -> bool:
    """Check whether two types overlap in a given schema.

    Provided two composite types, determine if they "overlap". Two composite types
    overlap when the Sets of possible concrete types for each intersect.

    This is often used to determine if a fragment of a given type could possibly be
    visited in a context of another type.

    This function is commutative.
    """
    # Equivalent types overlap
    if type_a is type_b:
        return True

    if is_abstract_type(type_a):
        type_a = cast(GraphQLAbstractType, type_a)
        if is_abstract_type(type_b):
            # If both types are abstract, then determine if there is any intersection
            # between possible concrete types of each.
            type_b = cast(GraphQLAbstractType, type_b)
            return any(
                schema.is_sub_type(type_b, type_)
                for type_ in schema.get_possible_types(type_a)
            )
        # Determine if latter type is a possible concrete type of the former.
        return schema.is_sub_type(type_a, type_b)

    if is_abstract_type(type_b):
        # Determine if former type is a possible concrete type of the latter.
        type_b = cast(GraphQLAbstractType, type_b)
        return schema.is_sub_type(type_b, type_a)

    # Otherwise the types do not overlap.
    return False
