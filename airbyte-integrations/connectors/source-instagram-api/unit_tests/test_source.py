# temp file change
#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

from airbyte_cdk.models import (
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    ConnectorSpecification,
    DestinationSyncMode,
    SyncMode,
)


def test_check_connection(source, requests_mock, config, logger):
    requests_mock.register_uri("GET", source.url_base + "/me", [{"json": {"id": "some_id"}}])
    ok, error_msg = source.check_connection(logger, config=config)
    assert ok and not error_msg


def test_streams(source):
    config_mock = MagicMock()
    streams = source.streams(config_mock)
    assert len(streams) == 5


def test_check_connection_empty_config(source, logger):
    ok, error_msg = source.check_connection(logger, config={})
    assert not ok and error_msg


def test_check_connection_exception(source, config, logger, mocker):
    mocker.patch("requests.get", side_effect=Exception)
    ok, error_msg = source.check_connection(logger, config=config)
    assert not ok and error_msg


def test_spec(source, logger):
    spec = source.spec(logger)
    assert isinstance(spec, ConnectorSpecification)


def test_read(source, config, logger):
    catalog = ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=AirbyteStream(name="user", json_schema={}, supported_sync_modes=[SyncMode.full_refresh]),
                sync_mode=SyncMode.full_refresh,
                destination_sync_mode=DestinationSyncMode.overwrite,
            )
        ]
    )
    assert source.read(logger, config, catalog)
