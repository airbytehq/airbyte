from itertools import chain
from typing import Any, Dict, List, Optional, Tuple, Union, cast

from ...error import GraphQLError
from ...language import (
    FieldNode,
    FragmentDefinitionNode,
    FragmentSpreadNode,
    InlineFragmentNode,
    ObjectFieldNode,
    ObjectValueNode,
    SelectionSetNode,
    print_ast,
)
from ...type import (
    GraphQLCompositeType,
    GraphQLField,
    GraphQLList,
    GraphQLNamedType,
    GraphQLNonNull,
    GraphQLOutputType,
    get_named_type,
    is_interface_type,
    is_leaf_type,
    is_list_type,
    is_non_null_type,
    is_object_type,
)
from ...utilities import type_from_ast
from ...utilities.sort_value_node import sort_value_node
from . import ValidationContext, ValidationRule

MYPY = False

__all__ = ["OverlappingFieldsCanBeMergedRule"]


def reason_message(reason: "ConflictReasonMessage") -> str:
    if isinstance(reason, list):
        return " and ".join(
            f"subfields '{response_name}' conflict"
            f" because {reason_message(sub_reason)}"
            for response_name, sub_reason in reason
        )
    return reason


class OverlappingFieldsCanBeMergedRule(ValidationRule):
    """Overlapping fields can be merged

    A selection set is only valid if all fields (including spreading any fragments)
    either correspond to distinct response names or can be merged without ambiguity.

    See https://spec.graphql.org/draft/#sec-Field-Selection-Merging
    """

    def __init__(self, context: ValidationContext):
        super().__init__(context)
        # A memoization for when two fragments are compared "between" each other for
        # conflicts. Two fragments may be compared many times, so memoizing this can
        # dramatically improve the performance of this validator.
        self.compared_fragment_pairs = PairSet()

        # A cache for the "field map" and list of fragment names found in any given
        # selection set. Selection sets may be asked for this information multiple
        # times, so this improves the performance of this validator.
        self.cached_fields_and_fragment_names: Dict = {}

    def enter_selection_set(self, selection_set: SelectionSetNode, *_args: Any) -> None:
        conflicts = find_conflicts_within_selection_set(
            self.context,
            self.cached_fields_and_fragment_names,
            self.compared_fragment_pairs,
            self.context.get_parent_type(),
            selection_set,
        )
        for (reason_name, reason), fields1, fields2 in conflicts:
            reason_msg = reason_message(reason)
            self.report_error(
                GraphQLError(
                    f"Fields '{reason_name}' conflict because {reason_msg}."
                    " Use different aliases on the fields to fetch both"
                    " if this was intentional.",
                    fields1 + fields2,
                )
            )


Conflict = Tuple["ConflictReason", List[FieldNode], List[FieldNode]]
# Field name and reason.
ConflictReason = Tuple[str, "ConflictReasonMessage"]
# Reason is a string, or a nested list of conflicts.
if MYPY:  # recursive types not fully supported yet (/python/mypy/issues/731)
    ConflictReasonMessage = Union[str, List]
else:
    ConflictReasonMessage = Union[str, List[ConflictReason]]
# Tuple defining a field node in a context.
NodeAndDef = Tuple[GraphQLCompositeType, FieldNode, Optional[GraphQLField]]
# Dictionary of lists of those.
NodeAndDefCollection = Dict[str, List[NodeAndDef]]


# Algorithm:
#
# Conflicts occur when two fields exist in a query which will produce the same
# response name, but represent differing values, thus creating a conflict.
# The algorithm below finds all conflicts via making a series of comparisons
# between fields. In order to compare as few fields as possible, this makes
# a series of comparisons "within" sets of fields and "between" sets of fields.
#
# Given any selection set, a collection produces both a set of fields by
# also including all inline fragments, as well as a list of fragments
# referenced by fragment spreads.
#
# A) Each selection set represented in the document first compares "within" its
# collected set of fields, finding any conflicts between every pair of
# overlapping fields.
# Note: This is the#only time* that a the fields "within" a set are compared
# to each other. After this only fields "between" sets are compared.
#
# B) Also, if any fragment is referenced in a selection set, then a
# comparison is made "between" the original set of fields and the
# referenced fragment.
#
# C) Also, if multiple fragments are referenced, then comparisons
# are made "between" each referenced fragment.
#
# D) When comparing "between" a set of fields and a referenced fragment, first
# a comparison is made between each field in the original set of fields and
# each field in the the referenced set of fields.
#
# E) Also, if any fragment is referenced in the referenced selection set,
# then a comparison is made "between" the original set of fields and the
# referenced fragment (recursively referring to step D).
#
# F) When comparing "between" two fragments, first a comparison is made between
# each field in the first referenced set of fields and each field in the the
# second referenced set of fields.
#
# G) Also, any fragments referenced by the first must be compared to the
# second, and any fragments referenced by the second must be compared to the
# first (recursively referring to step F).
#
# H) When comparing two fields, if both have selection sets, then a comparison
# is made "between" both selection sets, first comparing the set of fields in
# the first selection set with the set of fields in the second.
#
# I) Also, if any fragment is referenced in either selection set, then a
# comparison is made "between" the other set of fields and the
# referenced fragment.
#
# J) Also, if two fragments are referenced in both selection sets, then a
# comparison is made "between" the two fragments.


def find_conflicts_within_selection_set(
    context: ValidationContext,
    cached_fields_and_fragment_names: Dict,
    compared_fragment_pairs: "PairSet",
    parent_type: Optional[GraphQLNamedType],
    selection_set: SelectionSetNode,
) -> List[Conflict]:
    """Find conflicts within selection set.

    Find all conflicts found "within" a selection set, including those found via
    spreading in fragments.

    Called when visiting each SelectionSet in the GraphQL Document.
    """
    conflicts: List[Conflict] = []

    field_map, fragment_names = get_fields_and_fragment_names(
        context, cached_fields_and_fragment_names, parent_type, selection_set
    )

    # (A) Find all conflicts "within" the fields of this selection set.
    # Note: this is the *only place* `collect_conflicts_within` is called.
    collect_conflicts_within(
        context,
        conflicts,
        cached_fields_and_fragment_names,
        compared_fragment_pairs,
        field_map,
    )

    if fragment_names:
        # (B) Then collect conflicts between these fields and those represented by each
        # spread fragment name found.
        for i, fragment_name in enumerate(fragment_names):
            collect_conflicts_between_fields_and_fragment(
                context,
                conflicts,
                cached_fields_and_fragment_names,
                compared_fragment_pairs,
                False,
                field_map,
                fragment_name,
            )
            # (C) Then compare this fragment with all other fragments found in this
            # selection set to collect conflicts within fragments spread together.
            # This compares each item in the list of fragment names to every other
            # item in that same list (except for itself).
            for other_fragment_name in fragment_names[i + 1 :]:
                collect_conflicts_between_fragments(
                    context,
                    conflicts,
                    cached_fields_and_fragment_names,
                    compared_fragment_pairs,
                    False,
                    fragment_name,
                    other_fragment_name,
                )

    return conflicts


def collect_conflicts_between_fields_and_fragment(
    context: ValidationContext,
    conflicts: List[Conflict],
    cached_fields_and_fragment_names: Dict,
    compared_fragment_pairs: "PairSet",
    are_mutually_exclusive: bool,
    field_map: NodeAndDefCollection,
    fragment_name: str,
) -> None:
    """Collect conflicts between fields and fragment.

    Collect all conflicts found between a set of fields and a fragment reference
    including via spreading in any nested fragments.
    """
    fragment = context.get_fragment(fragment_name)
    if not fragment:
        return None

    field_map2, referenced_fragment_names = get_referenced_fields_and_fragment_names(
        context, cached_fields_and_fragment_names, fragment
    )

    # Do not compare a fragment's fieldMap to itself.
    if field_map is field_map2:
        return

    # (D) First collect any conflicts between the provided collection of fields and the
    # collection of fields represented by the given fragment.
    collect_conflicts_between(
        context,
        conflicts,
        cached_fields_and_fragment_names,
        compared_fragment_pairs,
        are_mutually_exclusive,
        field_map,
        field_map2,
    )

    # (E) Then collect any conflicts between the provided collection of fields and any
    # fragment names found in the given fragment.
    for referenced_fragment_name in referenced_fragment_names:
        # Memoize so two fragments are not compared for conflicts more than once.
        if compared_fragment_pairs.has(
            referenced_fragment_name, fragment_name, are_mutually_exclusive
        ):
            continue
        compared_fragment_pairs.add(
            referenced_fragment_name, fragment_name, are_mutually_exclusive
        )

        collect_conflicts_between_fields_and_fragment(
            context,
            conflicts,
            cached_fields_and_fragment_names,
            compared_fragment_pairs,
            are_mutually_exclusive,
            field_map,
            referenced_fragment_name,
        )


def collect_conflicts_between_fragments(
    context: ValidationContext,
    conflicts: List[Conflict],
    cached_fields_and_fragment_names: Dict,
    compared_fragment_pairs: "PairSet",
    are_mutually_exclusive: bool,
    fragment_name1: str,
    fragment_name2: str,
) -> None:
    """Collect conflicts between fragments.

    Collect all conflicts found between two fragments, including via spreading in any
    nested fragments.
    """
    # No need to compare a fragment to itself.
    if fragment_name1 == fragment_name2:
        return

    # Memoize so two fragments are not compared for conflicts more than once.
    if compared_fragment_pairs.has(
        fragment_name1, fragment_name2, are_mutually_exclusive
    ):
        return
    compared_fragment_pairs.add(fragment_name1, fragment_name2, are_mutually_exclusive)

    fragment1 = context.get_fragment(fragment_name1)
    fragment2 = context.get_fragment(fragment_name2)
    if not fragment1 or not fragment2:
        return None

    field_map1, referenced_fragment_names1 = get_referenced_fields_and_fragment_names(
        context, cached_fields_and_fragment_names, fragment1
    )

    field_map2, referenced_fragment_names2 = get_referenced_fields_and_fragment_names(
        context, cached_fields_and_fragment_names, fragment2
    )

    # (F) First, collect all conflicts between these two collections of fields
    # (not including any nested fragments)
    collect_conflicts_between(
        context,
        conflicts,
        cached_fields_and_fragment_names,
        compared_fragment_pairs,
        are_mutually_exclusive,
        field_map1,
        field_map2,
    )

    # (G) Then collect conflicts between the first fragment and any nested fragments
    # spread in the second fragment.
    for referenced_fragment_name2 in referenced_fragment_names2:
        collect_conflicts_between_fragments(
            context,
            conflicts,
            cached_fields_and_fragment_names,
            compared_fragment_pairs,
            are_mutually_exclusive,
            fragment_name1,
            referenced_fragment_name2,
        )

    # (G) Then collect conflicts between the second fragment and any nested fragments
    # spread in the first fragment.
    for referenced_fragment_name1 in referenced_fragment_names1:
        collect_conflicts_between_fragments(
            context,
            conflicts,
            cached_fields_and_fragment_names,
            compared_fragment_pairs,
            are_mutually_exclusive,
            referenced_fragment_name1,
            fragment_name2,
        )


def find_conflicts_between_sub_selection_sets(
    context: ValidationContext,
    cached_fields_and_fragment_names: Dict,
    compared_fragment_pairs: "PairSet",
    are_mutually_exclusive: bool,
    parent_type1: Optional[GraphQLNamedType],
    selection_set1: SelectionSetNode,
    parent_type2: Optional[GraphQLNamedType],
    selection_set2: SelectionSetNode,
) -> List[Conflict]:
    """Find conflicts between sub selection sets.

    Find all conflicts found between two selection sets, including those found via
    spreading in fragments. Called when determining if conflicts exist between the
    sub-fields of two overlapping fields.
    """
    conflicts: List[Conflict] = []

    field_map1, fragment_names1 = get_fields_and_fragment_names(
        context, cached_fields_and_fragment_names, parent_type1, selection_set1
    )
    field_map2, fragment_names2 = get_fields_and_fragment_names(
        context, cached_fields_and_fragment_names, parent_type2, selection_set2
    )

    # (H) First, collect all conflicts between these two collections of field.
    collect_conflicts_between(
        context,
        conflicts,
        cached_fields_and_fragment_names,
        compared_fragment_pairs,
        are_mutually_exclusive,
        field_map1,
        field_map2,
    )

    # (I) Then collect conflicts between the first collection of fields and those
    # referenced by each fragment name associated with the second.
    if fragment_names2:
        for fragment_name2 in fragment_names2:
            collect_conflicts_between_fields_and_fragment(
                context,
                conflicts,
                cached_fields_and_fragment_names,
                compared_fragment_pairs,
                are_mutually_exclusive,
                field_map1,
                fragment_name2,
            )

    # (I) Then collect conflicts between the second collection of fields and those
    # referenced by each fragment name associated with the first.
    if fragment_names1:
        for fragment_name1 in fragment_names1:
            collect_conflicts_between_fields_and_fragment(
                context,
                conflicts,
                cached_fields_and_fragment_names,
                compared_fragment_pairs,
                are_mutually_exclusive,
                field_map2,
                fragment_name1,
            )

    # (J) Also collect conflicts between any fragment names by the first and fragment
    # names by the second. This compares each item in the first set of names to each
    # item in the second set of names.
    for fragment_name1 in fragment_names1:
        for fragment_name2 in fragment_names2:
            collect_conflicts_between_fragments(
                context,
                conflicts,
                cached_fields_and_fragment_names,
                compared_fragment_pairs,
                are_mutually_exclusive,
                fragment_name1,
                fragment_name2,
            )

    return conflicts


def collect_conflicts_within(
    context: ValidationContext,
    conflicts: List[Conflict],
    cached_fields_and_fragment_names: Dict,
    compared_fragment_pairs: "PairSet",
    field_map: NodeAndDefCollection,
) -> None:
    """Collect all Conflicts "within" one collection of fields."""
    # A field map is a keyed collection, where each key represents a response name and
    # the value at that key is a list of all fields which provide that response name.
    # For every response name, if there are multiple fields, they must be compared to
    # find a potential conflict.
    for response_name, fields in field_map.items():
        # This compares every field in the list to every other field in this list
        # (except to itself). If the list only has one item, nothing needs to be
        # compared.
        if len(fields) > 1:
            for i, field in enumerate(fields):
                for other_field in fields[i + 1 :]:
                    conflict = find_conflict(
                        context,
                        cached_fields_and_fragment_names,
                        compared_fragment_pairs,
                        # within one collection is never mutually exclusive
                        False,
                        response_name,
                        field,
                        other_field,
                    )
                    if conflict:
                        conflicts.append(conflict)


def collect_conflicts_between(
    context: ValidationContext,
    conflicts: List[Conflict],
    cached_fields_and_fragment_names: Dict,
    compared_fragment_pairs: "PairSet",
    parent_fields_are_mutually_exclusive: bool,
    field_map1: NodeAndDefCollection,
    field_map2: NodeAndDefCollection,
) -> None:
    """Collect all Conflicts between two collections of fields.

    This is similar to, but different from the :func:`~.collect_conflicts_within`
    function above. This check assumes that :func:`~.collect_conflicts_within` has
    already been called on each provided collection of fields. This is true because
    this validator traverses each individual selection set.
    """
    # A field map is a keyed collection, where each key represents a response name and
    # the value at that key is a list of all fields which provide that response name.
    # For any response name which appears in both provided field maps, each field from
    # the first field map must be compared to every field in the second field map to
    # find potential conflicts.
    for response_name, fields1 in field_map1.items():
        fields2 = field_map2.get(response_name)
        if fields2:
            for field1 in fields1:
                for field2 in fields2:
                    conflict = find_conflict(
                        context,
                        cached_fields_and_fragment_names,
                        compared_fragment_pairs,
                        parent_fields_are_mutually_exclusive,
                        response_name,
                        field1,
                        field2,
                    )
                    if conflict:
                        conflicts.append(conflict)


def find_conflict(
    context: ValidationContext,
    cached_fields_and_fragment_names: Dict,
    compared_fragment_pairs: "PairSet",
    parent_fields_are_mutually_exclusive: bool,
    response_name: str,
    field1: NodeAndDef,
    field2: NodeAndDef,
) -> Optional[Conflict]:
    """Find conflict.

    Determines if there is a conflict between two particular fields, including comparing
    their sub-fields.
    """
    parent_type1, node1, def1 = field1
    parent_type2, node2, def2 = field2

    # If it is known that two fields could not possibly apply at the same time, due to
    # the parent types, then it is safe to permit them to diverge in aliased field or
    # arguments used as they will not present any ambiguity by differing. It is known
    # that two parent types could never overlap if they are different Object types.
    # Interface or Union types might overlap - if not in the current state of the
    # schema, then perhaps in some future version, thus may not safely diverge.
    are_mutually_exclusive = parent_fields_are_mutually_exclusive or (
        parent_type1 != parent_type2
        and is_object_type(parent_type1)
        and is_object_type(parent_type2)
    )

    # The return type for each field.
    type1 = cast(Optional[GraphQLOutputType], def1 and def1.type)
    type2 = cast(Optional[GraphQLOutputType], def2 and def2.type)

    if not are_mutually_exclusive:
        # Two aliases must refer to the same field.
        name1 = node1.name.value
        name2 = node2.name.value
        if name1 != name2:
            return (
                (response_name, f"'{name1}' and '{name2}' are different fields"),
                [node1],
                [node2],
            )

        # Two field calls must have the same arguments.
        if stringify_arguments(node1) != stringify_arguments(node2):
            return (response_name, "they have differing arguments"), [node1], [node2]

    if type1 and type2 and do_types_conflict(type1, type2):
        return (
            (response_name, f"they return conflicting types '{type1}' and '{type2}'"),
            [node1],
            [node2],
        )

    # Collect and compare sub-fields. Use the same "visited fragment names" list for
    # both collections so fields in a fragment reference are never compared to
    # themselves.
    selection_set1 = node1.selection_set
    selection_set2 = node2.selection_set
    if selection_set1 and selection_set2:
        conflicts = find_conflicts_between_sub_selection_sets(
            context,
            cached_fields_and_fragment_names,
            compared_fragment_pairs,
            are_mutually_exclusive,
            get_named_type(type1),
            selection_set1,
            get_named_type(type2),
            selection_set2,
        )
        return subfield_conflicts(conflicts, response_name, node1, node2)

    return None  # no conflict


def stringify_arguments(field_node: FieldNode) -> str:
    input_object_with_args = ObjectValueNode(
        fields=tuple(
            ObjectFieldNode(name=arg_node.name, value=arg_node.value)
            for arg_node in field_node.arguments
        )
    )
    return print_ast(sort_value_node(input_object_with_args))


def do_types_conflict(type1: GraphQLOutputType, type2: GraphQLOutputType) -> bool:
    """Check whether two types conflict

    Two types conflict if both types could not apply to a value simultaneously.
    Composite types are ignored as their individual field types will be compared later
    recursively. However List and Non-Null types must match.
    """
    if is_list_type(type1):
        return (
            do_types_conflict(
                cast(GraphQLList, type1).of_type, cast(GraphQLList, type2).of_type
            )
            if is_list_type(type2)
            else True
        )
    if is_list_type(type2):
        return True
    if is_non_null_type(type1):
        return (
            do_types_conflict(
                cast(GraphQLNonNull, type1).of_type, cast(GraphQLNonNull, type2).of_type
            )
            if is_non_null_type(type2)
            else True
        )
    if is_non_null_type(type2):
        return True
    if is_leaf_type(type1) or is_leaf_type(type2):
        return type1 is not type2
    return False


def get_fields_and_fragment_names(
    context: ValidationContext,
    cached_fields_and_fragment_names: Dict,
    parent_type: Optional[GraphQLNamedType],
    selection_set: SelectionSetNode,
) -> Tuple[NodeAndDefCollection, List[str]]:
    """Get fields and referenced fragment names

    Given a selection set, return the collection of fields (a mapping of response name
    to field nodes and definitions) as well as a list of fragment names referenced via
    fragment spreads.
    """
    cached = cached_fields_and_fragment_names.get(selection_set)
    if not cached:
        node_and_defs: NodeAndDefCollection = {}
        fragment_names: Dict[str, bool] = {}
        collect_fields_and_fragment_names(
            context, parent_type, selection_set, node_and_defs, fragment_names
        )
        cached = (node_and_defs, list(fragment_names))
        cached_fields_and_fragment_names[selection_set] = cached
    return cached


def get_referenced_fields_and_fragment_names(
    context: ValidationContext,
    cached_fields_and_fragment_names: Dict,
    fragment: FragmentDefinitionNode,
) -> Tuple[NodeAndDefCollection, List[str]]:
    """Get referenced fields and nested fragment names

    Given a reference to a fragment, return the represented collection of fields as well
    as a list of nested fragment names referenced via fragment spreads.
    """
    # Short-circuit building a type from the node if possible.
    cached = cached_fields_and_fragment_names.get(fragment.selection_set)
    if cached:
        return cached

    fragment_type = type_from_ast(context.schema, fragment.type_condition)
    return get_fields_and_fragment_names(
        context, cached_fields_and_fragment_names, fragment_type, fragment.selection_set
    )


def collect_fields_and_fragment_names(
    context: ValidationContext,
    parent_type: Optional[GraphQLNamedType],
    selection_set: SelectionSetNode,
    node_and_defs: NodeAndDefCollection,
    fragment_names: Dict[str, bool],
) -> None:
    for selection in selection_set.selections:
        if isinstance(selection, FieldNode):
            field_name = selection.name.value
            field_def = (
                parent_type.fields.get(field_name)  # type: ignore
                if is_object_type(parent_type) or is_interface_type(parent_type)
                else None
            )
            response_name = selection.alias.value if selection.alias else field_name
            if not node_and_defs.get(response_name):
                node_and_defs[response_name] = []
            node_and_defs[response_name].append(
                cast(NodeAndDef, (parent_type, selection, field_def))
            )
        elif isinstance(selection, FragmentSpreadNode):
            fragment_names[selection.name.value] = True
        elif isinstance(selection, InlineFragmentNode):  # pragma: no cover else
            type_condition = selection.type_condition
            inline_fragment_type = (
                type_from_ast(context.schema, type_condition)
                if type_condition
                else parent_type
            )
            collect_fields_and_fragment_names(
                context,
                inline_fragment_type,
                selection.selection_set,
                node_and_defs,
                fragment_names,
            )


def subfield_conflicts(
    conflicts: List[Conflict], response_name: str, node1: FieldNode, node2: FieldNode
) -> Optional[Conflict]:
    """Check whether there are conflicts between sub-fields.

    Given a series of Conflicts which occurred between two sub-fields, generate a single
    Conflict.
    """
    if conflicts:
        return (
            (response_name, [conflict[0] for conflict in conflicts]),
            list(chain([node1], *[conflict[1] for conflict in conflicts])),
            list(chain([node2], *[conflict[2] for conflict in conflicts])),
        )
    return None  # no conflict


class PairSet:
    """Pair set

    A way to keep track of pairs of things when the ordering of the pair doesn't matter.
    """

    __slots__ = ("_data",)

    _data: Dict[str, Dict[str, bool]]

    def __init__(self) -> None:
        self._data = {}

    def has(self, a: str, b: str, are_mutually_exclusive: bool) -> bool:
        key1, key2 = (a, b) if a < b else (b, a)

        map_ = self._data.get(key1)
        if map_ is None:
            return False
        result = map_.get(key2)
        if result is None:
            return False

        # are_mutually_exclusive being False is a superset of being True,
        # hence if we want to know if this PairSet "has" these two with no exclusivity,
        # we have to ensure it was added as such.
        return True if are_mutually_exclusive else are_mutually_exclusive == result

    def add(self, a: str, b: str, are_mutually_exclusive: bool) -> None:
        key1, key2 = (a, b) if a < b else (b, a)

        map_ = self._data.get(key1)
        if map_ is None:
            self._data[key1] = {key2: are_mutually_exclusive}
        else:
            map_[key2] = are_mutually_exclusive
