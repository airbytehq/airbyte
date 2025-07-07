#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import logging

from source_instagram.source import SourceInstagram

from airbyte_cdk.connector_builder.connector_builder_handler import resolve_manifest
from airbyte_cdk.models import (
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    ConnectorSpecification,
    DestinationSyncMode,
    SyncMode,
)


logger = logging.getLogger("airbyte")

GRAPH_URL = resolve_manifest(source=SourceInstagram(config={}, catalog=None, state=None)).record.data["manifest"]["definitions"][
    "base_requester"
]["url_base"]

account_url = f"{GRAPH_URL}/me/accounts?fields=id%2Cinstagram_business_account"


account_url_response = {
    "data": [{"id": "page_id", "name": "Airbyte", "instagram_business_account": {"id": "instagram_business_account_id"}}],
    "paging": {"cursors": {"before": "before", "after": "after"}},
}


def test_check_connection_ok(api, requests_mock, some_config):
    requests_mock.register_uri("GET", account_url, [{"json": account_url_response}])
    ok, error_msg = SourceInstagram(config=some_config, catalog=None, state=None).check_connection(logger, config=some_config)
    assert ok
    assert not error_msg


def test_check_connection_empty_config(api):
    config = {}
    ok, error_msg = SourceInstagram(config=config, catalog=None, state=None).check_connection(logger, config=config)

    assert not ok
    assert error_msg


def test_check_connection_invalid_config_future_date(api, some_config_future_date):
    ok, error_msg = SourceInstagram(config=some_config_future_date, catalog=None, state=None).check_connection(
        logger, config=some_config_future_date
    )

    assert not ok
    assert error_msg


def test_check_connection_no_date_config(api, requests_mock, some_config):
    requests_mock.register_uri("GET", account_url, [{"json": account_url_response}])
    some_config.pop("start_date")
    ok, error_msg = SourceInstagram(config=some_config, catalog=None, state=None).check_connection(logger, config=some_config)

    assert ok
    assert not error_msg


def test_check_connection_exception(api, config):
    api.side_effect = RuntimeError("Something went wrong!")
    ok, error_msg = SourceInstagram(config=config, catalog=None, state=None).check_connection(logger, config=config)

    assert not ok
    assert error_msg


def test_streams(api, config):
    streams = SourceInstagram(config=config, catalog=None, state=None).streams(config)

    assert len(streams) == 8


def test_spec():
    spec = SourceInstagram(config={}, catalog=None, state=None).spec(logger)

    assert isinstance(spec, ConnectorSpecification)


def test_read(config):
    source = SourceInstagram(config=config, catalog=None, state=None)
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
