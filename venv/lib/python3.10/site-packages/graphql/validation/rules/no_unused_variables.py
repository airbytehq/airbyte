from typing import Any, List, Set

from ...error import GraphQLError
from ...language import OperationDefinitionNode, VariableDefinitionNode
from . import ValidationContext, ValidationRule

__all__ = ["NoUnusedVariablesRule"]


class NoUnusedVariablesRule(ValidationRule):
    """No unused variables

    A GraphQL operation is only valid if all variables defined by an operation are used,
    either directly or within a spread fragment.

    See https://spec.graphql.org/draft/#sec-All-Variables-Used
    """

    def __init__(self, context: ValidationContext):
        super().__init__(context)
        self.variable_defs: List[VariableDefinitionNode] = []

    def enter_operation_definition(self, *_args: Any) -> None:
        self.variable_defs.clear()

    def leave_operation_definition(
        self, operation: OperationDefinitionNode, *_args: Any
    ) -> None:
        variable_name_used: Set[str] = set()
        usages = self.context.get_recursive_variable_usages(operation)

        for usage in usages:
            variable_name_used.add(usage.node.name.value)

        for variable_def in self.variable_defs:
            variable_name = variable_def.variable.name.value
            if variable_name not in variable_name_used:
                self.report_error(
                    GraphQLError(
                        f"Variable '${variable_name}' is never used"
                        f" in operation '{operation.name.value}'."
                        if operation.name
                        else f"Variable '${variable_name}' is never used.",
                        variable_def,
                    )
                )

    def enter_variable_definition(
        self, definition: VariableDefinitionNode, *_args: Any
    ) -> None:
        self.variable_defs.append(definition)
