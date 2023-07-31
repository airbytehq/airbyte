#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import errno
import os
import pkgutil
from typing import Any, Dict

import yaml
from airbyte_cdk.sources.declarative.manifest_declarative_source import ManifestDeclarativeSource
from airbyte_cdk.sources.declarative.types import ConnectionDefinition


class YamlDeclarativeSource(ManifestDeclarativeSource):
    """Declarative source defined by a yaml file"""

    def __init__(self, path_to_yaml: str, debug: bool = False) -> None:
        """
        :param path_to_yaml: Path to the yaml file describing the source
        """
        self._path_to_yaml = path_to_yaml
        source_config = self._read_and_parse_yaml_file(path_to_yaml)
        # this is actually not true that we pass a ConnectionDefinition to ManifestDeclarativeSource but ManifestDeclarativeSource cast it
        # as a dictionary anyway
        super().__init__(source_config, debug)

    def _read_and_parse_yaml_file(self, path_to_yaml_file: str) -> ConnectionDefinition:
        try:
            package = self.__class__.__module__.split(".")[0]
            yaml_config = pkgutil.get_data(package, path_to_yaml_file)
            if yaml_config:
                decoded_yaml = yaml_config.decode()
                return self._parse(decoded_yaml)
            else:
                raise FileNotFoundError(f"pkgutil.get_data returned empty data for package {package} and file {path_to_yaml_file}")
        except FileNotFoundError as pkg_file_error:
            try:
                with open(path_to_yaml_file) as f:
                    return self._parse(f.read())
            except FileNotFoundError as open_file_error:
                raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), f"{pkg_file_error.filename} or {open_file_error.filename}")

    def _emit_manifest_debug_message(self, extra_args: Dict[str, Any]) -> None:
        extra_args["path_to_yaml"] = self._path_to_yaml
        self.logger.debug("declarative source created from parsed YAML manifest", extra=extra_args)

    @staticmethod
    def _parse(connection_definition_str: str) -> ConnectionDefinition:
        """
        Parses a yaml file into a manifest. Component references still exist in the manifest which will be
        resolved during the creating of the DeclarativeSource.
        :param connection_definition_str: yaml string to parse
        :return: The ConnectionDefinition parsed from connection_definition_str
        """
        return yaml.safe_load(connection_definition_str)  # type: ignore  # this is actually not true that this method returns a ConnectionDefinition
