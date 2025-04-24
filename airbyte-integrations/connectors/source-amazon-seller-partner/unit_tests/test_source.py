#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import logging
from datetime import datetime, timedelta
from unittest.mock import patch

import freezegun
import pytest
import requests_mock
from freezegun import freeze_time
from source_amazon_seller_partner import SourceAmazonSellerPartner
from source_amazon_seller_partner.components import AmazonSPOauthAuthenticator
from source_amazon_seller_partner.utils import AmazonConfigException

from airbyte_cdk.models import AirbyteStream, ConfiguredAirbyteCatalog, ConfiguredAirbyteStream, DestinationSyncMode, SyncMode
from airbyte_cdk.sources.streams import Stream


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
    assert SourceAmazonSellerPartner(
        config=connector_config_with_report_options,
        catalog=None,
        state=None,
    ).check_connection(logger, connector_config_with_report_options) == (True, None)


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
    assert SourceAmazonSellerPartner(
        config=connector_config_with_report_options,
        catalog=None,
        state=None,
    ).check_connection(logger, connector_config_with_report_options) == (True, None)


@pytest.mark.parametrize(
    ("report_name", "stream_name_w_options"),
    (
        (
            "GET_FBA_FULFILLMENT_CUSTOMER_RETURNS_DATA",
            [
                (
                    "GET_FBA_FULFILLMENT_CUSTOMER_RETURNS_DATA",
                    [
                        {"option_name": "some_name_1", "option_value": "some_value_1"},
                        {"option_name": "some_name_2", "option_value": "some_value_2"},
                    ],
                ),
            ],
        ),
        ("SOME_OTHER_STREAM", []),
    ),
)
def test_get_stream_report_options_list(connector_config_with_report_options, report_name, stream_name_w_options):
    assert (
        list(
            SourceAmazonSellerPartner(
                config=connector_config_with_report_options,
                catalog=None,
                state=None,
            ).get_stream_report_kwargs(report_name, connector_config_with_report_options)
        )
        == stream_name_w_options
    )


def test_config_report_options_validation_error_duplicated_streams(connector_config_with_report_options):
    connector_config_with_report_options["report_options_list"].append(connector_config_with_report_options["report_options_list"][0])
    with pytest.raises(AmazonConfigException) as e:
        SourceAmazonSellerPartner(
            config=connector_config_with_report_options,
            catalog=None,
            state=None,
        ).validate_stream_report_options(connector_config_with_report_options)
    assert e.value.message == "Stream name should be unique among all Report options list"


def test_config_report_options_validation_error_duplicated_options(connector_config_with_report_options):
    connector_config_with_report_options["report_options_list"][0]["options_list"].append(
        connector_config_with_report_options["report_options_list"][0]["options_list"][0]
    )
    with pytest.raises(AmazonConfigException) as e:
        SourceAmazonSellerPartner(
            config=connector_config_with_report_options,
            catalog=None,
            state=None,
        ).validate_stream_report_options(connector_config_with_report_options)
    assert e.value.message == "Option names should be unique for `GET_FBA_FULFILLMENT_CUSTOMER_RETURNS_DATA` report options"


def test_streams(connector_config_without_start_date):
    for stream in SourceAmazonSellerPartner(
        config=connector_config_without_start_date,
        catalog=None,
        state=None,
    ).streams(connector_config_without_start_date):
        assert isinstance(stream, Stream)


def test_streams_count(connector_config_without_start_date, monkeypatch):
    streams = SourceAmazonSellerPartner(
        config=connector_config_without_start_date,
        catalog=None,
        state=None,
    ).streams(connector_config_without_start_date)
    assert len(streams) == 44


@pytest.mark.parametrize(
    ("config", "should_raise"),
    (
        ({"replication_start_date": "2022-09-01T00:00:00Z", "replication_end_date": "2022-08-01T00:00:00Z"}, True),
        ({"replication_start_date": "2022-09-01T00:00:00Z", "replication_end_date": "2022-10-01T00:00:00Z"}, False),
        ({"replication_end_date": "2022-10-01T00:00:00Z"}, False),
        ({"replication_start_date": "2022-09-01T00:00:00Z"}, False),
        ({}, False),
    ),
)
def test_replication_dates_validation(config, should_raise):
    if should_raise:
        with pytest.raises(AmazonConfigException) as e:
            SourceAmazonSellerPartner(
                config=config,
                catalog=None,
                state=None,
            ).validate_replication_dates(config)
        assert e.value.message == "End Date should be greater than or equal to Start Date"
    else:
        assert (
            SourceAmazonSellerPartner(
                config=config,
                catalog=None,
                state=None,
            ).validate_replication_dates(config)
            is None
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

    # Mock the token refresh endpoint
    requests_mock.post(
        "https://api.amazon.com/auth/o2/token", json={"access_token": "fake_access_token", "expires_in": 3600}, status_code=200
    )

    # Mock the Orders API endpoint for OrderItems stream
    if stream_name == "OrderItems":
        start_date = config.get("replication_start_date", default_start_date(now))
        end_date = config.get("replication_end_date", default_end_date("Orders", now))
        # Adjust start_date to default if earlier than now - 730 days
        default_start = default_start_date(now)
        start_date = max(start_date, default_start)

        orders_url = (
            f"https://sandbox.sellingpartnerapi-na.amazon.com/orders/v0/orders?"
            f"MarketplaceIds={config['marketplace_id']}&MaxResultsPerPage=100&"
            f"LastUpdatedAfter={start_date}&LastUpdatedBefore={end_date}"
        )
        requests_mock.get(orders_url, json={"payload": {"Orders": [{"AmazonOrderId": "123-4567890-1234567"}]}}, status_code=200)

    # Initialize the source with the mock catalog, test config, and no state
    source = SourceAmazonSellerPartner(catalog=mock_catalog, config=config, state=None)

    # Retrieve the specific stream by its name
    streams = source.streams(config)
    stream = next((s for s in streams if s.name == stream_name), None)
    assert stream is not None, f"Stream '{stream_name}' not found in available streams"

    # Compute the expected end time if not explicitly provided
    if expected_end_base is None:
        expected_end = default_end_date(stream_name, now)
    else:
        expected_end = expected_end_base

    # Generate and verify stream slices
    slices = list(stream.stream_slices(sync_mode=SyncMode.full_refresh, stream_state={}))
    assert len(slices) > 0, f"No slices generated for stream '{stream_name}'"
    first_slice = slices[0]
    last_slice = slices[-1]

    # Assert start and end times match expectations
    assert (
        first_slice["start_time"] == expected_start_base
    ), f"Stream '{stream_name}': Expected start time {expected_start_base}, got {first_slice['start_time']}"
    assert last_slice["end_time"] == expected_end, f"Stream '{stream_name}': Expected end time {expected_end}, got {last_slice['end_time']}"
