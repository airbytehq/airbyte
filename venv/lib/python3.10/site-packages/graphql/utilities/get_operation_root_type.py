from typing import Union

from ..error import GraphQLError
from ..language import (
    OperationType,
    OperationDefinitionNode,
    OperationTypeDefinitionNode,
)
from ..type import GraphQLObjectType, GraphQLSchema

__all__ = ["get_operation_root_type"]


def get_operation_root_type(
    schema: GraphQLSchema,
    operation: Union[OperationDefinitionNode, OperationTypeDefinitionNode],
) -> GraphQLObjectType:
    """Extract the root type of the operation from the schema.

    .. deprecated:: 3.2
       Please use `GraphQLSchema.getRootType` instead. Will be removed in v3.3.
    """
    operation_type = operation.operation
    if operation_type == OperationType.QUERY:
        query_type = schema.query_type
        if not query_type:
            raise GraphQLError(
                "Schema does not define the required query root type.", operation
            )
        return query_type

    if operation_type == OperationType.MUTATION:
        mutation_type = schema.mutation_type
        if not mutation_type:
            raise GraphQLError("Schema is not configured for mutations.", operation)
        return mutation_type

    if operation_type == OperationType.SUBSCRIPTION:
        subscription_type = schema.subscription_type
        if not subscription_type:
            raise GraphQLError("Schema is not configured for subscriptions.", operation)
        return subscription_type

    raise GraphQLError(
        "Can only have query, mutation and subscription operations.", operation
    )
