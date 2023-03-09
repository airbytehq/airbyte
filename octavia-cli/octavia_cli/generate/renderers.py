#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import abc
import os
from pathlib import Path
from typing import Any, Callable, List

import click
import yaml
from airbyte_api_client.model.airbyte_catalog import AirbyteCatalog
from jinja2 import Environment, PackageLoader, Template, select_autoescape
from octavia_cli.apply import resources
from slugify import slugify

from .definitions import BaseDefinition, ConnectionDefinition
from .yaml_dumpers import CatalogDumper

JINJA_ENV = Environment(loader=PackageLoader(__package__), autoescape=select_autoescape(), trim_blocks=False, lstrip_blocks=True)


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
    def is_array_of_objects(self) -> bool:
        if self.type == "array" and self.items:
            if self.items.get("type") == "object":
                return True
        return False

    def _get_one_of_values(self) -> List[List["FieldToRender"]]:
        """An object field can have multiple kind of values if it's a oneOf.
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
        if self.is_array_of_objects:
            required_fields = self.items.get("required", [])
            return parse_fields(required_fields, self.items["properties"])
        return []

    def _get_required_comment(self) -> str:
        return "REQUIRED" if self.required else "OPTIONAL"

    def _get_type_comment(self) -> str:
        if isinstance(self.type, list):
            return ", ".join(self.type)
        return self.type if self.type else None

    def _get_secret_comment(self) -> str:
        return "SECRET (please store in environment variables)" if self.airbyte_secret else None

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
        if self.airbyte_secret:
            return f"${{{self.name.upper()}}}"
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


class BaseRenderer(abc.ABC):
    @property
    @abc.abstractmethod
    def TEMPLATE(
        self,
    ) -> Template:  # pragma: no cover
        pass

    def __init__(self, resource_name: str) -> None:
        self.resource_name = resource_name

    @classmethod
    def get_output_path(cls, project_path: str, definition_type: str, resource_name: str) -> Path:
        """Get rendered file output path
        Args:
            project_path (str): Current project path.
            definition_type (str): Current definition_type.
            resource_name (str): Current resource_name.
        Returns:
            Path: Full path to the output path.
        """
        directory = os.path.join(project_path, f"{definition_type}s", slugify(resource_name, separator="_"))
        if not os.path.exists(directory):
            os.makedirs(directory)
        return Path(os.path.join(directory, "configuration.yaml"))

    @staticmethod
    def _confirm_overwrite(output_path):
        """User input to determine if the configuration paqth should be overwritten.
        Args:
            output_path (str): Path of the configuration file to overwrite
        Returns:
            bool: Boolean representing if the configuration file is to be overwritten
        """
        overwrite = True
        if output_path.is_file():
            overwrite = click.confirm(
                f"The configuration octavia-cli is about to create already exists, do you want to replace it? ({output_path})"
            )
        return overwrite

    @abc.abstractmethod
    def _render(self):  # pragma: no cover
        """Runs the template rendering.
        Raises:
            NotImplementedError: Must be implemented on subclasses.
        """
        raise NotImplementedError

    def write_yaml(self, project_path: Path) -> str:
        """Write rendered specification to a YAML file in local project path.
        Args:
            project_path (str): Path to directory hosting the octavia project.
        Returns:
            str: Path to the rendered specification.
        """
        output_path = self.get_output_path(project_path, self.definition.type, self.resource_name)
        if self._confirm_overwrite(output_path):
            with open(output_path, "w") as f:
                rendered_yaml = self._render()
                f.write(rendered_yaml)
        return output_path

    def import_configuration(self, project_path: str, configuration: dict) -> Path:
        """Import the resource configuration. Save the yaml file to disk and return its path.
        Args:
            project_path (str): Current project path.
            configuration (dict): The configuration of the resource.
        Returns:
            Path: Path to the resource configuration.
        """
        rendered = self._render()
        data = yaml.safe_load(rendered)
        data["configuration"] = configuration
        output_path = self.get_output_path(project_path, self.definition.type, self.resource_name)
        if self._confirm_overwrite(output_path):
            with open(output_path, "wb") as f:
                yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True, encoding="utf-8")
        return output_path


class ConnectorSpecificationRenderer(BaseRenderer):
    TEMPLATE = JINJA_ENV.get_template("source_or_destination.yaml.j2")

    def __init__(self, resource_name: str, definition: BaseDefinition) -> None:
        """Connector specification renderer constructor.
        Args:
            resource_name (str): Name of the source or destination.
            definition (BaseDefinition): The definition related to a source or a destination.
        """
        super().__init__(resource_name)
        self.definition = definition

    def _parse_connection_specification(self, schema: dict) -> List[List["FieldToRender"]]:
        """Create a renderable structure from the specification schema
        Returns:
            List[List["FieldToRender"]]: List of list of fields to render.
        """
        if schema.get("oneOf"):
            roots = []
            for one_of_value in schema.get("oneOf"):
                required_fields = one_of_value.get("required", [])
                roots.append(parse_fields(required_fields, one_of_value["properties"]))
            return roots
        else:
            required_fields = schema.get("required", [])
            return [parse_fields(required_fields, schema["properties"])]

    def _render(self) -> str:
        parsed_schema = self._parse_connection_specification(self.definition.specification.connection_specification)
        return self.TEMPLATE.render(
            {"resource_name": self.resource_name, "definition": self.definition, "configuration_fields": parsed_schema}
        )


class ConnectionRenderer(BaseRenderer):

    TEMPLATE = JINJA_ENV.get_template("connection.yaml.j2")
    definition = ConnectionDefinition
    KEYS_TO_REMOVE_FROM_REMOTE_CONFIGURATION = [
        "connection_id",
        "name",
        "source_id",
        "destination_id",
        "latest_sync_job_created_at",
        "latest_sync_job_status",
        "source",
        "destination",
        "is_syncing",
        "operation_ids",
        "catalog_id",
        "catalog_diff",
    ]

    def __init__(self, connection_name: str, source: resources.Source, destination: resources.Destination) -> None:
        """Connection renderer constructor.
        Args:
            connection_name (str): Name of the connection to render.
            source (resources.Source): Connection's source.
            destination (resources.Destination): Connections's destination.
        """
        super().__init__(connection_name)
        self.source = source
        self.destination = destination

    @staticmethod
    def catalog_to_yaml(catalog: AirbyteCatalog) -> str:
        """Convert the source catalog to a YAML string.
        Args:
            catalog (AirbyteCatalog): Source's catalog.
        Returns:
            str: Catalog rendered as yaml.
        """
        return yaml.dump(catalog.to_dict(), Dumper=CatalogDumper, default_flow_style=False)

    def _render(self) -> str:
        yaml_catalog = self.catalog_to_yaml(self.source.catalog)
        return self.TEMPLATE.render(
            {
                "connection_name": self.resource_name,
                "source_configuration_path": self.source.configuration_path,
                "destination_configuration_path": self.destination.configuration_path,
                "catalog": yaml_catalog,
                "supports_normalization": self.destination.definition.normalization_config.supported,
                "supports_dbt": self.destination.definition.supports_dbt,
            }
        )

    def import_configuration(self, project_path: Path, configuration: dict) -> Path:
        """Import the connection configuration. Save the yaml file to disk and return its path.
        Args:
            project_path (str): Current project path.
            configuration (dict): The configuration of the connection.
        Returns:
            Path: Path to the connection configuration.
        """
        rendered = self._render()
        data = yaml.safe_load(rendered)
        data["configuration"] = {k: v for k, v in configuration.items() if k not in self.KEYS_TO_REMOVE_FROM_REMOTE_CONFIGURATION}
        if "operations" in data["configuration"] and len(data["configuration"]["operations"]) == 0:
            data["configuration"].pop("operations")
        [
            operation.pop(field_to_remove, "")
            for field_to_remove in ["workspace_id", "operation_id"]
            for operation in data["configuration"].get("operations", {})
        ]
        output_path = self.get_output_path(project_path, self.definition.type, self.resource_name)
        if self._confirm_overwrite(output_path):
            with open(output_path, "wb") as f:
                yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True, encoding="utf-8")
        return output_path
