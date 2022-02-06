#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
import os
from typing import Any, Callable, List

from jinja2 import Environment, PackageLoader, select_autoescape

from .definitions import BaseDefinition

JINJA_ENV = Environment(loader=PackageLoader("octavia_cli"), autoescape=select_autoescape(), trim_blocks=False, lstrip_blocks=True)


class FieldToRender:
    def __init__(self, name: str, required: bool, field_metadata: dict) -> None:
        """Initialize a FieldToRender instance

        Args:
            name (str): name of the field
            required (bool): whether it's a required field or not
            field_metadata (dict): metadata associated with the field
        """
        self.name = name
        self.required = required
        self.field_metadata = field_metadata
        self.one_of_values = self._get_one_of_values()
        self.object_properties = get_object_fields(field_metadata)
        self.array_items = self._get_array_items()
        self.comment = self._build_comment(
            [
                self._get_secret_comment,
                self._get_required_comment,
                self._get_type_comment,
                self._get_description_comment,
                self._get_example_comment,
            ]
        )
        self.default = self._get_default()

    def __getattr__(self, name: str) -> Any:
        """Map field_metadata keys to attributes of Field.

        Args:
            name (str): attribute name

        Returns:
            [Any]: attribute value
        """
        if name in self.field_metadata:
            return self.field_metadata.get(name)

    @property
    def _is_array_of_objects(self) -> bool:
        if self.type == "array" and self.items:
            if self.items["type"] == "object":
                return True
        return False

    def _get_one_of_values(self) -> List[List["FieldToRender"]]:
        """An object field get have multiple kind of fields if it's a oneOf.
        This functions returns all the possible one of values the field can take.
        Returns:
            [list]: List of oneof values.
        """
        if not self.oneOf:
            return []
        one_of_values = []
        for one_of_value in self.oneOf:
            properties = get_object_fields(one_of_value)
            one_of_values.append(properties)
        return one_of_values

    def _get_array_items(self) -> List["FieldToRender"]:
        """If the field is an array of objects, retrieve fields of these objects.

        Returns:
            [list]: List of fields
        """
        if self._is_array_of_objects:
            required_fields = self.items.get("required", [])
            return parse_fields(required_fields, self.items["properties"])
        return []

    def _get_required_comment(self) -> str:
        return "REQUIRED" if self.required else "OPTIONAL"

    def _get_type_comment(self) -> str:
        return self.type if self.type else None

    def _get_secret_comment(self) -> str:
        return "🤫" if self.airbyte_secret else None

    def _get_description_comment(self) -> str:
        return self.description if self.description else None

    def _get_example_comment(self) -> str:
        example_comment = None
        if self.examples:
            if isinstance(self.examples, list):
                if len(self.examples) > 1:
                    example_comment = f"Examples: {', '.join([str(example) for example in self.examples])}"
                else:
                    example_comment = f"Example: {self.examples[0]}"
            else:
                example_comment = f"Example: {self.examples}"
        return example_comment

    def _get_default(self) -> str:
        if self.const:
            return self.const
        return self.default

    @staticmethod
    def _build_comment(comment_functions: Callable) -> str:
        return " | ".join(filter(None, [comment_fn() for comment_fn in comment_functions])).replace("\n", "")


def parse_fields(required_fields: List[str], fields: dict) -> List["FieldToRender"]:
    return [FieldToRender(f_name, f_name in required_fields, f_metadata) for f_name, f_metadata in fields.items()]


def get_object_fields(field_metadata: dict) -> List["FieldToRender"]:
    if field_metadata.get("properties"):
        required_fields = field_metadata.get("required", [])
        return parse_fields(required_fields, field_metadata["properties"])
    return []


class ConnectionSpecificationRenderer:
    TEMPLATE = JINJA_ENV.get_template("source_or_destination.yaml.j2")

    def __init__(self, resource_name: str, definition: BaseDefinition) -> None:
        self.resource_name = resource_name
        self.definition = definition

    def _parse_connection_specification(self, schema: dict) -> List[List["FieldToRender"]]:
        if schema.get("oneOf"):
            roots = []
            for one_of_value in schema.get("oneOf"):
                required_fields = one_of_value.get("required", [])
                roots.append(parse_fields(required_fields, one_of_value["properties"]))
            return roots
        else:
            required_fields = schema.get("required", [])
            return [parse_fields(required_fields, schema["properties"])]

    def _get_output_path(self, project_path: str) -> str:
        return os.path.join(project_path, f"{self.definition.type}s", f"{self.resource_name}.yaml")

    def write_yaml(self, project_path: str) -> str:
        output_path = self._get_output_path(project_path)
        parsed_schema = self._parse_connection_specification(self.definition.specification.connection_specification)

        rendered = self.TEMPLATE.render(
            {"resource_name": self.resource_name, "definition": self.definition, "configuration_fields": parsed_schema}
        )

        with open(output_path, "w") as f:
            f.write(rendered)
        return output_path
