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
from source_instagram.source import SourceInstagram

logger = logging.getLogger("airbyte")


def test_check_connection_ok(api, some_config):
    ok, error_msg = SourceInstagram().check_connection(logger, config=some_config)

    assert ok
    assert not error_msg


def test_check_connection_empty_config(api):
    config = {}
    ok, error_msg = SourceInstagram().check_connection(logger, config=config)

    assert not ok
    assert error_msg


def test_check_connection_invalid_config_future_date(api, some_config_future_date):
    ok, error_msg = SourceInstagram().check_connection(logger, config=some_config_future_date)

    assert not ok
    assert error_msg


def test_check_connection_no_date_config(api, some_config):
    some_config.pop("start_date")
    ok, error_msg = SourceInstagram().check_connection(logger, config=some_config)

    assert ok
    assert not error_msg


def test_check_connection_exception(api, config):
    api.side_effect = RuntimeError("Something went wrong!")
    ok, error_msg = SourceInstagram().check_connection(logger, config=config)

    assert not ok
    assert error_msg


def test_streams(api, config):
    streams = SourceInstagram().streams(config)

    assert len(streams) == 7


def test_spec():
    spec = SourceInstagram().spec()

    assert isinstance(spec, ConnectorSpecification)


def test_read(config):
    source = SourceInstagram()
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
