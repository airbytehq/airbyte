#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging

from airbyte_cdk.models import (
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    ConnectorSpecification,
    DestinationSyncMode,
    SyncMode,
)

from .conftest import GRAPH_URL, account_url, get_source, mock_fb_account_response


logger = logging.getLogger("airbyte")


account_url_response = {
    "data": [{"id": "page_id", "name": "Airbyte", "instagram_business_account": {"id": "instagram_business_account_id"}}],
    # I'm not sure why we added paging originally, but it's presence can lead to trying to fetch
    # additional business accounts which is not intended because we don't have mocks supplied for query params `after=after`
    # "paging": {"cursors": {"before": "before", "after": "after"}},
}


def mock_api(requests_mock, some_config):
    fb_account_response = mock_fb_account_response("unknown_account", some_config, requests_mock)

    requests_mock.register_uri(
        "GET",
        f"{GRAPH_URL}/me/accounts?" f"access_token={some_config['access_token']}&summary=true",
        [fb_account_response],
    )


def test_check_connection_ok(requests_mock):
    some_config = {"start_date": "2021-01-23T00:00:00Z", "access_token": "unknown_token"}
    mock_api(requests_mock, some_config)
    requests_mock.register_uri("GET", account_url, [{"json": account_url_response}])

    ok, error_msg = get_source(config=some_config, state=None).check_connection(logger, config=some_config)
    assert ok
    assert not error_msg


def test_check_connection_no_date_config(requests_mock):
    some_config = {"start_date": "2021-01-23T00:00:00Z", "access_token": "unknown_token"}
    mock_api(requests_mock, some_config)
    requests_mock.register_uri("GET", account_url, [{"json": account_url_response}])
    some_config.pop("start_date")

    ok, error_msg = get_source(config=some_config, state=None).check_connection(logger, config=some_config)

    assert ok
    assert not error_msg


def test_streams(config):
    streams = get_source(config=config, state=None).streams(config)

    assert len(streams) == 8


def test_spec():
    spec = get_source(config={}, state=None).spec(logger)

    assert isinstance(spec, ConnectorSpecification)


def test_read(config):
    source = get_source(config=config, state=None)
    catalog = ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=AirbyteStream(name="users", json_schema={}, supported_sync_modes=[SyncMode.full_refresh]),
                sync_mode=SyncMode.full_refresh,
                destination_sync_mode=DestinationSyncMode.overwrite,
            )
        ]
    )
    assert source.read(logger, config, catalog)
