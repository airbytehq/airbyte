#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pytest
from airbyte_cdk.models import (
    AirbyteRecordMessage,
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    SyncMode,
)
from source_acceptance_test.utils.asserts import verify_records_schema


@pytest.fixture(name="record_schema")
def record_schema_fixture():
    return {
        "properties": {
            "text_or_null": {"type": ["null", "string"]},
            "number_or_null": {"type": ["null", "number"]},
            "integer_or_null": {"type": ["null", "integer"]},
            "text": {"type": ["string"]},
            "number": {"type": ["number"]},
        },
        "type": ["null", "object"],
    }


@pytest.fixture(name="configured_catalog")
def catalog_fixture(request, record_schema) -> ConfiguredAirbyteCatalog:
    record_schema = request.param if hasattr(request, "param") else record_schema
    stream = ConfiguredAirbyteStream(
        stream=AirbyteStream(name="my_stream", json_schema=record_schema, supported_sync_modes=[SyncMode.full_refresh]),
        sync_mode=SyncMode.full_refresh,
        destination_sync_mode=DestinationSyncMode.append,
    )

    return ConfiguredAirbyteCatalog(streams=[stream])


def test_verify_records_schema(configured_catalog: ConfiguredAirbyteCatalog):
    """Test that correct records returned as records with errors, and verify specific error messages"""
    records = [
        {
            "text_or_null": 123,  # wrong format
            "number_or_null": 10.3,
            "text": "text",
            "number": "text",  # wrong format
        },
        {
            "text_or_null": "test",
            "number_or_null": None,
            "text": None,  # wrong value
            "number": None,  # wrong value
        },
        {
            "text_or_null": None,
            "number_or_null": None,
            "text": "text",
            "number": 77,
        },
        {
            "text_or_null": None,
            "number_or_null": None,
            "text": "text",
            "number": "text",  # wrong format
        },
        {"text_or_null": None, "number_or_null": None, "text": "text", "number": 10.3, "integer": 1},
        {"text_or_null": None, "number_or_null": None, "text": "text", "number": 10.3, "integer_or_null": 1.0},  # wrong format
    ]

    records = [AirbyteRecordMessage(stream="my_stream", data=record, emitted_at=0) for record in records]

    streams_with_errors = verify_records_schema(records, configured_catalog)
    errors = [error.message for error in streams_with_errors["my_stream"].values()]

    assert "my_stream" in streams_with_errors
    assert len(streams_with_errors) == 1, "only one stream"
    assert len(streams_with_errors["my_stream"]) == 4, "only first error for each field"
    assert errors == [
        "123 is not of type 'null', 'string'",
        "'text' is not of type 'number'",
        "None is not of type 'string'",
        "1.0 is not of type 'null', 'integer'",
    ]


@pytest.mark.parametrize(
    "record, configured_catalog, valid",
    [
        # Send null data
        ({"a": None}, {"type": "object", "properties": {"a": {"type": "string", "format": "time"}}}, False),
        # time
        ({"a": "sdf"}, {"type": "object", "properties": {"a": {"type": "string", "format": "time"}}}, False),
        ({"a": "12:00"}, {"type": "object", "properties": {"a": {"type": "string", "format": "time"}}}, False),
        ({"a": "12:00:90"}, {"type": "object", "properties": {"a": {"type": "string", "format": "time"}}}, False),
        ({"a": "12:00:22"}, {"type": "object", "properties": {"a": {"type": "string", "format": "time"}}}, True),
        # date
        ({"a": "12:00:90"}, {"type": "object", "properties": {"a": {"type": "string", "format": "date"}}}, False),
        ({"a": "2020-12-20"}, {"type": "object", "properties": {"a": {"type": "string", "format": "date"}}}, True),
        ({"a": "2020-20-20"}, {"type": "object", "properties": {"a": {"type": "string", "format": "date"}}}, False),
        # date-time
        # full date-time format with timezone only valid, according to https://datatracker.ietf.org/doc/html/rfc3339#section-5.6
        ({"a": "12:11:00"}, {"type": "object", "properties": {"a": {"type": "string", "format": "date-time"}}}, False),
        ({"a": "2018-11-13 20:20:39"}, {"type": "object", "properties": {"a": {"type": "string", "format": "date-time"}}}, True),
        ({"a": "2021-08-10T12:43:15"}, {"type": "object", "properties": {"a": {"type": "string", "format": "date-time"}}}, True),
        ({"a": "2021-08-10T12:43:15Z"}, {"type": "object", "properties": {"a": {"type": "string", "format": "date-time"}}}, True),
        ({"a": "2018-11-13T20:20:39+00:00"}, {"type": "object", "properties": {"a": {"type": "string", "format": "date-time"}}}, True),
        ({"a": "2018-21-13T20:20:39+00:00"}, {"type": "object", "properties": {"a": {"type": "string", "format": "date-time"}}}, False),
        # This is valid for postgres sql but not valid for bigquery
        ({"a": "2014-09-27 9:35z"}, {"type": "object", "properties": {"a": {"type": "string", "format": "date-time"}}}, False),
        # Seconds are obligatory for bigquery timestamp
        ({"a": "2014-09-27 9:35"}, {"type": "object", "properties": {"a": {"type": "string", "format": "date-time"}}}, False),
        ({"a": "2014-09-27 9:35:0z"}, {"type": "object", "properties": {"a": {"type": "string", "format": "date-time"}}}, True),
        # email
        ({"a": "2018-11-13 20:20:39"}, {"type": "object", "properties": {"a": {"type": "string", "format": "email"}}}, False),
        ({"a": "hi@example.com"}, {"type": "object", "properties": {"a": {"type": "string", "format": "email"}}}, True),
        ({"a": "Пример@example.com"}, {"type": "object", "properties": {"a": {"type": "string", "format": "email"}}}, True),
        ({"a": "写电子邮件@子邮件"}, {"type": "object", "properties": {"a": {"type": "string", "format": "email"}}}, True),
        # hostname
        ({"a": "2018-11-13 20:20:39"}, {"type": "object", "properties": {"a": {"type": "string", "format": "hostname"}}}, False),
        ({"a": "hi@example.com"}, {"type": "object", "properties": {"a": {"type": "string", "format": "hostname"}}}, False),
        ({"a": "localhost"}, {"type": "object", "properties": {"a": {"type": "string", "format": "hostname"}}}, True),
        ({"a": "example.com"}, {"type": "object", "properties": {"a": {"type": "string", "format": "hostname"}}}, True),
        # ipv4
        ({"a": "example.com"}, {"type": "object", "properties": {"a": {"type": "string", "format": "ipv4"}}}, False),
        ({"a": "0.0.0.1000"}, {"type": "object", "properties": {"a": {"type": "string", "format": "ipv4"}}}, False),
        ({"a": "0.0.0.0"}, {"type": "object", "properties": {"a": {"type": "string", "format": "ipv4"}}}, True),
        # ipv6
        ({"a": "example.com"}, {"type": "object", "properties": {"a": {"type": "string", "format": "ipv6"}}}, False),
        ({"a": "1080:0:0:0:8:800:200C:417A"}, {"type": "object", "properties": {"a": {"type": "string", "format": "ipv6"}}}, True),
        ({"a": "::1"}, {"type": "object", "properties": {"a": {"type": "string", "format": "ipv6"}}}, True),
        ({"a": "::"}, {"type": "object", "properties": {"a": {"type": "string", "format": "ipv6"}}}, True),
    ],
    indirect=["configured_catalog"],
)
def test_validate_records_format(record, configured_catalog, valid):
    records = [AirbyteRecordMessage(stream="my_stream", data=record, emitted_at=0)]
    streams_with_errors = verify_records_schema(records, configured_catalog)
    if valid:
        assert not streams_with_errors
    else:
        assert streams_with_errors, f"Record {record} should produce errors against {configured_catalog.streams[0].stream.json_schema}"
