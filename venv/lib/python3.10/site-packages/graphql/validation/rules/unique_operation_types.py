from typing import Any, Dict, Optional, Union

from ...error import GraphQLError
from ...language import (
    OperationTypeDefinitionNode,
    OperationType,
    SchemaDefinitionNode,
    SchemaExtensionNode,
    VisitorAction,
    SKIP,
)
from ...type import GraphQLObjectType
from . import SDLValidationContext, SDLValidationRule

__all__ = ["UniqueOperationTypesRule"]


class UniqueOperationTypesRule(SDLValidationRule):
    """Unique operation types

    A GraphQL document is only valid if it has only one type per operation.
    """

    def __init__(self, context: SDLValidationContext):
        super().__init__(context)
        schema = context.schema
        self.defined_operation_types: Dict[
            OperationType, OperationTypeDefinitionNode
        ] = {}
        self.existing_operation_types: Dict[
            OperationType, Optional[GraphQLObjectType]
        ] = (
            {
                OperationType.QUERY: schema.query_type,
                OperationType.MUTATION: schema.mutation_type,
                OperationType.SUBSCRIPTION: schema.subscription_type,
            }
            if schema
            else {}
        )
        self.schema = schema

    def check_operation_types(
        self, node: Union[SchemaDefinitionNode, SchemaExtensionNode], *_args: Any
    ) -> VisitorAction:
        for operation_type in node.operation_types or []:
            operation = operation_type.operation
            already_defined_operation_type = self.defined_operation_types.get(operation)

            if self.existing_operation_types.get(operation):
                self.report_error(
                    GraphQLError(
                        f"Type for {operation.value} already defined in the schema."
                        " It cannot be redefined.",
                        operation_type,
                    )
                )
            elif already_defined_operation_type:
                self.report_error(
                    GraphQLError(
                        f"There can be only one {operation.value} type in schema.",
                        [already_defined_operation_type, operation_type],
                    )
                )
            else:
                self.defined_operation_types[operation] = operation_type
        return SKIP

    enter_schema_definition = enter_schema_extension = check_operation_types
