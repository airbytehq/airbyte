#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pkgutil
from typing import Any, List, Mapping, Optional

import yaml

from airbyte_cdk.models import AirbyteStateMessage, ConfiguredAirbyteCatalog
from airbyte_cdk.sources.declarative.concurrent_declarative_source import (
    ConcurrentDeclarativeSource,
)
from airbyte_cdk.sources.types import ConnectionDefinition


class YamlDeclarativeSource(ConcurrentDeclarativeSource):
    """Declarative source defined by a yaml file"""

    def __init__(
        self,
        path_to_yaml: str,
        debug: bool = False,
        catalog: Optional[ConfiguredAirbyteCatalog] = None,
        config: Optional[Mapping[str, Any]] = None,
        state: Optional[List[AirbyteStateMessage]] = None,
        config_path: Optional[str] = None,
    ) -> None:
        """
        :param path_to_yaml: Path to the yaml file describing the source
        """
        self._path_to_yaml = path_to_yaml
        source_config = self._read_and_parse_yaml_file(path_to_yaml)

        super().__init__(
            catalog=catalog or ConfiguredAirbyteCatalog(streams=[]),
            config=config or {},
            state=state or [],
            source_config=source_config,
            config_path=config_path,
        )

    def _read_and_parse_yaml_file(self, path_to_yaml_file: str) -> ConnectionDefinition:
        try:
            # For testing purposes, we want to allow to just pass a file
            with open(path_to_yaml_file, "r") as f:
                return yaml.safe_load(f)  # type: ignore  # we assume the yaml represents a ConnectionDefinition
        except FileNotFoundError:
            # Running inside the container, the working directory during an operation is not structured the same as the static files
            package = self.__class__.__module__.split(".")[0]

            yaml_config = pkgutil.get_data(package, path_to_yaml_file)
            if yaml_config:
                decoded_yaml = yaml_config.decode()
                return self._parse(decoded_yaml)
            return {}

    def _emit_manifest_debug_message(self, extra_args: dict[str, Any]) -> None:
        extra_args["path_to_yaml"] = self._path_to_yaml

    @staticmethod
    def _parse(connection_definition_str: str) -> ConnectionDefinition:
        """
        Parses a yaml file into a manifest. Component references still exist in the manifest which will be
        resolved during the creating of the DeclarativeSource.
        :param connection_definition_str: yaml string to parse
        :return: The ConnectionDefinition parsed from connection_definition_str
        """
        return yaml.safe_load(connection_definition_str)  # type: ignore # yaml.safe_load doesn't return a type but know it is a Mapping
