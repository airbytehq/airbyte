#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
import responses
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
    responses.get("https://api.iterable.com/api/lists", json={"lists": [{"id": 1}, {"id": 2}]})


@pytest.fixture(name="lists_stream")
def lists_stream():
    # local imports
    from source_iterable.streams import Lists

    # return the instance of the stream so we could make global tests on it,
    # to cover the different `should_retry` logic
    return Lists(authenticator=None)


@pytest.fixture(autouse=True)
def mock_sleep(mocker):
    mocker.patch("time.sleep")
