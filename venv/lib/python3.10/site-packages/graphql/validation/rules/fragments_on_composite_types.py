from typing import Any

from ...error import GraphQLError
from ...language import (
    FragmentDefinitionNode,
    InlineFragmentNode,
    print_ast,
)
from ...type import is_composite_type
from ...utilities import type_from_ast
from . import ValidationRule

__all__ = ["FragmentsOnCompositeTypesRule"]


class FragmentsOnCompositeTypesRule(ValidationRule):
    """Fragments on composite type

    Fragments use a type condition to determine if they apply, since fragments can only
    be spread into a composite type (object, interface, or union), the type condition
    must also be a composite type.

    See https://spec.graphql.org/draft/#sec-Fragments-On-Composite-Types
    """

    def enter_inline_fragment(self, node: InlineFragmentNode, *_args: Any) -> None:
        type_condition = node.type_condition
        if type_condition:
            type_ = type_from_ast(self.context.schema, type_condition)
            if type_ and not is_composite_type(type_):
                type_str = print_ast(type_condition)
                self.report_error(
                    GraphQLError(
                        "Fragment cannot condition"
                        f" on non composite type '{type_str}'.",
                        type_condition,
                    )
                )

    def enter_fragment_definition(
        self, node: FragmentDefinitionNode, *_args: Any
    ) -> None:
        type_condition = node.type_condition
        type_ = type_from_ast(self.context.schema, type_condition)
        if type_ and not is_composite_type(type_):
            type_str = print_ast(type_condition)
            self.report_error(
                GraphQLError(
                    f"Fragment '{node.name.value}' cannot condition"
                    f" on non composite type '{type_str}'.",
                    type_condition,
                )
            )
