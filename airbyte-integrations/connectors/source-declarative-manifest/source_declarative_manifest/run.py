#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import argparse
import json
import pkgutil
import sys
from typing import List

from airbyte_cdk.connector import BaseConnector
from airbyte_cdk.entrypoint import AirbyteEntrypoint, launch
from airbyte_cdk.models import AirbyteMessage, ConnectorSpecification, Type
from airbyte_cdk.sources.declarative.manifest_declarative_source import ManifestDeclarativeSource


def handle_command(args: List[str]) -> None:
    """Overrides the spec command to return the generalized spec for the declarative manifest source.

    This is different from a typical low-code, but built and published separately source built as a ManifestDeclarativeSource,
    because that will have a spec method that returns the spec for that specific source. Other than spec,
    the generalized connector behaves the same as any other, since the manifest is provided in the config.
    """
    if args[0] == "spec":
        json_spec = pkgutil.get_data("source_declarative_manifest", "spec.json")
        spec_obj = json.loads(json_spec)
        spec = ConnectorSpecification.parse_obj(spec_obj)

        message = AirbyteMessage(type=Type.SPEC, spec=spec)
        print(AirbyteEntrypoint.airbyte_message_to_string(message))
    else:
        source = create_manifest(args)
        launch(source, sys.argv[1:])


def create_manifest(args: List[str]) -> ManifestDeclarativeSource:
    """Creates the source with the injected config.

    This essentially does what other low-code sources do at build time, but at runtime,
    with a user-provided manifest in the config. This better reflects what happens in the
    connector builder.
    """
    parsed_args = AirbyteEntrypoint.parse_args(args)
    config = BaseConnector.read_config(parsed_args.config)
    if "__injected_declarative_manifest" not in config:
        raise ValueError(
            f"Invalid config: `__injected_declarative_manifest` should be provided at the root of the config but config only has keys {list(config.keys())}"
        )
    return ManifestDeclarativeSource(config.get("__injected_declarative_manifest"))


def run():
    args = sys.argv[1:]
    handle_command(args)
