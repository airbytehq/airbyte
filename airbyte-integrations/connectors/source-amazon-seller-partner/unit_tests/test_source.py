#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import logging
from datetime import datetime, timedelta
from pathlib import Path

import pytest
import yaml
from freezegun import freeze_time

from airbyte_cdk.models import AirbyteStream, ConfiguredAirbyteCatalog, ConfiguredAirbyteStream, DestinationSyncMode, Status, SyncMode
from airbyte_cdk.sources.streams.concurrent.default_stream import DefaultStream

from .conftest import get_source


logger = logging.getLogger("airbyte")


@pytest.fixture
def connector_config_with_report_options():
    return {
        "replication_start_date": "2017-01-25T00:00:00Z",
        "replication_end_date": "2017-02-25T00:00:00Z",
        "refresh_token": "Atzr|IwEBIP-abc123",
        "lwa_app_id": "amzn1.application-oa2-client.abc123",
        "lwa_client_secret": "abc123",
        "aws_environment": "SANDBOX",
        "account_type": "Seller",
        "region": "US",
        "report_options_list": [
            {
                "report_name": "GET_FBA_FULFILLMENT_CUSTOMER_RETURNS_DATA",
                "stream_name": "GET_FBA_FULFILLMENT_CUSTOMER_RETURNS_DATA",
                "options_list": [
                    {"option_name": "some_name_1", "option_value": "some_value_1"},
                    {"option_name": "some_name_2", "option_value": "some_value_2"},
                ],
            },
        ],
    }


@pytest.fixture
def connector_vendor_config_with_report_options():
    return {
        "replication_start_date": "2017-01-25T00:00:00Z",
        "replication_end_date": "2017-02-25T00:00:00Z",
        "refresh_token": "Atzr|IwEBIP-abc123",
        "lwa_app_id": "amzn1.application-oa2-client.abc123",
        "lwa_client_secret": "abc123",
        "aws_environment": "SANDBOX",
        "account_type": "Vendor",
        "region": "US",
        "report_options_list": [
            {
                "stream_name": "GET_FBA_FULFILLMENT_CUSTOMER_RETURNS_DATA",
                "options_list": [
                    {"option_name": "some_name_1", "option_value": "some_value_1"},
                    {"option_name": "some_name_2", "option_value": "some_value_2"},
                ],
            },
        ],
    }


@pytest.fixture
def connector_config_without_start_date():
    return {
        "refresh_token": "Atzr|IwEBIP-abc123",
        "lwa_app_id": "amzn1.application-oa2-client.abc123",
        "lwa_client_secret": "abc123",
        "aws_environment": "SANDBOX",
        "region": "US",
    }


@freeze_time("2017-02-25T00:00:00Z")
def test_check_connection_with_orders_stop_iteration(requests_mock, connector_config_with_report_options):
    requests_mock.register_uri(
        "POST",
        "https://api.amazon.com/auth/o2/token",
        status_code=200,
        json={"access_token": "access_token", "expires_in": "3600"},
    )
    requests_mock.register_uri(
        "GET",
        "https://sandbox.sellingpartnerapi-na.amazon.com/orders/v0/orders",
        status_code=201,
        json={"payload": {"Orders": []}},
    )
    config = dict(connector_config_with_report_options)
    source = get_source(config, config_path=None)
    result = source.check(logger, source._config)
    assert result.status == Status.SUCCEEDED
    assert result.message is None


@freeze_time("2017-02-25T00:00:00Z")
def test_check_connection_with_orders(requests_mock, connector_config_with_report_options):
    requests_mock.register_uri(
        "POST",
        "https://api.amazon.com/auth/o2/token",
        status_code=200,
        json={"access_token": "access_token", "expires_in": "3600"},
    )
    requests_mock.register_uri(
        "GET",
        "https://sandbox.sellingpartnerapi-na.amazon.com/orders/v0/orders",
        status_code=200,
        json={"payload": {"Orders": [{"LastUpdateDate": "2024-06-02T00:00:00Z"}]}},
    )
    source = get_source(connector_config_with_report_options)
    result = source.check(logger, source._config)
    assert result.status == Status.SUCCEEDED
    assert result.message is None


@freeze_time("2017-02-25T00:00:00Z")
def test_check_connection_vendor_account(requests_mock, connector_vendor_config_with_report_options):
    """Vendor accounts should pass the check using a vendor stream (not the seller Orders endpoint)."""
    requests_mock.register_uri(
        "POST",
        "https://api.amazon.com/auth/o2/token",
        status_code=200,
        json={"access_token": "access_token", "expires_in": "3600"},
    )
    requests_mock.register_uri(
        "GET",
        "https://sandbox.sellingpartnerapi-na.amazon.com/vendor/orders/v1/purchaseOrders",
        status_code=200,
        json={"payload": {"orders": [{"purchaseOrderDate": "2017-02-25T00:00:00Z"}]}},
    )
    config = dict(connector_vendor_config_with_report_options)
    source = get_source(config, config_path=None)
    result = source.check(logger, source._config)
    assert result.status == Status.SUCCEEDED
    assert result.message is None


# TODO: Renable this test once this type of validation is supported
# def test_config_report_options_validation_error_duplicated_streams(connector_config_with_report_options):
#     connector_config_with_report_options["report_options_list"].append(connector_config_with_report_options["report_options_list"][0])
#     with pytest.raises(ValueError) as e:
#         get_source(connector_config_with_report_options).streams(connector_config_with_report_options)
#     assert "Condition evaluated to False" in str(e.value)

# TODO: Renable this test once this type of validation is supported
# def test_config_report_options_validation_error_duplicated_options(connector_config_with_report_options):
#     connector_config_with_report_options["report_options_list"][0]["options_list"].append(
#         connector_config_with_report_options["report_options_list"][0]["options_list"][0]
#     )
#     with pytest.raises(ValueError) as e:
#         get_source(connector_config_with_report_options).streams(connector_config_with_report_options)
#     assert "Condition evaluated to False" in str(e.value)


def test_streams(connector_config_without_start_date):
    for stream in get_source(connector_config_without_start_date).streams(connector_config_without_start_date):
        assert isinstance(stream, DefaultStream)


def test_streams_count_seller(connector_config_without_start_date, monkeypatch):
    streams = get_source(connector_config_without_start_date).streams(connector_config_without_start_date)
    assert len(streams) == 46


def test_streams_count_vendor(monkeypatch):
    config = {
        "refresh_token": "Atzr|IwEBIP-abc123",
        "lwa_app_id": "amzn1.application-oa2-client.abc123",
        "lwa_client_secret": "abc123",
        "aws_environment": "SANDBOX",
        "region": "US",
        "account_type": "Vendor",
    }
    streams = get_source(config).streams(config)
    assert len(streams) == 49


# TODO: Renable this test once this type of validation is supported
# @pytest.mark.parametrize(
#     ("config", "should_raise"),
#     (
#         ({"replication_start_date": "2022-09-01T00:00:00Z", "replication_end_date": "2022-08-01T00:00:00Z"}, True),
#         ({"replication_start_date": "2022-09-01T00:00:00Z", "replication_end_date": "2022-10-01T00:00:00Z"}, False),
#         ({"replication_end_date": "2022-10-01T00:00:00Z"}, False),
#         ({"replication_start_date": "2022-09-01T00:00:00Z"}, False),
#         ({}, False),
#     ),
# )
# def test_replication_dates_validation(config, should_raise):
#     if should_raise:
#         with pytest.raises(AmazonConfigException) as e:
#             SourceAmazonSellerPartner(
#                 config=config,
#                 catalog=None,
#                 state=None,
#             ).validate_replication_dates(config)
#         assert e.value.message == "End Date should be greater than or equal to Start Date"
#     else:
#         assert (
#             SourceAmazonSellerPartner(
#                 config=config,
#                 catalog=None,
#                 state=None,
#             ).validate_replication_dates(config)
#             is None
#         )


VENDOR_ONLY_STREAM_NAMES = [
    "VendorDirectFulfillmentShipping",
    "VendorOrders",
    "VendorOrdersStatus",
    "GET_VENDOR_FORECASTING_FRESH_REPORT",
    "GET_VENDOR_FORECASTING_RETAIL_REPORT",
    "GET_VENDOR_SALES_REPORT",
    "GET_VENDOR_INVENTORY_REPORT",
]

SELLER_ONLY_STREAM_NAMES = [
    "Orders",
    "OrderItems",
    "ListFinancialEventGroups",
    "ListFinancialEvents",
]


def test_vendor_streams_excluded_for_seller():
    config = {
        "refresh_token": "Atzr|IwEBIP-abc123",
        "lwa_app_id": "amzn1.application-oa2-client.abc123",
        "lwa_client_secret": "abc123",
        "aws_environment": "SANDBOX",
        "region": "US",
        "account_type": "Seller",
    }
    stream_names = [s.name for s in get_source(config).streams(config)]
    for vendor_stream in VENDOR_ONLY_STREAM_NAMES:
        assert vendor_stream not in stream_names, f"{vendor_stream} should not appear for Seller accounts"


def test_vendor_streams_included_for_vendor():
    config = {
        "refresh_token": "Atzr|IwEBIP-abc123",
        "lwa_app_id": "amzn1.application-oa2-client.abc123",
        "lwa_client_secret": "abc123",
        "aws_environment": "SANDBOX",
        "region": "US",
        "account_type": "Vendor",
    }
    stream_names = [s.name for s in get_source(config).streams(config)]
    for vendor_stream in VENDOR_ONLY_STREAM_NAMES:
        assert vendor_stream in stream_names, f"{vendor_stream} should appear for Vendor accounts"


def test_vendor_streams_excluded_when_account_type_missing():
    config = {
        "refresh_token": "Atzr|IwEBIP-abc123",
        "lwa_app_id": "amzn1.application-oa2-client.abc123",
        "lwa_client_secret": "abc123",
        "aws_environment": "SANDBOX",
        "region": "US",
    }
    stream_names = [s.name for s in get_source(config).streams(config)]
    for vendor_stream in VENDOR_ONLY_STREAM_NAMES:
        assert vendor_stream not in stream_names, f"{vendor_stream} should not appear when account_type is not set"


def test_seller_streams_excluded_for_vendor():
    config = {
        "refresh_token": "Atzr|IwEBIP-abc123",
        "lwa_app_id": "amzn1.application-oa2-client.abc123",
        "lwa_client_secret": "abc123",
        "aws_environment": "SANDBOX",
        "region": "US",
        "account_type": "Vendor",
    }
    stream_names = [s.name for s in get_source(config).streams(config)]
    for seller_stream in SELLER_ONLY_STREAM_NAMES:
        assert seller_stream not in stream_names, f"{seller_stream} should not appear for Vendor accounts"


def test_seller_streams_included_for_seller():
    config = {
        "refresh_token": "Atzr|IwEBIP-abc123",
        "lwa_app_id": "amzn1.application-oa2-client.abc123",
        "lwa_client_secret": "abc123",
        "aws_environment": "SANDBOX",
        "region": "US",
        "account_type": "Seller",
    }
    stream_names = [s.name for s in get_source(config).streams(config)]
    for seller_stream in SELLER_ONLY_STREAM_NAMES:
        assert seller_stream in stream_names, f"{seller_stream} should appear for Seller accounts"


def test_seller_streams_included_when_account_type_missing():
    config = {
        "refresh_token": "Atzr|IwEBIP-abc123",
        "lwa_app_id": "amzn1.application-oa2-client.abc123",
        "lwa_client_secret": "abc123",
        "aws_environment": "SANDBOX",
        "region": "US",
    }
    stream_names = [s.name for s in get_source(config).streams(config)]
    for seller_stream in SELLER_ONLY_STREAM_NAMES:
        assert seller_stream in stream_names, f"{seller_stream} should appear when account_type is not set (defaults to Seller)"


@pytest.mark.parametrize(
    "account_type,expected_first_stream",
    [
        pytest.param("Seller", "Orders", id="seller_first_stream_is_orders"),
        pytest.param("Vendor", "VendorOrders", id="vendor_first_stream_is_vendor_orders"),
    ],
)
def test_first_stream_ordering_for_check(account_type, expected_first_stream):
    """CheckDynamicStream uses the first stream for connectivity check.

    Seller accounts must resolve Orders first; Vendor accounts must resolve
    VendorOrders first. If this test fails, the connectivity check will use
    the wrong stream — see the IMPORTANT comment in manifest.yaml streams section.
    """
    config = {
        "refresh_token": "Atzr|IwEBIP-abc123",
        "lwa_app_id": "amzn1.application-oa2-client.abc123",
        "lwa_client_secret": "abc123",
        "aws_environment": "SANDBOX",
        "region": "US",
        "account_type": account_type,
    }
    streams = get_source(config).streams(config)
    assert streams[0].name == expected_first_stream, (
        f"Expected first stream for {account_type} to be {expected_first_stream}, "
        f"got {streams[0].name}. Stream ordering matters for CheckDynamicStream."
    )


mock_catalog = ConfiguredAirbyteCatalog(
    streams=[
        ConfiguredAirbyteStream(
            stream=AirbyteStream(name="Orders", json_schema={}, supported_sync_modes=[SyncMode.full_refresh, SyncMode.incremental]),
            sync_mode=SyncMode.full_refresh,
            destination_sync_mode=DestinationSyncMode.overwrite,
        ),
        ConfiguredAirbyteStream(
            stream=AirbyteStream(name="OrderItems", json_schema={}, supported_sync_modes=[SyncMode.full_refresh, SyncMode.incremental]),
            sync_mode=SyncMode.full_refresh,
            destination_sync_mode=DestinationSyncMode.overwrite,
        ),
        ConfiguredAirbyteStream(
            stream=AirbyteStream(
                name="ListFinancialEventGroups", json_schema={}, supported_sync_modes=[SyncMode.full_refresh, SyncMode.incremental]
            ),
            sync_mode=SyncMode.full_refresh,
            destination_sync_mode=DestinationSyncMode.overwrite,
        ),
        ConfiguredAirbyteStream(
            stream=AirbyteStream(
                name="ListFinancialEvents", json_schema={}, supported_sync_modes=[SyncMode.full_refresh, SyncMode.incremental]
            ),
            sync_mode=SyncMode.full_refresh,
            destination_sync_mode=DestinationSyncMode.overwrite,
        ),
        ConfiguredAirbyteStream(
            stream=AirbyteStream(
                name="VendorDirectFulfillmentShipping", json_schema={}, supported_sync_modes=[SyncMode.full_refresh, SyncMode.incremental]
            ),
            sync_mode=SyncMode.full_refresh,
            destination_sync_mode=DestinationSyncMode.overwrite,
        ),
        ConfiguredAirbyteStream(
            stream=AirbyteStream(name="VendorOrders", json_schema={}, supported_sync_modes=[SyncMode.full_refresh, SyncMode.incremental]),
            sync_mode=SyncMode.full_refresh,
            destination_sync_mode=DestinationSyncMode.overwrite,
        ),
    ]
)

STREAM_NAMES = [
    "Orders",
    "OrderItems",
    "ListFinancialEventGroups",
    "ListFinancialEvents",
    "VendorDirectFulfillmentShipping",
    "VendorOrders",
]


END_DATETIME_LOGIC = {
    "Orders": "now_minus_2m",  # now_utc() - PT2M
    "OrderItems": "now",  # now_utc()
    "ListFinancialEventGroups": "now_minus_2m",  # now_utc() - PT2M
    "ListFinancialEvents": "now_minus_2m",  # now_utc() - PT2M
    "VendorDirectFulfillmentShipping": "now",  # now_utc()
    "VendorOrders": "now",  # now_utc()
}


# Helper function to calculate default start date (now - 730 days)
def default_start_date(now):
    return (now - timedelta(days=730)).strftime("%Y-%m-%dT%H:%M:%SZ")


# Helper function to calculate default end date based on stream logic
def default_end_date(stream_name, now):
    if END_DATETIME_LOGIC[stream_name] == "now_minus_2m":
        return (now - timedelta(minutes=2)).strftime("%Y-%m-%dT%H:%M:%SZ")
    return now.strftime("%Y-%m-%dT%H:%M:%SZ")


@pytest.mark.parametrize("stream_name", STREAM_NAMES, ids=STREAM_NAMES)
@pytest.mark.parametrize(
    "config, expected_start_base, expected_end_base",
    [
        # Case 1: Valid Range - end_date after start_date
        (
            {
                "replication_start_date": "2022-09-01T00:00:00Z",
                "replication_end_date": "2022-10-01T00:00:00Z",
                "refresh_token": "dummy_token",
                "lwa_app_id": "dummy_id",
                "lwa_client_secret": "dummy_secret",
                "aws_environment": "SANDBOX",
                "region": "US",
                "marketplace_id": "ATVPDKIKX0DER",
            },
            "2022-09-01T00:00:00Z",
            "2022-10-01T00:00:00Z",
        ),
        # Case 2: Only End Date Provided
        (
            {
                "replication_end_date": "2022-10-01T00:00:00Z",
                "refresh_token": "dummy_token",
                "lwa_app_id": "dummy_id",
                "lwa_client_secret": "dummy_secret",
                "aws_environment": "SANDBOX",
                "region": "US",
                "marketplace_id": "ATVPDKIKX0DER",
            },
            "2021-01-01T00:00:00Z",  # Default start: now - 730 days
            "2022-10-01T00:00:00Z",
        ),
        # Case 3: Only Start Date Provided
        (
            {
                "replication_start_date": "2022-09-01T00:00:00Z",
                "refresh_token": "dummy_token",
                "lwa_app_id": "dummy_id",
                "lwa_client_secret": "dummy_secret",
                "aws_environment": "SANDBOX",
                "region": "US",
                "marketplace_id": "ATVPDKIKX0DER",
            },
            "2022-09-01T00:00:00Z",
            None,  # Default end depends on stream
        ),
        # Case 4: No Dates Provided
        (
            {
                "refresh_token": "dummy_token",
                "lwa_app_id": "dummy_id",
                "lwa_client_secret": "dummy_secret",
                "aws_environment": "SANDBOX",
                "region": "US",
                "marketplace_id": "ATVPDKIKX0DER",
            },
            "2021-01-01T00:00:00Z",  # Default start: now - 730 days
            None,  # Default end depends on stream
        ),
        # Case 5: Start Date Before Default
        (
            {
                "replication_start_date": "2020-01-01T00:00:00Z",
                "replication_end_date": "2022-10-01T00:00:00Z",
                "refresh_token": "dummy_token",
                "lwa_app_id": "dummy_id",
                "lwa_client_secret": "dummy_secret",
                "aws_environment": "SANDBOX",
                "region": "US",
                "marketplace_id": "ATVPDKIKX0DER",
            },
            "2021-01-01T00:00:00Z",  # Adjusted to default start: now - 730 days
            "2022-10-01T00:00:00Z",
        ),
    ],
    ids=[
        "valid_end_after_start",
        "only_end_date",
        "only_start_date",
        "no_dates",
        "start_date_before_default",
    ],
)
@freeze_time("2023-01-01T00:00:00Z")
def test_stream_slice_dates(config, expected_start_base, expected_end_base, stream_name, requests_mock):
    """
    Test that stream slices have the correct start and end times for all REST API streams based on config and stream-specific logic.

    Args:
        config (dict): Configuration dictionary for the source.
        expected_start_base (str): Expected start time for the first slice.
        expected_end_base (str or None): Expected end time for the last slice, or None if computed dynamically.
        stream_name (str): Name of the stream to test.
        requests_mock: Fixture to mock HTTP requests.
    """
    now = datetime.strptime("2023-01-01T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ")

    # Vendor streams require account_type=Vendor to appear in the catalog
    if stream_name.startswith("Vendor"):
        config = {**config, "account_type": "Vendor"}

    # Mock the token refresh endpoint
    requests_mock.post(
        "https://api.amazon.com/auth/o2/token", json={"access_token": "fake_access_token", "expires_in": 3600}, status_code=200
    )

    # Mock the Orders API endpoint for OrderItems stream
    if stream_name == "OrderItems":
        orders_url = "https://sandbox.sellingpartnerapi-na.amazon.com/orders/v0/orders"
        requests_mock.get(orders_url, json={"payload": {"Orders": [{"AmazonOrderId": "123-4567890-1234567"}]}}, status_code=200)

    # Initialize the source with the mock catalog, test config, and no state
    source = get_source(config=config, state=None)

    # Retrieve the specific stream by its name
    streams = source.streams(source._config)
    stream = next((s for s in streams if s.name == stream_name), None)
    assert stream is not None, f"Stream '{stream_name}' not found in available streams"

    # Compute the expected end time if not explicitly provided
    if expected_end_base is None:
        expected_end = default_end_date(stream_name, now)
    else:
        expected_end = expected_end_base

    # Generate and verify stream slices
    slices = list(map(lambda partition: partition.to_slice(), stream.generate_partitions()))
    assert len(slices) > 0, f"No slices generated for stream '{stream_name}'"
    first_slice = slices[0]
    last_slice = slices[-1]

    # Assert start and end times match expectations
    assert (
        first_slice["start_time"] == expected_start_base
    ), f"Stream '{stream_name}': Expected start time {expected_start_base}, got {first_slice['start_time']}"
    assert last_slice["end_time"] == expected_end, f"Stream '{stream_name}': Expected end time {expected_end}, got {last_slice['end_time']}"


# --- Lookback window manifest-level tests ---


def _load_manifest():
    manifest_path = Path(__file__).parent.parent / "manifest.yaml"
    with open(manifest_path, "r") as f:
        return yaml.safe_load(f)


@pytest.mark.parametrize(
    "stream_key, should_have_lookback",
    [
        pytest.param("get_sales_and_traffic_report", False, id="asin_aggregate_no_lookback"),
        pytest.param("get_sales_and_traffic_report_by_date", True, id="by_date_has_lookback"),
        pytest.param("get_sales_and_traffic_report_by_month", False, id="by_month_no_lookback"),
    ],
)
def test_manifest_lookback_window_on_sales_and_traffic_streams(stream_key, should_have_lookback):
    """
    GET_SALES_AND_TRAFFIC_REPORT extracts salesAndTrafficByAsin which aggregates
    across the full date range (dateGranularity defaults to TOTAL). A lookback
    window causes cross-midnight slices that produce inflated multi-day sums,
    corrupting destination data. This stream must NOT have a lookback_window.

    GET_SALES_AND_TRAFFIC_REPORT_BY_DATE extracts salesAndTrafficByDate (per-day
    records) and safely supports lookback.

    GET_SALES_AND_TRAFFIC_REPORT_BY_MONTH uses monthly granularity and must NOT
    have a lookback_window.
    """
    manifest = _load_manifest()
    incremental_sync = manifest["definitions"]["streams"][stream_key]["incremental_sync"]
    has_lookback = "lookback_window" in incremental_sync

    if should_have_lookback:
        assert has_lookback, (
            f"Stream '{stream_key}' should have a lookback_window (it extracts per-day records)"
        )
    else:
        assert not has_lookback, (
            f"Stream '{stream_key}' must NOT have a lookback_window "
            f"(it aggregates across the date range, causing data corruption with cross-midnight slices)"
        )
