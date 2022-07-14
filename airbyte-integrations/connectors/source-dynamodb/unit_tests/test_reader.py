#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from decimal import Decimal

from airbyte_cdk.models import AirbyteStream, SyncMode
from source_dynamodb import reader


def test_check(populate_table, my_reader: reader.Reader) -> None:
    number_tables = my_reader.check()
    assert number_tables == 1


def test_get_streams(populate_table, my_reader: reader.Reader) -> None:

    streams = my_reader.get_streams()
    assert streams == [
        AirbyteStream(
            name="Devices",
            json_schema=my_reader.typed_schema,
            source_defined_cursor=None,
            default_cursor_field=None,
            source_defined_primary_key=None,
            namespace=None,
            supported_sync_modes=[SyncMode.full_refresh],
        ),
        AirbyteStream(
            name="Music",
            json_schema=my_reader.typed_schema,
            source_defined_cursor=None,
            default_cursor_field=None,
            source_defined_primary_key=None,
            namespace=None,
            supported_sync_modes=[SyncMode.full_refresh],
        ),
    ]


def test_read(populate_table, my_reader: reader.Reader) -> None:

    data = my_reader.read(table_name="Devices")
    assert data == [
        {
            "device_id": "10001",
            "datacount": Decimal("1"),
            "info": {
                "temperature5": Decimal("24.69"),
                "temperature4": Decimal("22.96"),
                "temperature3": Decimal("25.6"),
                "info_timestamp": "1612519200",
                "temperature2": Decimal("21.31"),
                "temperature1": Decimal("37.2"),
            },
        },
        {
            "device_id": "10001",
            "datacount": Decimal("2"),
            "info": {
                "temperature5": Decimal("23.18"),
                "temperature4": Decimal("29.11"),
                "temperature3": Decimal("19.2"),
                "info_timestamp": "1612521000",
                "temperature2": Decimal("24.59"),
                "temperature1": Decimal("24.34"),
            },
        },
        {
            "device_id": "10003",
            "datacount": Decimal("1"),
            "info": {
                "temperature5": Decimal("29.54"),
                "temperature4": Decimal("32.02"),
                "temperature3": Decimal("31.24"),
                "info_timestamp": "1612519200",
                "temperature2": Decimal("36.21"),
                "temperature1": Decimal("34.23"),
            },
        },
        {
            "device_id": "10003",
            "datacount": Decimal("2"),
            "info": {
                "temperature5": Decimal("38.87"),
                "temperature4": Decimal("39.32"),
                "temperature3": Decimal("32.62"),
                "info_timestamp": "1612521000",
                "temperature2": Decimal("33.13"),
                "temperature1": Decimal("34.55"),
            },
        },
        {
            "device_id": "10002",
            "datacount": Decimal("1"),
            "info": {
                "temperature5": Decimal("16.17"),
                "temperature4": Decimal("15.95"),
                "temperature3": Decimal("11.2"),
                "info_timestamp": "1612519200",
                "temperature2": Decimal("17.59"),
                "temperature1": Decimal("14.34"),
            },
        },
        {
            "device_id": "10002",
            "datacount": Decimal("2"),
            "info": {
                "temperature5": Decimal("16.21"),
                "temperature4": Decimal("16.45"),
                "temperature3": Decimal("18.91"),
                "info_timestamp": "1612521000",
                "temperature2": Decimal("15.01"),
                "temperature1": Decimal("13.04"),
            },
        },
    ]
