from typing import Any

from ...error import GraphQLError
from ...language import DocumentNode, OperationDefinitionNode
from . import ASTValidationContext, ASTValidationRule

__all__ = ["LoneAnonymousOperationRule"]


class LoneAnonymousOperationRule(ASTValidationRule):
    """Lone anonymous operation

    A GraphQL document is only valid if when it contains an anonymous operation
    (the query short-hand) that it contains only that one operation definition.

    See https://spec.graphql.org/draft/#sec-Lone-Anonymous-Operation
    """

    def __init__(self, context: ASTValidationContext):
        super().__init__(context)
        self.operation_count = 0

    def enter_document(self, node: DocumentNode, *_args: Any) -> None:
        self.operation_count = sum(
            isinstance(definition, OperationDefinitionNode)
            for definition in node.definitions
        )

    def enter_operation_definition(
        self, node: OperationDefinitionNode, *_args: Any
    ) -> None:
        if not node.name and self.operation_count > 1:
            self.report_error(
                GraphQLError(
                    "This anonymous operation must be the only defined operation.", node
                )
            )
