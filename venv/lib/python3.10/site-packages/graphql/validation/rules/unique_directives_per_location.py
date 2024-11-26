from collections import defaultdict
from typing import Any, Dict, List, Union, cast

from ...error import GraphQLError
from ...language import (
    DirectiveDefinitionNode,
    DirectiveNode,
    Node,
    SchemaDefinitionNode,
    SchemaExtensionNode,
    TypeDefinitionNode,
    TypeExtensionNode,
    is_type_definition_node,
    is_type_extension_node,
)
from ...type import specified_directives
from . import ASTValidationRule, SDLValidationContext, ValidationContext

__all__ = ["UniqueDirectivesPerLocationRule"]


class UniqueDirectivesPerLocationRule(ASTValidationRule):
    """Unique directive names per location

    A GraphQL document is only valid if all non-repeatable directives at a given
    location are uniquely named.

    See https://spec.graphql.org/draft/#sec-Directives-Are-Unique-Per-Location
    """

    context: Union[ValidationContext, SDLValidationContext]

    def __init__(self, context: Union[ValidationContext, SDLValidationContext]):
        super().__init__(context)
        unique_directive_map: Dict[str, bool] = {}

        schema = context.schema
        defined_directives = (
            schema.directives if schema else cast(List, specified_directives)
        )
        for directive in defined_directives:
            unique_directive_map[directive.name] = not directive.is_repeatable

        ast_definitions = context.document.definitions
        for def_ in ast_definitions:
            if isinstance(def_, DirectiveDefinitionNode):
                unique_directive_map[def_.name.value] = not def_.repeatable
        self.unique_directive_map = unique_directive_map

        self.schema_directives: Dict[str, DirectiveNode] = {}
        self.type_directives_map: Dict[str, Dict[str, DirectiveNode]] = defaultdict(
            dict
        )

    # Many different AST nodes may contain directives. Rather than listing them all,
    # just listen for entering any node, and check to see if it defines any directives.
    def enter(self, node: Node, *_args: Any) -> None:
        directives = getattr(node, "directives", None)
        if not directives:
            return
        directives = cast(List[DirectiveNode], directives)

        if isinstance(node, (SchemaDefinitionNode, SchemaExtensionNode)):
            seen_directives = self.schema_directives
        elif is_type_definition_node(node) or is_type_extension_node(node):
            node = cast(Union[TypeDefinitionNode, TypeExtensionNode], node)
            type_name = node.name.value
            seen_directives = self.type_directives_map[type_name]
        else:
            seen_directives = {}

        for directive in directives:
            directive_name = directive.name.value

            if self.unique_directive_map.get(directive_name):
                if directive_name in seen_directives:
                    self.report_error(
                        GraphQLError(
                            f"The directive '@{directive_name}'"
                            " can only be used once at this location.",
                            [seen_directives[directive_name], directive],
                        )
                    )
                else:
                    seen_directives[directive_name] = directive
