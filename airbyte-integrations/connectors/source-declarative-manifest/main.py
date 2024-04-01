#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import pkgutil
import sys
from typing import List

from airbyte_cdk.connector import BaseConnector
from airbyte_cdk.entrypoint import AirbyteEntrypoint, launch
from airbyte_cdk.models import ConnectorSpecification, AirbyteMessage, Type
from airbyte_cdk.sources.declarative.manifest_declarative_source import ManifestDeclarativeSource



def create_manifest(args: List[str]):
    config = BaseConnector.read_config(parsed_args.config)
    if "__injected_declarative_manifest" not in config:
        raise ValueError(
            f"Invalid config: `__injected_declarative_manifest` should be provided at the root of the config but config only has keys {list(config.keys())}"
        )
    return ManifestDeclarativeSource(config.get("__injected_declarative_manifest"))


if __name__ == "__main__":
    args = sys.argv[1:]
    parsed_args = AirbyteEntrypoint.parse_args(args)
    if parsed_args.command == "spec":
        json_spec = pkgutil.get_data("source_declarative_manifest", "spec.json")
        spec_obj = json.loads(json_spec)
        spec = ConnectorSpecification.parse_obj(spec_obj)

        message = AirbyteMessage(type=Type.SPEC, spec=spec)
        print(AirbyteEntrypoint.airbyte_message_to_string(message))
    else:
        source = create_manifest(sys.argv[1:])
        launch(source, sys.argv[1:])
