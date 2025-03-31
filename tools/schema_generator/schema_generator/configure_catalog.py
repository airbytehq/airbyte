#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import os

from airbyte_cdk.models import ConfiguredAirbyteCatalog, ConfiguredAirbyteStream, DestinationSyncMode


def configure_catalog():
    record_dict = json.loads(input())
    catalog_streams = record_dict.get("catalog", {}).get("streams", [])
    for stream in catalog_streams:
        stream["json_schema"] = {}
    streams = [
        ConfiguredAirbyteStream(
            stream=stream.get("name"), sync_mode=stream.get("supported_sync_modes", [])[0], destination_sync_mode=DestinationSyncMode.append
        )
        for stream in catalog_streams
        if stream.get("supported_sync_modes")
    ]
    configured_catalog = ConfiguredAirbyteCatalog(streams=streams)

    default_folder = os.path.join(os.getcwd(), "integration_tests")
    if not os.path.exists(default_folder):
        os.mkdir(default_folder)
    output_file_name = os.path.join(default_folder, "configured_catalog.json")
    with open(output_file_name, "w") as outfile:
        # Create a dictionary representation of the configured catalog
        result = {"streams": []}
        for stream in configured_catalog.streams:
            stream_dict = {
                "stream": {
                    "name": stream.stream.name if hasattr(stream.stream, "name") else stream.stream,
                    "supported_sync_modes": ["full_refresh"],
                    "json_schema": {},
                },
                "sync_mode": str(stream.sync_mode),
                "destination_sync_mode": "append",
            }
            result["streams"].append(stream_dict)
        json.dump(result, outfile, indent=2, sort_keys=True)
