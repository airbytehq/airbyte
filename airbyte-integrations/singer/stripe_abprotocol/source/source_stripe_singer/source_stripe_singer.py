from airbyte_protocol import Source
from airbyte_protocol import AirbyteSpec
from airbyte_protocol import AirbyteCheckResponse
from airbyte_protocol import AirbyteCatalog
from airbyte_protocol import AirbyteMessage
import requests
from typing import Generator
from base_singer import SingerHelper
import sys
import json


def is_field_metadata(metadata):
    if len(metadata.get("breadcrumb")) != 2:
        return False
    else:
        return metadata.get("breadcrumb")[0] != "property"


class SourceStripeSinger(Source):
    def __init__(self):
        pass

    def spec(self) -> AirbyteSpec:
        return SingerHelper.spec_from_file('/airbyte/stripe-files/spec.json')

    def check(self, logger, config_container) -> AirbyteCheckResponse:
        json_config = config_container.rendered_config
        r = requests.get('https://api.stripe.com/v1/customers', auth=(json_config['client_secret'], ''))

        return AirbyteCheckResponse(r.status_code == 200, {})

    def discover(self, logger, config_container) -> AirbyteCatalog:
        catalogs = SingerHelper.get_catalogs(logger, f"tap-stripe --config {config_container.rendered_config_path} --discover")
        return catalogs.airbyte_catalog

    def read(self, logger, config_container, catalog_path, state=None) -> Generator[AirbyteMessage, None, None]:
        masked_airbyte_catalog = self.read_config(catalog_path)
        discovered_singer_catalog = SingerHelper.get_catalogs(logger, f"tap-stripe --config {config_container.rendered_config_path} --discover").singer_catalog

        combined_catalog_path = "/mount/rendered_catalog.json"
        masked_singer_streams = []

        stream_to_airbyte_schema = {}
        for stream in masked_airbyte_catalog["streams"]:
            stream_to_airbyte_schema[stream.get("name")] = stream

        for singer_stream in discovered_singer_catalog.get("streams"):
            if singer_stream.get("stream") in stream_to_airbyte_schema:
                new_metadatas = []
                metadatas = singer_stream.get("metadata")
                for metadata in metadatas:
                    new_metadata = metadata
                    new_metadata["metadata"]["selected"] = True
                    if not is_field_metadata(new_metadata):
                        new_metadata["metadata"]["forced-replication-method"] = "FULL_TABLE"
                    new_metadatas += [new_metadata]
                singer_stream["metadata"] = new_metadatas

            masked_singer_streams += [singer_stream]

        combined_catalog = {"streams": masked_singer_streams}
        with open(combined_catalog_path, 'w') as fh:
            fh.write(json.dumps(combined_catalog))

        # todo: figure out how to make this easier to consume for new implementers

        if state:
            return SingerHelper.read(logger, f"tap-stripe --config {config_container.rendered_config_path} --catalog {combined_catalog_path} --state {state}")
        else:
            return SingerHelper.read(logger, f"tap-stripe --config {config_container.rendered_config_path} --catalog {combined_catalog_path}")
