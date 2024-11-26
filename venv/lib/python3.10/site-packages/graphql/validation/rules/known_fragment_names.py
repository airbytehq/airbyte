from typing import Any

from ...error import GraphQLError
from ...language import FragmentSpreadNode
from . import ValidationRule

__all__ = ["KnownFragmentNamesRule"]


class KnownFragmentNamesRule(ValidationRule):
    """Known fragment names

    A GraphQL document is only valid if all ``...Fragment`` fragment spreads refer to
    fragments defined in the same document.

    See https://spec.graphql.org/draft/#sec-Fragment-spread-target-defined
    """

    def enter_fragment_spread(self, node: FragmentSpreadNode, *_args: Any) -> None:
        fragment_name = node.name.value
        fragment = self.context.get_fragment(fragment_name)
        if not fragment:
            self.report_error(
                GraphQLError(f"Unknown fragment '{fragment_name}'.", node.name)
            )
