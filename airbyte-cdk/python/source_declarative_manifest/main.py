#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import argparse
import sys
from typing import Any, List, Mapping, Tuple

from airbyte_cdk.connector import BaseConnector
from airbyte_cdk.entrypoint import AirbyteEntrypoint, launch
from airbyte_cdk.models import AirbyteMessage
from airbyte_cdk.sources.declarative.declarative_source import DeclarativeSource
from airbyte_cdk.sources.declarative.manifest_declarative_source import ManifestDeclarativeSource
from connector_builder import connector_builder_handler


def create_source(config: Mapping[str, Any], debug: bool) -> DeclarativeSource:
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


def preparse(args: List[str]) -> Tuple[str, str]:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", type=str, help="Airbyte Protocol command")
    parser.add_argument("--config", type=str, required=True, help="path to the json configuration file")
    parsed, _ = parser.parse_known_args(args)
    return parsed.command, parsed.config


def execute_command(source: DeclarativeSource, config: Mapping[str, Any]) -> AirbyteMessage:
    command = config.get("__command")
    if command == "resolve_manifest":
        return connector_builder_handler.resolve_manifest(source)
    elif command == "read":
        return connector_builder_handler.read_stream(source, config)
    raise ValueError(f"Unrecognized command {command}.")

def handle_connector_builder_request(source: DeclarativeSource, config: Mapping[str, Any]):
    message = execute_command(source, config)
    print(message.json(exclude_unset=True))


def handle_connector_request(source: DeclarativeSource, args: List[str]):
    # Verify that the correct args are present for the production codepaths.
    AirbyteEntrypoint.parse_args(args)
    launch(source, sys.argv[1:])


def handle_request(args: List[str]):
    config = get_config_from_args(args)
    is_connector_builder_request = "__command" in config
    source = create_source(config, is_connector_builder_request)
    if is_connector_builder_request:
        handle_connector_builder_request(source, config)
    else:
        handle_connector_request(source, args)


if __name__ == "__main__":
    handle_request(sys.argv[1:])
