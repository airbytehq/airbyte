#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import (
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    ConnectorSpecification,
    DestinationSyncMode,
    SyncMode,
)
from source_pipedrive.source import SourcePipedrive

logger = AirbyteLogger()

PIPEDRIVE_URL_BASE = "https://api.pipedrive.com/v1/"


def test_check_connection(requests_mock, config_token):
    body = {"success": "true", "data": [{"id": 1, "update_time": "2020-10-14T11:30:36.551Z"}]}
    response = setup_response(200, body)
    api_token = config_token["authorization"]["api_token"]
    requests_mock.register_uri("GET", PIPEDRIVE_URL_BASE + "deals?limit=50&api_token=" + api_token, response)

    ok, error = SourcePipedrive().check_connection(logger, config_token)

    assert ok
    assert not error


def test_check_connection_empty():
    config = {}
    ok, error = SourcePipedrive().check_connection(logger, config)

    assert not ok
    assert error


def test_check_connection_error(config_token):
    config_token.pop("replication_start_date")

    ok, error = SourcePipedrive().check_connection(logger, config_token)

    assert not ok
    assert error


def test_check_connection_exception(requests_mock, config_token):
    response = setup_response(400, {})
    api_token = config_token["authorization"]["api_token"]
    requests_mock.register_uri("GET", PIPEDRIVE_URL_BASE + "deals?limit=50&api_token=" + api_token, response)

    ok, error = SourcePipedrive().check_connection(logger, config_token)

    assert not ok
    assert error


def test_streams(config_token):
    streams = SourcePipedrive().streams(config_token)

    assert len(streams) == 12


def setup_response(status, body):
    return [
        {"json": body, "status_code": status},
    ]


def test_spec():
    spec = SourcePipedrive().spec(logger)
    assert isinstance(spec, ConnectorSpecification)


def test_read(config_token):
    source = SourcePipedrive()
    catalog = ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=AirbyteStream(name="deals", json_schema={}),
                sync_mode=SyncMode.full_refresh,
                destination_sync_mode=DestinationSyncMode.overwrite,
            )
        ]
    )
    assert source.read(logger, config_token, catalog)
