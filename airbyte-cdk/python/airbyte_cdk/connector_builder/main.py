#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys
from typing import Any, List, Mapping, Optional, Tuple

from airbyte_cdk.connector import BaseConnector
from airbyte_cdk.connector_builder.connector_builder_handler import TestReadLimits, create_source, get_limits, read_stream, resolve_manifest
from airbyte_cdk.entrypoint import AirbyteEntrypoint
from airbyte_cdk.models import AirbyteMessage, ConfiguredAirbyteCatalog
from airbyte_cdk.sources.declarative.manifest_declarative_source import ManifestDeclarativeSource
from airbyte_cdk.utils.traced_exception import AirbyteTracedException


def get_config_and_catalog_from_args(args: List[str]) -> Tuple[str, Mapping[str, Any], Optional[ConfiguredAirbyteCatalog]]:
    # TODO: Add functionality for the `debug` logger.
    #  Currently, no one `debug` level log will be displayed during `read` a stream for a connector created through `connector-builder`.
    parsed_args = AirbyteEntrypoint.parse_args(args)
    config_path, catalog_path = parsed_args.config, parsed_args.catalog
    if parsed_args.command != "read":
        raise ValueError("Only read commands are allowed for Connector Builder requests.")

    config = BaseConnector.read_config(config_path)

    if "__command" not in config:
        raise ValueError(
            f"Invalid config: `__command` should be provided at the root of the config but config only has keys {list(config.keys())}"
        )

    command = config["__command"]
    if command == "test_read":
        catalog = ConfiguredAirbyteCatalog.parse_obj(BaseConnector.read_config(catalog_path))
    else:
        catalog = None

    if "__injected_declarative_manifest" not in config:
        raise ValueError(
            f"Invalid config: `__injected_declarative_manifest` should be provided at the root of the config but config only has keys {list(config.keys())}"
        )

    return command, config, catalog


def handle_connector_builder_request(
    source: ManifestDeclarativeSource,
    command: str,
    config: Mapping[str, Any],
    catalog: Optional[ConfiguredAirbyteCatalog],
    limits: TestReadLimits,
) -> AirbyteMessage:
    if command == "resolve_manifest":
        return resolve_manifest(source)
    elif command == "test_read":
        assert catalog is not None, "`test_read` requires a valid `ConfiguredAirbyteCatalog`, got None."
        return read_stream(source, config, catalog, limits)
    else:
        raise ValueError(f"Unrecognized command {command}.")


def handle_request(args: List[str]) -> AirbyteMessage:
    command, config, catalog = get_config_and_catalog_from_args(args)
    limits = get_limits(config)
    source = create_source(config, limits)
    return handle_connector_builder_request(source, command, config, catalog, limits).json(exclude_unset=True)


if __name__ == "__main__":
    try:
        print(handle_request(sys.argv[1:]))
    except Exception as exc:
        error = AirbyteTracedException.from_exception(exc, message=f"Error handling request: {str(exc)}")
        m = error.as_airbyte_message()
        print(error.as_airbyte_message().json(exclude_unset=True))
