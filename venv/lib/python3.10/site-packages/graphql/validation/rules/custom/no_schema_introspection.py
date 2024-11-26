from typing import Any

from ....error import GraphQLError
from ....language import FieldNode
from ....type import get_named_type, is_introspection_type
from .. import ValidationRule

__all__ = ["NoSchemaIntrospectionCustomRule"]


class NoSchemaIntrospectionCustomRule(ValidationRule):
    """Prohibit introspection queries

    A GraphQL document is only valid if all fields selected are not fields that
    return an introspection type.

    Note: This rule is optional and is not part of the Validation section of the
    GraphQL Specification. This rule effectively disables introspection, which
    does not reflect best practices and should only be done if absolutely necessary.
    """

    def enter_field(self, node: FieldNode, *_args: Any) -> None:
        type_ = get_named_type(self.context.get_type())
        if type_ and is_introspection_type(type_):
            self.report_error(
                GraphQLError(
                    "GraphQL introspection has been disabled, but the requested query"
                    f" contained the field '{node.name.value}'.",
                    node,
                )
            )
