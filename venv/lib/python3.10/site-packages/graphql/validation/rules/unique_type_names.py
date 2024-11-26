from typing import Any, Dict

from ...error import GraphQLError
from ...language import NameNode, TypeDefinitionNode, VisitorAction, SKIP
from . import SDLValidationContext, SDLValidationRule

__all__ = ["UniqueTypeNamesRule"]


class UniqueTypeNamesRule(SDLValidationRule):
    """Unique type names

    A GraphQL document is only valid if all defined types have unique names.
    """

    def __init__(self, context: SDLValidationContext):
        super().__init__(context)
        self.known_type_names: Dict[str, NameNode] = {}
        self.schema = context.schema

    def check_type_name(self, node: TypeDefinitionNode, *_args: Any) -> VisitorAction:
        type_name = node.name.value

        if self.schema and self.schema.get_type(type_name):
            self.report_error(
                GraphQLError(
                    f"Type '{type_name}' already exists in the schema."
                    " It cannot also be defined in this type definition.",
                    node.name,
                )
            )
        else:
            if type_name in self.known_type_names:
                self.report_error(
                    GraphQLError(
                        f"There can be only one type named '{type_name}'.",
                        [self.known_type_names[type_name], node.name],
                    )
                )
            else:
                self.known_type_names[type_name] = node.name
            return SKIP

        return None

    enter_scalar_type_definition = enter_object_type_definition = check_type_name
    enter_interface_type_definition = enter_union_type_definition = check_type_name
    enter_enum_type_definition = enter_input_object_type_definition = check_type_name
