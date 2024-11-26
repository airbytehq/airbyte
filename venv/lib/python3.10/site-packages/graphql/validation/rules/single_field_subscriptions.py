from typing import Any, Dict, cast

from ...error import GraphQLError
from ...execution.collect_fields import collect_fields
from ...language import (
    FieldNode,
    FragmentDefinitionNode,
    OperationDefinitionNode,
    OperationType,
)
from . import ValidationRule

__all__ = ["SingleFieldSubscriptionsRule"]


class SingleFieldSubscriptionsRule(ValidationRule):
    """Subscriptions must only include a single non-introspection field.

    A GraphQL subscription is valid only if it contains a single root field and
    that root field is not an introspection field.

    See https://spec.graphql.org/draft/#sec-Single-root-field
    """

    def enter_operation_definition(
        self, node: OperationDefinitionNode, *_args: Any
    ) -> None:
        if node.operation != OperationType.SUBSCRIPTION:
            return
        schema = self.context.schema
        subscription_type = schema.subscription_type
        if subscription_type:
            operation_name = node.name.value if node.name else None
            variable_values: Dict[str, Any] = {}
            document = self.context.document
            fragments: Dict[str, FragmentDefinitionNode] = {
                definition.name.value: definition
                for definition in document.definitions
                if isinstance(definition, FragmentDefinitionNode)
            }
            fields = collect_fields(
                schema,
                fragments,
                variable_values,
                subscription_type,
                node.selection_set,
            )
            if len(fields) > 1:
                field_selection_lists = list(fields.values())
                extra_field_selection_lists = field_selection_lists[1:]
                extra_field_selection = [
                    field
                    for fields in extra_field_selection_lists
                    for field in (
                        fields
                        if isinstance(fields, list)
                        else [cast(FieldNode, fields)]
                    )
                ]
                self.report_error(
                    GraphQLError(
                        (
                            "Anonymous Subscription"
                            if operation_name is None
                            else f"Subscription '{operation_name}'"
                        )
                        + " must select only one top level field.",
                        extra_field_selection,
                    )
                )
            for field_nodes in fields.values():
                field = field_nodes[0]
                field_name = field.name.value
                if field_name.startswith("__"):
                    self.report_error(
                        GraphQLError(
                            (
                                "Anonymous Subscription"
                                if operation_name is None
                                else f"Subscription '{operation_name}'"
                            )
                            + " must not select an introspection top level field.",
                            field_nodes,
                        )
                    )
