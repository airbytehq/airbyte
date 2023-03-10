#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys
from typing import Any, List, Mapping

from airbyte_cdk.connector import BaseConnector
from airbyte_cdk.entrypoint import AirbyteEntrypoint, launch
from airbyte_cdk.models import AirbyteMessage
from airbyte_cdk.models import ConfiguredAirbyteCatalog
from airbyte_cdk.sources.declarative.manifest_declarative_source import ManifestDeclarativeSource
from airbyte_cdk.sources.source import Source
from connector_builder import connector_builder_handler


def create_source(config: Mapping[str, Any], debug: bool) -> ManifestDeclarativeSource:
    manifest = config.get("__injected_declarative_manifest")
    return ManifestDeclarativeSource(manifest, debug)


def get_config_from_args(args: List[str]) -> Mapping[str, Any]:
    command, config_filepath = preparse(args)
    if command == "spec":
        raise ValueError("spec command is not supported for injected declarative manifest")

    config = BaseConnector.read_config(config_filepath)

    if "__injected_declarative_manifest" not in config:
        raise ValueError(
            f"Invalid config: `__injected_declarative_manifest` should be provided at the root of the config but config only has keys {list(config.keys())}"
        )

    return config


def execute_command(source: ManifestDeclarativeSource, config: Mapping[str, Any],
                    configured_catalog: ConfiguredAirbyteCatalog) -> AirbyteMessage:
    command = configured_catalog.streams[0].stream.name
    if command == "resolve_manifest":
        return connector_builder_handler.resolve_manifest(source)
    else:
        return connector_builder_handler.read_stream(source, config, configured_catalog)


def handle_connector_builder_request(source: ManifestDeclarativeSource, config: Mapping[str, Any],
                                     configured_catalog: ConfiguredAirbyteCatalog):
    message = execute_command(source, config, configured_catalog)
    print(message.json(exclude_unset=True))


def handle_connector_request(source: ManifestDeclarativeSource, args: List[str]):
    # Verify that the correct args are present for the production codepaths.
    launch(source, sys.argv[1:])


def handle_request(args: List[str]):
    # FIXME: need to make sure the manifest is passed in the config too!
    parser = AirbyteEntrypoint.parse_args(args)
    config_path = parser.config
    catalog_path = parser.catalog
    config = BaseConnector.read_config(config_path)
    catalog = Source.read_catalog(catalog_path)
    is_builder_request = connector_builder_handler.is_connector_builder_request(config, catalog)
    source = create_source(config, is_builder_request)
    if is_builder_request:
        handle_connector_builder_request(source, config, catalog)
    else:
        handle_connector_request(source, args)


if __name__ == "__main__":
    handle_request(sys.argv[1:])
