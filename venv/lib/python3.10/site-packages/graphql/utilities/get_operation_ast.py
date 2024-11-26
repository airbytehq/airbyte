from typing import Optional

from ..language import DocumentNode, OperationDefinitionNode

__all__ = ["get_operation_ast"]


def get_operation_ast(
    document_ast: DocumentNode, operation_name: Optional[str] = None
) -> Optional[OperationDefinitionNode]:
    """Get operation AST node.

    Returns an operation AST given a document AST and optionally an operation
    name. If a name is not provided, an operation is only returned if only one
    is provided in the document.
    """
    operation = None
    for definition in document_ast.definitions:
        if isinstance(definition, OperationDefinitionNode):
            if operation_name is None:
                # If no operation name was provided, only return an Operation if there
                # is one defined in the document.
                # Upon encountering the second, return None.
                if operation:
                    return None
                operation = definition
            elif definition.name and definition.name.value == operation_name:
                return definition
    return operation
