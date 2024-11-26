from typing import Any, cast

from ....error import GraphQLError
from ....language import ArgumentNode, EnumValueNode, FieldNode, ObjectFieldNode
from ....type import GraphQLInputObjectType, get_named_type, is_input_object_type
from .. import ValidationRule

__all__ = ["NoDeprecatedCustomRule"]


class NoDeprecatedCustomRule(ValidationRule):
    """No deprecated

    A GraphQL document is only valid if all selected fields and all used enum values
    have not been deprecated.

    Note: This rule is optional and is not part of the Validation section of the GraphQL
    Specification. The main purpose of this rule is detection of deprecated usages and
    not necessarily to forbid their use when querying a service.
    """

    def enter_field(self, node: FieldNode, *_args: Any) -> None:
        context = self.context
        field_def = context.get_field_def()
        if field_def:
            deprecation_reason = field_def.deprecation_reason
            if deprecation_reason is not None:
                parent_type = context.get_parent_type()
                parent_name = parent_type.name  # type: ignore
                self.report_error(
                    GraphQLError(
                        f"The field {parent_name}.{node.name.value}"
                        f" is deprecated. {deprecation_reason}",
                        node,
                    )
                )

    def enter_argument(self, node: ArgumentNode, *_args: Any) -> None:
        context = self.context
        arg_def = context.get_argument()
        if arg_def:
            deprecation_reason = arg_def.deprecation_reason
            if deprecation_reason is not None:
                directive_def = context.get_directive()
                arg_name = node.name.value
                if directive_def is None:
                    parent_type = context.get_parent_type()
                    parent_name = parent_type.name  # type: ignore
                    field_def = context.get_field_def()
                    field_name = field_def.ast_node.name.value  # type: ignore
                    self.report_error(
                        GraphQLError(
                            f"Field '{parent_name}.{field_name}' argument"
                            f" '{arg_name}' is deprecated. {deprecation_reason}",
                            node,
                        )
                    )
                else:
                    self.report_error(
                        GraphQLError(
                            f"Directive '@{directive_def.name}' argument"
                            f" '{arg_name}' is deprecated. {deprecation_reason}",
                            node,
                        )
                    )

    def enter_object_field(self, node: ObjectFieldNode, *_args: Any) -> None:
        context = self.context
        input_object_def = get_named_type(context.get_parent_input_type())
        if is_input_object_type(input_object_def):
            input_field_def = cast(GraphQLInputObjectType, input_object_def).fields.get(
                node.name.value
            )
            if input_field_def:
                deprecation_reason = input_field_def.deprecation_reason
                if deprecation_reason is not None:
                    field_name = node.name.value
                    input_object_name = input_object_def.name  # type: ignore
                    self.report_error(
                        GraphQLError(
                            f"The input field {input_object_name}.{field_name}"
                            f" is deprecated. {deprecation_reason}",
                            node,
                        )
                    )

    def enter_enum_value(self, node: EnumValueNode, *_args: Any) -> None:
        context = self.context
        enum_value_def = context.get_enum_value()
        if enum_value_def:
            deprecation_reason = enum_value_def.deprecation_reason
            if deprecation_reason is not None:  # pragma: no cover else
                enum_type_def = get_named_type(context.get_input_type())
                enum_type_name = enum_type_def.name  # type: ignore
                self.report_error(
                    GraphQLError(
                        f"The enum value '{enum_type_name}.{node.value}'"
                        f" is deprecated. {deprecation_reason}",
                        node,
                    )
                )
