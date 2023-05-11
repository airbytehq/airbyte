#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import pytest
import requests
from airbyte_cdk import AirbyteLogger
from airbyte_cdk.models import AirbyteStream, ConfiguredAirbyteCatalog, ConfiguredAirbyteStream, DestinationSyncMode, SyncMode


@pytest.fixture
def logger():
    return AirbyteLogger()


@pytest.fixture
def basic_config():
    return {"shop": "test_shop", "credentials": {"auth_method": "api_password", "api_password": "api_password"}}


@pytest.fixture
def catalog_with_streams():
    def _catalog_with_streams(names):
        streams = []
        for name in names:
            streams.append(
                ConfiguredAirbyteStream(
                    stream=AirbyteStream(name=name, json_schema={"type": "object"}),
                    sync_mode=SyncMode.full_refresh,
                    destination_sync_mode=DestinationSyncMode.overwrite,
                )
            )
        return ConfiguredAirbyteCatalog(streams=streams)

    return _catalog_with_streams


@pytest.fixture
def response_with_bad_json():
    bad_json_str = '{"customers": [{ "field1": "test1", "field2": }]}'
    response = requests.Response()
    response.status_code = 200
    response._content = bad_json_str.encode("utf-8")
    return response
