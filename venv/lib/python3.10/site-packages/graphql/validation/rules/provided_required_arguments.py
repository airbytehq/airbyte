from typing import cast, Any, Dict, List, Union

from ...error import GraphQLError
from ...language import (
    DirectiveDefinitionNode,
    DirectiveNode,
    FieldNode,
    InputValueDefinitionNode,
    NonNullTypeNode,
    TypeNode,
    VisitorAction,
    SKIP,
    print_ast,
)
from ...type import GraphQLArgument, is_required_argument, is_type, specified_directives
from . import ASTValidationRule, SDLValidationContext, ValidationContext

__all__ = ["ProvidedRequiredArgumentsRule", "ProvidedRequiredArgumentsOnDirectivesRule"]


class ProvidedRequiredArgumentsOnDirectivesRule(ASTValidationRule):
    """Provided required arguments on directives

    A directive is only valid if all required (non-null without a default value)
    arguments have been provided.

    For internal use only.
    """

    context: Union[ValidationContext, SDLValidationContext]

    def __init__(self, context: Union[ValidationContext, SDLValidationContext]):
        super().__init__(context)
        required_args_map: Dict[
            str, Dict[str, Union[GraphQLArgument, InputValueDefinitionNode]]
        ] = {}

        schema = context.schema
        defined_directives = schema.directives if schema else specified_directives
        for directive in cast(List, defined_directives):
            required_args_map[directive.name] = {
                name: arg
                for name, arg in directive.args.items()
                if is_required_argument(arg)
            }

        ast_definitions = context.document.definitions
        for def_ in ast_definitions:
            if isinstance(def_, DirectiveDefinitionNode):
                required_args_map[def_.name.value] = {
                    arg.name.value: arg
                    for arg in filter(is_required_argument_node, def_.arguments or ())
                }

        self.required_args_map = required_args_map

    def leave_directive(self, directive_node: DirectiveNode, *_args: Any) -> None:
        # Validate on leave to allow for deeper errors to appear first.
        directive_name = directive_node.name.value
        required_args = self.required_args_map.get(directive_name)
        if required_args:

            arg_nodes = directive_node.arguments or ()
            arg_node_set = {arg.name.value for arg in arg_nodes}
            for arg_name in required_args:
                if arg_name not in arg_node_set:
                    arg_type = required_args[arg_name].type
                    arg_type_str = (
                        str(arg_type)
                        if is_type(arg_type)
                        else print_ast(cast(TypeNode, arg_type))
                    )
                    self.report_error(
                        GraphQLError(
                            f"Directive '@{directive_name}' argument '{arg_name}'"
                            f" of type '{arg_type_str}' is required,"
                            " but it was not provided.",
                            directive_node,
                        )
                    )


class ProvidedRequiredArgumentsRule(ProvidedRequiredArgumentsOnDirectivesRule):
    """Provided required arguments

    A field or directive is only valid if all required (non-null without a default
    value) field arguments have been provided.
    """

    context: ValidationContext

    def __init__(self, context: ValidationContext):
        super().__init__(context)

    def leave_field(self, field_node: FieldNode, *_args: Any) -> VisitorAction:
        # Validate on leave to allow for deeper errors to appear first.
        field_def = self.context.get_field_def()
        if not field_def:
            return SKIP
        arg_nodes = field_node.arguments or ()

        arg_node_map = {arg.name.value: arg for arg in arg_nodes}
        for arg_name, arg_def in field_def.args.items():
            arg_node = arg_node_map.get(arg_name)
            if not arg_node and is_required_argument(arg_def):
                self.report_error(
                    GraphQLError(
                        f"Field '{field_node.name.value}' argument '{arg_name}'"
                        f" of type '{arg_def.type}' is required,"
                        " but it was not provided.",
                        field_node,
                    )
                )

        return None


def is_required_argument_node(arg: InputValueDefinitionNode) -> bool:
    return isinstance(arg.type, NonNullTypeNode) and arg.default_value is None
