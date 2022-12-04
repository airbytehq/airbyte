import json
import os

from airbyte_cdk.models import ConfiguredAirbyteCatalog, AirbyteMessage, ConfiguredAirbyteStream, DestinationSyncMode


def configure_catalog():
    record = AirbyteMessage.parse_raw(input())
    for stream in record.catalog.streams:
        stream.json_schema = {}
    streams = [
        ConfiguredAirbyteStream(stream=stream, sync_mode=stream.supported_sync_modes[0], destination_sync_mode=DestinationSyncMode.append)
        for stream in record.catalog.streams
    ]
    configured_catalog = ConfiguredAirbyteCatalog(streams=streams)

    default_folder = os.path.join(os.getcwd(), "integration_tests")
    if not os.path.exists(default_folder):
        os.mkdir(default_folder)
    output_file_name = os.path.join(default_folder, "configured_catalog.json")
    with open(output_file_name, "w") as outfile:
        json.dump(json.loads(configured_catalog.json()), outfile, indent=2, sort_keys=True)
