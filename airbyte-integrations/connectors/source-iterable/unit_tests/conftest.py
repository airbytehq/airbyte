#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pytest
from airbyte_cdk.models import AirbyteStream, ConfiguredAirbyteCatalog, ConfiguredAirbyteStream


@pytest.fixture
def catalog(request):
    return ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=AirbyteStream(name=request.param, json_schema={}, supported_sync_modes=["full_refresh"]),
                sync_mode="full_refresh",
                destination_sync_mode="append",
            )
        ]
    )


@pytest.fixture(name="config")
def config_fixture():
    return {"api_key": 123, "start_date": "2019-10-10T00:00:00"}


@pytest.fixture()
def mock_lists_resp(mocker):
    mocker.patch("source_iterable.streams.Lists.read_records", return_value=iter([{"id": 1}, {"id": 2}]))
