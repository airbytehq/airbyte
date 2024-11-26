from typing import Any, Dict, Optional

from graphql import (
    DocumentNode,
    GraphQLEnumType,
    GraphQLError,
    GraphQLInputObjectType,
    GraphQLList,
    GraphQLNonNull,
    GraphQLScalarType,
    GraphQLSchema,
    GraphQLType,
    GraphQLWrappingType,
    OperationDefinitionNode,
    type_from_ast,
)
from graphql.pyutils import inspect


def _get_document_operation(
    document: DocumentNode, operation_name: Optional[str] = None
) -> OperationDefinitionNode:
    """Returns the operation which should be executed in the document.

    Raises a GraphQLError if a single operation cannot be retrieved.
    """

    operation: Optional[OperationDefinitionNode] = None

    for definition in document.definitions:
        if isinstance(definition, OperationDefinitionNode):
            if operation_name is None:
                if operation:
                    raise GraphQLError(
                        "Must provide operation name"
                        " if query contains multiple operations."
                    )
                operation = definition
            elif definition.name and definition.name.value == operation_name:
                operation = definition

    if not operation:
        if operation_name is not None:
            raise GraphQLError(f"Unknown operation named '{operation_name}'.")

        # The following line should never happen normally as the document is
        # already verified before calling this function.
        raise GraphQLError("Must provide an operation.")  # pragma: no cover

    return operation


def serialize_value(type_: GraphQLType, value: Any) -> Any:
    """Given a GraphQL type and a Python value, return the serialized value.

    This method will serialize the value recursively, entering into
    lists and dicts.

    Can be used to serialize Enums and/or Custom Scalars in variable values.

    :param type_: the GraphQL type
    :param value: the provided value
    """

    if value is None:
        if isinstance(type_, GraphQLNonNull):
            # raise GraphQLError(f"Type {type_.of_type.name} Cannot be None.")
            raise GraphQLError(f"Type {inspect(type_)} Cannot be None.")
        else:
            return None

    if isinstance(type_, GraphQLWrappingType):
        inner_type = type_.of_type

        if isinstance(type_, GraphQLNonNull):
            return serialize_value(inner_type, value)

        elif isinstance(type_, GraphQLList):
            return [serialize_value(inner_type, v) for v in value]

    elif isinstance(type_, (GraphQLScalarType, GraphQLEnumType)):
        return type_.serialize(value)

    elif isinstance(type_, GraphQLInputObjectType):
        return {
            field_name: serialize_value(field.type, value[field_name])
            for field_name, field in type_.fields.items()
            if field_name in value
        }

    raise GraphQLError(f"Impossible to serialize value with type: {inspect(type_)}.")


def serialize_variable_values(
    schema: GraphQLSchema,
    document: DocumentNode,
    variable_values: Dict[str, Any],
    operation_name: Optional[str] = None,
) -> Dict[str, Any]:
    """Given a GraphQL document and a schema, serialize the Dictionary of
    variable values.

    Useful to serialize Enums and/or Custom Scalars in variable values.

    :param schema: the GraphQL schema
    :param document: the document representing the query sent to the backend
    :param variable_values: the dictionnary of variable values which needs
        to be serialized.
    :param operation_name: the optional operation_name for the query.
    """

    parsed_variable_values: Dict[str, Any] = {}

    # Find the operation in the document
    operation = _get_document_operation(document, operation_name=operation_name)

    # Serialize every variable value defined for the operation
    for var_def_node in operation.variable_definitions:
        var_name = var_def_node.variable.name.value
        var_type = type_from_ast(schema, var_def_node.type)

        if var_name in variable_values:

            assert var_type is not None

            var_value = variable_values[var_name]

            parsed_variable_values[var_name] = serialize_value(var_type, var_value)

    return parsed_variable_values
