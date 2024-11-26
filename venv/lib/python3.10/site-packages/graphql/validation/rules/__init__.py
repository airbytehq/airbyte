"""graphql.validation.rules package"""

from ...error import GraphQLError
from ...language.visitor import Visitor
from ..validation_context import (
    ASTValidationContext,
    SDLValidationContext,
    ValidationContext,
)

__all__ = ["ASTValidationRule", "SDLValidationRule", "ValidationRule"]


class ASTValidationRule(Visitor):
    """Visitor for validation of an AST."""

    context: ASTValidationContext

    def __init__(self, context: ASTValidationContext):
        super().__init__()
        self.context = context

    def report_error(self, error: GraphQLError) -> None:
        self.context.report_error(error)


class SDLValidationRule(ASTValidationRule):
    """Visitor for validation of an SDL AST."""

    context: SDLValidationContext

    def __init__(self, context: SDLValidationContext) -> None:
        super().__init__(context)


class ValidationRule(ASTValidationRule):
    """Visitor for validation using a GraphQL schema."""

    context: ValidationContext

    def __init__(self, context: ValidationContext) -> None:
        super().__init__(context)
