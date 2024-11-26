from typing import cast, Any, Optional

from ...error import GraphQLError
from ...language import FragmentSpreadNode, InlineFragmentNode
from ...type import GraphQLCompositeType, is_composite_type
from ...utilities import do_types_overlap, type_from_ast
from . import ValidationRule

__all__ = ["PossibleFragmentSpreadsRule"]


class PossibleFragmentSpreadsRule(ValidationRule):
    """Possible fragment spread

    A fragment spread is only valid if the type condition could ever possibly be true:
    if there is a non-empty intersection of the possible parent types, and possible
    types which pass the type condition.
    """

    def enter_inline_fragment(self, node: InlineFragmentNode, *_args: Any) -> None:
        context = self.context
        frag_type = context.get_type()
        parent_type = context.get_parent_type()
        if (
            is_composite_type(frag_type)
            and is_composite_type(parent_type)
            and not do_types_overlap(
                context.schema,
                cast(GraphQLCompositeType, frag_type),
                cast(GraphQLCompositeType, parent_type),
            )
        ):
            context.report_error(
                GraphQLError(
                    f"Fragment cannot be spread here as objects"
                    f" of type '{parent_type}' can never be of type '{frag_type}'.",
                    node,
                )
            )

    def enter_fragment_spread(self, node: FragmentSpreadNode, *_args: Any) -> None:
        context = self.context
        frag_name = node.name.value
        frag_type = self.get_fragment_type(frag_name)
        parent_type = context.get_parent_type()
        if (
            frag_type
            and parent_type
            and not do_types_overlap(context.schema, frag_type, parent_type)
        ):
            context.report_error(
                GraphQLError(
                    f"Fragment '{frag_name}' cannot be spread here as objects"
                    f" of type '{parent_type}' can never be of type '{frag_type}'.",
                    node,
                )
            )

    def get_fragment_type(self, name: str) -> Optional[GraphQLCompositeType]:
        context = self.context
        frag = context.get_fragment(name)
        if frag:
            type_ = type_from_ast(context.schema, frag.type_condition)
            if is_composite_type(type_):
                return cast(GraphQLCompositeType, type_)
        return None
