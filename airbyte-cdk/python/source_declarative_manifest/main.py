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


def handle_connector_request(source: ManifestDeclarativeSource, args: List[str]):
    # Verify that the correct args are present for the production codepaths.
    launch(source, args)


def handle_request(args: List[str]):
    parser = AirbyteEntrypoint.parse_args(args)
    command = parser.command
    config_path = parser.config
    config = BaseConnector.read_config(config_path)
    if "__injected_declarative_manifest" not in config:
        raise ValueError(
            f"Invalid config: `__injected_declarative_manifest` should be provided at the root of the config but config only has keys {list(config.keys())}"
        )
    if command == "read":
        catalog_path = parser.catalog
        catalog = Source.read_catalog(catalog_path)
        is_builder_request = connector_builder_handler.is_connector_builder_request(config, catalog)
        source = create_source(config, is_builder_request)
        if is_builder_request:
            print(is_builder_request(source))
        else:
            handle_connector_request(source, args)
    else:
        source = create_source(config, False)
        handle_connector_request(source, args)


if __name__ == "__main__":
    handle_request(sys.argv[1:])
