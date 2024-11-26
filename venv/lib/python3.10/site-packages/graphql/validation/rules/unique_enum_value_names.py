from collections import defaultdict
from typing import cast, Any, Dict

from ...error import GraphQLError
from ...language import NameNode, EnumTypeDefinitionNode, VisitorAction, SKIP
from ...type import is_enum_type, GraphQLEnumType
from . import SDLValidationContext, SDLValidationRule

__all__ = ["UniqueEnumValueNamesRule"]


class UniqueEnumValueNamesRule(SDLValidationRule):
    """Unique enum value names

    A GraphQL enum type is only valid if all its values are uniquely named.
    """

    def __init__(self, context: SDLValidationContext):
        super().__init__(context)
        schema = context.schema
        self.existing_type_map = schema.type_map if schema else {}
        self.known_value_names: Dict[str, Dict[str, NameNode]] = defaultdict(dict)

    def check_value_uniqueness(
        self, node: EnumTypeDefinitionNode, *_args: Any
    ) -> VisitorAction:
        existing_type_map = self.existing_type_map
        type_name = node.name.value
        value_names = self.known_value_names[type_name]

        for value_def in node.values or []:
            value_name = value_def.name.value

            existing_type = existing_type_map.get(type_name)
            if (
                is_enum_type(existing_type)
                and value_name in cast(GraphQLEnumType, existing_type).values
            ):
                self.report_error(
                    GraphQLError(
                        f"Enum value '{type_name}.{value_name}'"
                        " already exists in the schema."
                        " It cannot also be defined in this type extension.",
                        value_def.name,
                    )
                )
            elif value_name in value_names:
                self.report_error(
                    GraphQLError(
                        f"Enum value '{type_name}.{value_name}'"
                        " can only be defined once.",
                        [value_names[value_name], value_def.name],
                    )
                )
            else:
                value_names[value_name] = value_def.name

        return SKIP

    enter_enum_type_definition = check_value_uniqueness
    enter_enum_type_extension = check_value_uniqueness
