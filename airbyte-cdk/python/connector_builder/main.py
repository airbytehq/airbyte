#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import argparse
import sys
from typing import Any, List, Mapping, Tuple

from airbyte_cdk.connector import BaseConnector
from airbyte_cdk.entrypoint import AirbyteEntrypoint, launch
from airbyte_cdk.sources.declarative.manifest_declarative_source import ManifestDeclarativeSource
from connector_builder.connector_builder_handler import resolve_manifest, read_stream
from airbyte_cdk.models import ConfiguredAirbyteCatalog


def create_source(config: Mapping[str, Any], debug: bool) -> ManifestDeclarativeSource:
    manifest = config.get("__injected_declarative_manifest")
    return ManifestDeclarativeSource(manifest, debug)


def handle_connector_builder_request(source: ManifestDeclarativeSource, config: Mapping[str, Any], catalog: ConfiguredAirbyteCatalog):
    command = config["__command"]
    if command == "resolve_manifest":
        result = resolve_manifest(source)
    elif command == "read":
        result = read_stream(source, config, catalog)
    else:
        raise ValueError(f"Unrecognized command {command}.")
    print(result)


def handle_connector_request(source: ManifestDeclarativeSource, args: List[str]):
    # Verify that the correct args are present for the production codepaths.
    AirbyteEntrypoint.parse_args(args)
    launch(source, sys.argv[1:])


def handle_request(args: List[str]):
    parser = AirbyteEntrypoint.parse_args(args)
    config_path, catalog_path = parser.config, parser.catalog
    config = BaseConnector.read_config(config_path)
    catalog = ConfiguredAirbyteCatalog.parse_obj(BaseConnector.read_config(catalog_path))
    if "__command" in config:
        source = create_source(config, True)
        handle_connector_builder_request(source, config, catalog)
    else:
        source = create_source(config, False)
        handle_connector_request(source, args)


if __name__ == "__main__":
    handle_request(sys.argv[1:])
