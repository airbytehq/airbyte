from typing import cast, Any, Dict, List, Union

from ...error import GraphQLError
from ...language import (
    ArgumentNode,
    DirectiveDefinitionNode,
    DirectiveNode,
    SKIP,
    VisitorAction,
)
from ...pyutils import did_you_mean, suggestion_list
from ...type import specified_directives
from . import ASTValidationRule, SDLValidationContext, ValidationContext

__all__ = ["KnownArgumentNamesRule", "KnownArgumentNamesOnDirectivesRule"]


class KnownArgumentNamesOnDirectivesRule(ASTValidationRule):
    """Known argument names on directives

    A GraphQL directive is only valid if all supplied arguments are defined.

    For internal use only.
    """

    context: Union[ValidationContext, SDLValidationContext]

    def __init__(self, context: Union[ValidationContext, SDLValidationContext]):
        super().__init__(context)
        directive_args: Dict[str, List[str]] = {}

        schema = context.schema
        defined_directives = schema.directives if schema else specified_directives
        for directive in cast(List, defined_directives):
            directive_args[directive.name] = list(directive.args)

        ast_definitions = context.document.definitions
        for def_ in ast_definitions:
            if isinstance(def_, DirectiveDefinitionNode):
                directive_args[def_.name.value] = [
                    arg.name.value for arg in def_.arguments or []
                ]

        self.directive_args = directive_args

    def enter_directive(
        self, directive_node: DirectiveNode, *_args: Any
    ) -> VisitorAction:
        directive_name = directive_node.name.value
        known_args = self.directive_args.get(directive_name)
        if directive_node.arguments and known_args is not None:
            for arg_node in directive_node.arguments:
                arg_name = arg_node.name.value
                if arg_name not in known_args:
                    suggestions = suggestion_list(arg_name, known_args)
                    self.report_error(
                        GraphQLError(
                            f"Unknown argument '{arg_name}'"
                            f" on directive '@{directive_name}'."
                            + did_you_mean(suggestions),
                            arg_node,
                        )
                    )
        return SKIP


class KnownArgumentNamesRule(KnownArgumentNamesOnDirectivesRule):
    """Known argument names

    A GraphQL field is only valid if all supplied arguments are defined by that field.

    See https://spec.graphql.org/draft/#sec-Argument-Names
    See https://spec.graphql.org/draft/#sec-Directives-Are-In-Valid-Locations
    """

    context: ValidationContext

    def __init__(self, context: ValidationContext):
        super().__init__(context)

    def enter_argument(self, arg_node: ArgumentNode, *args: Any) -> None:
        context = self.context
        arg_def = context.get_argument()
        field_def = context.get_field_def()
        parent_type = context.get_parent_type()
        if not arg_def and field_def and parent_type:
            arg_name = arg_node.name.value
            field_name = args[3][-1].name.value
            known_args_names = list(field_def.args)
            suggestions = suggestion_list(arg_name, known_args_names)
            context.report_error(
                GraphQLError(
                    f"Unknown argument '{arg_name}'"
                    f" on field '{parent_type.name}.{field_name}'."
                    + did_you_mean(suggestions),
                    arg_node,
                )
            )
