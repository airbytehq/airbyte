from operator import attrgetter
from typing import Any, Collection

from ...error import GraphQLError
from ...language import (
    DirectiveDefinitionNode,
    FieldDefinitionNode,
    InputValueDefinitionNode,
    InterfaceTypeDefinitionNode,
    InterfaceTypeExtensionNode,
    NameNode,
    ObjectTypeDefinitionNode,
    ObjectTypeExtensionNode,
    VisitorAction,
    SKIP,
)
from ...pyutils import group_by
from . import SDLValidationRule

__all__ = ["UniqueArgumentDefinitionNamesRule"]


class UniqueArgumentDefinitionNamesRule(SDLValidationRule):
    """Unique argument definition names

    A GraphQL Object or Interface type is only valid if all its fields have uniquely
    named arguments.
    A GraphQL Directive is only valid if all its arguments are uniquely named.

    See https://spec.graphql.org/draft/#sec-Argument-Uniqueness
    """

    def enter_directive_definition(
        self, node: DirectiveDefinitionNode, *_args: Any
    ) -> VisitorAction:
        return self.check_arg_uniqueness(f"@{node.name.value}", node.arguments)

    def enter_interface_type_definition(
        self, node: InterfaceTypeDefinitionNode, *_args: Any
    ) -> VisitorAction:
        return self.check_arg_uniqueness_per_field(node.name, node.fields)

    def enter_interface_type_extension(
        self, node: InterfaceTypeExtensionNode, *_args: Any
    ) -> VisitorAction:
        return self.check_arg_uniqueness_per_field(node.name, node.fields)

    def enter_object_type_definition(
        self, node: ObjectTypeDefinitionNode, *_args: Any
    ) -> VisitorAction:
        return self.check_arg_uniqueness_per_field(node.name, node.fields)

    def enter_object_type_extension(
        self, node: ObjectTypeExtensionNode, *_args: Any
    ) -> VisitorAction:
        return self.check_arg_uniqueness_per_field(node.name, node.fields)

    def check_arg_uniqueness_per_field(
        self,
        name: NameNode,
        fields: Collection[FieldDefinitionNode],
    ) -> VisitorAction:
        type_name = name.value
        for field_def in fields:
            field_name = field_def.name.value
            argument_nodes = field_def.arguments or ()
            self.check_arg_uniqueness(f"{type_name}.{field_name}", argument_nodes)
        return SKIP

    def check_arg_uniqueness(
        self, parent_name: str, argument_nodes: Collection[InputValueDefinitionNode]
    ) -> VisitorAction:
        seen_args = group_by(argument_nodes, attrgetter("name.value"))
        for arg_name, arg_nodes in seen_args.items():
            if len(arg_nodes) > 1:
                self.report_error(
                    GraphQLError(
                        f"Argument '{parent_name}({arg_name}:)'"
                        " can only be defined once.",
                        [node.name for node in arg_nodes],
                    )
                )
        return SKIP
