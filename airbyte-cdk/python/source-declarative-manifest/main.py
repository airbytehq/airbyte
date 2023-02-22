#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.connector import BaseConnector
from airbyte_cdk.entrypoint import AirbyteEntrypoint, launch
from airbyte_cdk.sources.declarative.manifest_declarative_source import ManifestDeclarativeSource

if __name__ == "__main__":
    args = AirbyteEntrypoint.parse_args(sys.argv[1:])
    config = BaseConnector.read_config(args.config)
    if "__injected_declarative_manifest" not in config:
        raise ValueError(
            f"Invalid config: `__injected_declarative_manifest` should be provided at the root of the config but config only has keys {list(config.keys())}"
        )
    source = ManifestDeclarativeSource(config.get("__injected_declarative_manifest"))
    launch(source, sys.argv[1:])
