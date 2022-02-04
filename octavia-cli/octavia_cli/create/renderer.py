#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
import os

from jinja2 import Environment, PackageLoader, select_autoescape

from .schema_utils import parse_properties

JINJA_ENV = Environment(loader=PackageLoader("octavia_cli"), autoescape=select_autoescape())


class SpecRenderer:
    TEMPLATE = JINJA_ENV.get_template("sources_destinations.yaml.j2")

    def __init__(
        self,
        definition_name,
        definition_type,
        definition_id,
        definition_image,
        definition_version,
        definition_documentation_url,
        definition_schema,
    ) -> None:
        self.definition_name = definition_name
        self.definition_type = definition_type

        self.definition_metadata = {
            "name": definition_name,
            "type": definition_type,
            "id": definition_id,
            "image": definition_image,
            "version": definition_version,
            "documentation_url": definition_documentation_url,
        }
        self.definition_schema = definition_schema

    def parse_schema(self, schema):
        if schema.get("oneOf"):
            roots = []
            for one_of_value in schema.get("oneOf"):
                required_fields = one_of_value.get("required", [])
                roots.append(parse_properties(required_fields, one_of_value["properties"]))
            return roots
        else:
            required_fields = schema.get("required", [])
            return [parse_properties(required_fields, schema["properties"])]

    def get_output_path(self, project_path):
        return os.path.join(project_path, f"{self.definition_type}s", f"{self.definition_name}.yaml")

    def write_yaml(self, project_path):

        output_path = self.get_output_path(project_path)
        parsed_schema = self.parse_schema(self.definition_schema)

        rendered = self.TEMPLATE.render({"definition_metadata": self.definition_metadata, "configuration_fields": parsed_schema})

        with open(output_path, "w") as f:
            f.write(rendered)
        return output_path
