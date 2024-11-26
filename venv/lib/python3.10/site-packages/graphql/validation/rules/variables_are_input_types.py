from typing import Any

from ...error import GraphQLError
from ...language import VariableDefinitionNode, print_ast
from ...type import is_input_type
from ...utilities import type_from_ast
from . import ValidationRule

__all__ = ["VariablesAreInputTypesRule"]


class VariablesAreInputTypesRule(ValidationRule):
    """Variables are input types

    A GraphQL operation is only valid if all the variables it defines are of input types
    (scalar, enum, or input object).

    See https://spec.graphql.org/draft/#sec-Variables-Are-Input-Types
    """

    def enter_variable_definition(
        self, node: VariableDefinitionNode, *_args: Any
    ) -> None:
        type_ = type_from_ast(self.context.schema, node.type)

        # If the variable type is not an input type, return an error.
        if type_ is not None and not is_input_type(type_):
            variable_name = node.variable.name.value
            type_name = print_ast(node.type)
            self.report_error(
                GraphQLError(
                    f"Variable '${variable_name}'"
                    f" cannot be non-input type '{type_name}'.",
                    node.type,
                )
            )
