from collections import defaultdict
from typing import Any, Dict

from ...error import GraphQLError
from ...language import NameNode, ObjectTypeDefinitionNode, VisitorAction, SKIP
from ...type import is_object_type, is_interface_type, is_input_object_type
from . import SDLValidationContext, SDLValidationRule

__all__ = ["UniqueFieldDefinitionNamesRule"]


class UniqueFieldDefinitionNamesRule(SDLValidationRule):
    """Unique field definition names

    A GraphQL complex type is only valid if all its fields are uniquely named.
    """

    def __init__(self, context: SDLValidationContext):
        super().__init__(context)
        schema = context.schema
        self.existing_type_map = schema.type_map if schema else {}
        self.known_field_names: Dict[str, Dict[str, NameNode]] = defaultdict(dict)

    def check_field_uniqueness(
        self, node: ObjectTypeDefinitionNode, *_args: Any
    ) -> VisitorAction:
        existing_type_map = self.existing_type_map
        type_name = node.name.value
        field_names = self.known_field_names[type_name]

        for field_def in node.fields or []:
            field_name = field_def.name.value

            if has_field(existing_type_map.get(type_name), field_name):
                self.report_error(
                    GraphQLError(
                        f"Field '{type_name}.{field_name}'"
                        " already exists in the schema."
                        " It cannot also be defined in this type extension.",
                        field_def.name,
                    )
                )
            elif field_name in field_names:
                self.report_error(
                    GraphQLError(
                        f"Field '{type_name}.{field_name}'"
                        " can only be defined once.",
                        [field_names[field_name], field_def.name],
                    )
                )
            else:
                field_names[field_name] = field_def.name

        return SKIP

    enter_input_object_type_definition = check_field_uniqueness
    enter_input_object_type_extension = check_field_uniqueness
    enter_interface_type_definition = check_field_uniqueness
    enter_interface_type_extension = check_field_uniqueness
    enter_object_type_definition = check_field_uniqueness
    enter_object_type_extension = check_field_uniqueness


def has_field(type_: Any, field_name: str) -> bool:
    if is_object_type(type_) or is_interface_type(type_) or is_input_object_type(type_):
        return field_name in type_.fields
    return False
