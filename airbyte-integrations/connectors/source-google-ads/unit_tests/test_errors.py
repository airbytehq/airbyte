#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import logging
from contextlib import nullcontext as does_not_raise
from unittest.mock import Mock

import pytest
from source_google_ads.google_ads import GoogleAds
from source_google_ads.models import CustomerModel
from source_google_ads.source import SourceGoogleAds
from source_google_ads.streams import AdGroupLabel, Label, ServiceAccounts

from airbyte_cdk.utils import AirbyteTracedException

from .common import MockGoogleAdsClient, mock_google_ads_request_failure


@pytest.fixture
def mock_get_customers(mocker):
    mocker.patch(
        "source_google_ads.source.SourceGoogleAds.get_customers",
        Mock(return_value=[CustomerModel(is_manager_account=False, time_zone="Europe/Berlin", id="123")]),
    )


params = [
    (
        ["USER_PERMISSION_DENIED"],
        "Failed to access the customer '123'. Ensure the customer is linked to your manager account or check your permissions to access this customer account.",
    ),
    (
        ["CUSTOMER_NOT_FOUND"],
        "Failed to access the customer '123'. Ensure the customer is linked to your manager account or check your permissions to access this customer account.",
    ),
    (["QUERY_ERROR"], "Incorrect custom query. Error in query: unexpected end of query."),
    (
        ["UNRECOGNIZED_FIELD"],
        "The Custom Query: `None` has unrecognized field in the query. Please make sure the field exists or name entered is valid.",
    ),
    (
        ["RESOURCE_EXHAUSTED"],
        (
            "The operation limits for your Google Ads account '123' have been exceeded for the last 24 hours. "
            "To avoid these limitations, consider applying for Standard access which offers unlimited operations per day. "
            "Learn more about access levels and how to apply for Standard access here: "
            "https://developers.google.com/google-ads/api/docs/access-levels#access_levels_2"
        ),
    ),
    (["UNEXPECTED_ERROR"], "Unexpected error message"),
    (["QUERY_ERROR", "UNEXPECTED_ERROR"], "Incorrect custom query. Error in query: unexpected end of query.\nUnexpected error message"),
]


@pytest.mark.parametrize(("exception", "error_message"), params)
def test_expected_errors(mocker, config, exception, error_message):
    mock_google_ads_request_failure(mocker, exception)
    mocker.patch(
        "source_google_ads.google_ads.GoogleAds.get_accessible_accounts",
        Mock(return_value=["123", "12345"]),
    )
    source = SourceGoogleAds()
    with pytest.raises(AirbyteTracedException) as exception:
        status_ok, error = source.check_connection(logging.getLogger("airbyte"), config)
    assert exception.value.message == error_message


@pytest.mark.parametrize(
    ("cls", "raise_expected"),
    (
        (AdGroupLabel, False),
        (Label, False),
        (ServiceAccounts, True),
    ),
)
def test_read_record_error_handling(mocker, config, customers, cls, raise_expected):
    mock_google_ads_request_failure(mocker, ["CUSTOMER_NOT_ENABLED"])
    google_api = GoogleAds(credentials=config["credentials"])
    stream = cls(api=google_api, customers=customers)

    # Use nullcontext or pytest.raises based on raise_expected
    context = pytest.raises(AirbyteTracedException) if raise_expected else does_not_raise()

    with context as exception:
        for _ in stream.read_records(sync_mode=Mock(), stream_slice={"customer_id": "1234567890", "login_customer_id": "default"}):
            pass

    if raise_expected:
        assert exception.value.message == (
            "The customer account '1234567890' hasn't finished signup or has been deactivated. "
            "Sign in to the Google Ads UI to verify its status. "
            "For reactivating deactivated accounts, refer to: "
            "https://support.google.com/google-ads/answer/2375392."
        )


@pytest.mark.parametrize(
    "custom_query, is_manager_account, error_message, warning",
    [
        (
            {
                "query": "SELECT campaign.accessible_bidding_strategy, metrics.clicks from campaigns",
                "primary_key": None,
                "cursor_field": "None",
                "table_name": "happytable",
            },
            True,
            None,
            (
                "Metrics are not available for manager account 8765. "
                'Skipping the custom query: "SELECT campaign.accessible_bidding_strategy, '
                'metrics.clicks FROM campaigns" for manager account.'
            ),
        ),
        (
            {
                "query": "SELECT campaign.accessible_bidding_strategy, metrics.clicks from campaigns",
                "primary_key": None,
                "cursor_field": None,
                "table_name": "happytable",
            },
            False,
            None,
            None,
        ),
        (
            {
                "query": "SELECT segments.ad_destination_type, segments.date from campaigns",
                "primary_key": "customer.id",
                "cursor_field": None,
                "table_name": "unhappytable",
            },
            False,
            None,
            None,
        ),
    ],
)
def test_check_custom_queries(mocker, config, custom_query, is_manager_account, error_message, warning):
    config["custom_queries_array"] = [custom_query]
    mocker.patch(
        "source_google_ads.source.SourceGoogleAds.get_customers",
        Mock(return_value=[CustomerModel(is_manager_account=is_manager_account, time_zone="Europe/Berlin", id="8765")]),
    )
    mocker.patch("source_google_ads.google_ads.GoogleAdsClient", return_value=MockGoogleAdsClient)
    source = SourceGoogleAds()
    logger_mock = Mock()

    # Use nullcontext or pytest.raises based on error_message
    context = pytest.raises(AirbyteTracedException) if error_message else does_not_raise()

    with context as exception:
        status_ok, error = source.check_connection(logger_mock, config)

    if error_message:
        assert exception.value.message == error_message

    if warning:
        logger_mock.warning.assert_called_with(warning)
