#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import json
from pathlib import Path
from typing import Any, Mapping

import pytest
from airbyte_cdk.sources.streams import Stream
from source_salesforce.source import SourceSalesforce

HERE = Path(__file__).parent


class Logger:
    def __init__(self):
        self._logs = []

    def save_log(self, msg: str):
        raise Exception("aaaa111")
        self._logs.append(msg)


Logger.warning = Logger.save_log
Logger.error = Logger.save_log


@pytest.fixture(name="input_config")
def parse_input_config():
    with open(HERE.parent / "secrets/config_bulk.json", "r") as file:
        return json.loads(file.read())


def get_stream(input_config: Mapping[str, Any], stream_name: str) -> Stream:
    stream_cls = type("a", (object,), {"name": stream_name})
    configured_stream_cls = type("b", (object,), {"stream": stream_cls()})
    catalog_cls = type("c", (object,), {"streams": [configured_stream_cls()]})
    return SourceSalesforce().streams(input_config, catalog_cls())[0]


def get_any_real_stream(input_config: Mapping[str, Any]) -> Stream:
    return get_stream(input_config, "Account")


def test_not_queryable_stream(input_config):
    stream = get_any_real_stream(input_config)
    stream.create_stream_job()
    raise Exception(stream)

    self.generate_streams(input_config, stream_names, sf)
    ConfiguredAirbyteCatalog
    AirbyteStream
    ConfiguredAirbyteStream(input_config)
    raise Exception(source)

    # def streams(self, config: Mapping[str, Any], catalog: ConfiguredAirbyteCatalog = None) -> List[Stream]:
    #     ConfiguredAirbyteCatalog
    #     sf = self._get_sf_object(config)
    #     stream_names = sf.get_validated_streams(catalog=catalog)
    #     return self.generate_streams(config, stream_names, sf)

    raise Exception("aaaaww")
