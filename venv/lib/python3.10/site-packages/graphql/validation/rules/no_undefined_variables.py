from typing import Any, Set

from ...error import GraphQLError
from ...language import OperationDefinitionNode, VariableDefinitionNode
from . import ValidationContext, ValidationRule

__all__ = ["NoUndefinedVariablesRule"]


class NoUndefinedVariablesRule(ValidationRule):
    """No undefined variables

    A GraphQL operation is only valid if all variables encountered, both directly and
    via fragment spreads, are defined by that operation.

    See https://spec.graphql.org/draft/#sec-All-Variable-Uses-Defined
    """

    def __init__(self, context: ValidationContext):
        super().__init__(context)
        self.defined_variable_names: Set[str] = set()

    def enter_operation_definition(self, *_args: Any) -> None:
        self.defined_variable_names.clear()

    def leave_operation_definition(
        self, operation: OperationDefinitionNode, *_args: Any
    ) -> None:
        usages = self.context.get_recursive_variable_usages(operation)
        defined_variables = self.defined_variable_names
        for usage in usages:
            node = usage.node
            var_name = node.name.value
            if var_name not in defined_variables:
                self.report_error(
                    GraphQLError(
                        f"Variable '${var_name}' is not defined"
                        f" by operation '{operation.name.value}'."
                        if operation.name
                        else f"Variable '${var_name}' is not defined.",
                        [node, operation],
                    )
                )

    def enter_variable_definition(
        self, node: VariableDefinitionNode, *_args: Any
    ) -> None:
        self.defined_variable_names.add(node.variable.name.value)
