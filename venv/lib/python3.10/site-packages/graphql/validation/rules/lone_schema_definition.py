from typing import Any

from ...error import GraphQLError
from ...language import SchemaDefinitionNode
from . import SDLValidationRule, SDLValidationContext

__all__ = ["LoneSchemaDefinitionRule"]


class LoneSchemaDefinitionRule(SDLValidationRule):
    """Lone Schema definition

    A GraphQL document is only valid if it contains only one schema definition.
    """

    def __init__(self, context: SDLValidationContext):
        super().__init__(context)
        old_schema = context.schema
        self.already_defined = old_schema and (
            old_schema.ast_node
            or old_schema.query_type
            or old_schema.mutation_type
            or old_schema.subscription_type
        )
        self.schema_definitions_count = 0

    def enter_schema_definition(self, node: SchemaDefinitionNode, *_args: Any) -> None:
        if self.already_defined:
            self.report_error(
                GraphQLError(
                    "Cannot define a new schema within a schema extension.", node
                )
            )
        else:
            if self.schema_definitions_count:
                self.report_error(
                    GraphQLError("Must provide only one schema definition.", node)
                )
            self.schema_definitions_count += 1
