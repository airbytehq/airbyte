#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys
from typing import List

from airbyte_cdk.connector import BaseConnector
from airbyte_cdk.entrypoint import AirbyteEntrypoint, launch
from airbyte_cdk.sources.declarative.manifest_declarative_source import ManifestDeclarativeSource


def create_manifest(args: List[str]):
    parsed_args = AirbyteEntrypoint.parse_args(args)
    if parsed_args.command == "spec":
        raise ValueError("spec command is not supported for injected declarative manifest")

    config = BaseConnector.read_config(parsed_args.config)
    if "__injected_declarative_manifest" not in config:
        raise ValueError(
            f"Invalid config: `__injected_declarative_manifest` should be provided at the root of the config but config only has keys {list(config.keys())}"
        )
    return ManifestDeclarativeSource(config.get("__injected_declarative_manifest"))


if __name__ == "__main__":
    source = create_manifest(sys.argv[1:])
    launch(source, sys.argv[1:])
