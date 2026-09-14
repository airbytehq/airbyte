#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#


import pytest

from .conftest import get_source


_CONFIG = {
    "refresh_token": "test_refresh_token",
    "lwa_app_id": "test_lwa_app_id",
    "lwa_client_secret": "test_lwa_client_secret",
    "replication_start_date": "2023-01-01T00:00:00Z",
    "replication_end_date": "2023-01-30T00:00:00Z",
    "aws_environment": "PRODUCTION",
    "region": "US",
    "account_type": "Seller",
    "marketplace_id": "ATVPDKIKX0DER",
}

# The All Orders flat-file reports emit one row per order item, and Amazon does not include
# order-item-id in the delivered report, so no column (or combination of columns) can serve as a
# reliable primary key. Declaring `amazon-order-id` as the primary key collapsed every multi-item
# order to a single row in Incremental | Append + Deduped mode, silently losing data.
STREAMS_WITHOUT_PRIMARY_KEY = (
    "GET_FLAT_FILE_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL",
    "GET_FLAT_FILE_ALL_ORDERS_DATA_BY_LAST_UPDATE_GENERAL",
)


@pytest.mark.parametrize("stream_name", STREAMS_WITHOUT_PRIMARY_KEY)
def test_all_orders_streams_have_no_primary_key(stream_name: str) -> None:
    source = get_source(_CONFIG)
    streams = [stream for stream in source.streams(source._config) if stream.name == stream_name]
    assert streams, f"Stream {stream_name} not found"
    airbyte_stream = streams[0].as_airbyte_stream()
    assert not airbyte_stream.source_defined_primary_key
