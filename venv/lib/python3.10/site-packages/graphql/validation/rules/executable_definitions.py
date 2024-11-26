from typing import Any, Union, cast

from ...error import GraphQLError
from ...language import (
    DirectiveDefinitionNode,
    DocumentNode,
    ExecutableDefinitionNode,
    SchemaDefinitionNode,
    SchemaExtensionNode,
    TypeDefinitionNode,
    VisitorAction,
    SKIP,
)
from . import ASTValidationRule

__all__ = ["ExecutableDefinitionsRule"]


class ExecutableDefinitionsRule(ASTValidationRule):
    """Executable definitions

    A GraphQL document is only valid for execution if all definitions are either
    operation or fragment definitions.

    See https://spec.graphql.org/draft/#sec-Executable-Definitions
    """

    def enter_document(self, node: DocumentNode, *_args: Any) -> VisitorAction:
        for definition in node.definitions:
            if not isinstance(definition, ExecutableDefinitionNode):
                def_name = (
                    "schema"
                    if isinstance(
                        definition, (SchemaDefinitionNode, SchemaExtensionNode)
                    )
                    else "'{}'".format(
                        cast(
                            Union[DirectiveDefinitionNode, TypeDefinitionNode],
                            definition,
                        ).name.value
                    )
                )
                self.report_error(
                    GraphQLError(
                        f"The {def_name} definition is not executable.",
                        definition,
                    )
                )
        return SKIP
