#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import pkgutil
import sys


from airbyte_cdk.entrypoint import AirbyteEntrypoint, launch
from airbyte_cdk.models import ConnectorSpecification, AirbyteMessage, Type

from source_declarative_manifest.run import run

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
        run()
