#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from unittest import mock
from unittest.mock import MagicMock

from source_microsoft_dataverse.dataverse import AirbyteType
from source_microsoft_dataverse.source import SourceMicrosoftDataverse
from source_microsoft_dataverse.streams import IncrementalMicrosoftDataverseStream, MicrosoftDataverseStream

from airbyte_cdk.models import SyncMode


@mock.patch("source_microsoft_dataverse.source.do_request")
def test_check_connection(mock_request):
    mock_request.return_value.raise_for_status = lambda: ()
    source = SourceMicrosoftDataverse()
    logger_mock, config_mock = MagicMock(), MagicMock()
    assert source.check_connection(logger_mock, config_mock) == (True, None)


@mock.patch("source_microsoft_dataverse.source.get_auth")
@mock.patch("source_microsoft_dataverse.source.do_request")
def test_streams_incremental(mock_get_auth, mock_request):
    streams = MagicMock()
    streams.sync_mode = SyncMode.incremental
    streams.stream.name = "test"

    catalog = MagicMock()

    catalog.streams = [streams]

    config_mock = MagicMock()
    source = SourceMicrosoftDataverse()
    source.catalogs = catalog

    streams = source.streams(config_mock)

    expected_streams_number = 1
    assert len(streams) == expected_streams_number
    assert isinstance(streams[0], IncrementalMicrosoftDataverseStream)
    assert streams[0].name == "test"


@mock.patch("source_microsoft_dataverse.source.get_auth")
@mock.patch("source_microsoft_dataverse.source.do_request")
def test_streams_full_refresh(mock_get_auth, mock_request):
    streams = MagicMock()
    streams.sync_mode = SyncMode.full_refresh
    streams.stream.name = "test"

    catalog = MagicMock()

    catalog.streams = [streams]

    config_mock = MagicMock()
    source = SourceMicrosoftDataverse()
    source.catalogs = catalog

    streams = source.streams(config_mock)

    expected_streams_number = 1
    assert len(streams) == expected_streams_number
    assert isinstance(streams[0], MicrosoftDataverseStream)
    assert streams[0].name == "test"


@mock.patch("source_microsoft_dataverse.source.do_request")
def test_discover_incremental(mock_request):
    result_json = json.loads(
        """
        {
            "value": [
                {
                    "LogicalName": "stream",
                    "PrimaryIdAttribute": "primary",
                    "ChangeTrackingEnabled": true,
                    "CanChangeTrackingBeEnabled": {
                        "Value": true
                    },
                    "Attributes": [
                        {
                            "LogicalName": "test",
                            "AttributeType": "String"
                        },
                        {
                            "LogicalName": "modifiedon",
                            "AttributeType": "DateTime"
                        }
                    ]
                }
            ]
        }
    """
    )

    mock_request.return_value.status.return_value = 200
    mock_request.return_value.json.return_value = result_json

    source = SourceMicrosoftDataverse()
    logger_mock, config_mock = MagicMock(), MagicMock()

    catalog = source.discover(logger_mock, config_mock)

    assert not {"modifiedon"} ^ set(catalog.streams[0].default_cursor_field)
    assert not {SyncMode.full_refresh, SyncMode.incremental} ^ set(catalog.streams[0].supported_sync_modes)
    assert not {"primary"} ^ set(catalog.streams[0].source_defined_primary_key[0])
    assert catalog.streams[0].json_schema["properties"]["test"] == AirbyteType.String.value


@mock.patch("source_microsoft_dataverse.source.do_request")
def test_discover_full_refresh(mock_request):
    result_json = json.loads(
        """
        {
            "value": [
                {
                    "LogicalName": "stream",
                    "PrimaryIdAttribute": "primary",
                    "ChangeTrackingEnabled": false,
                    "CanChangeTrackingBeEnabled": {
                        "Value": false
                    },
                    "Attributes": [
                        {
                            "LogicalName": "test",
                            "AttributeType": "String"
                        }
                    ]
                }
            ]
        }
    """
    )

    mock_request.return_value.status.return_value = 200
    mock_request.return_value.json.return_value = result_json

    source = SourceMicrosoftDataverse()
    logger_mock, config_mock = MagicMock(), MagicMock()

    catalog = source.discover(logger_mock, config_mock)

    assert catalog.streams[0].default_cursor_field is None or len(catalog.streams[0].default_cursor_field) == 0
    assert not {SyncMode.full_refresh} ^ set(catalog.streams[0].supported_sync_modes)
    assert not {"primary"} ^ set(catalog.streams[0].source_defined_primary_key[0])
    assert catalog.streams[0].json_schema["properties"]["test"] == AirbyteType.String.value
