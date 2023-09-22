from unittest.mock import Mock

import pytest
from airbyte_cdk import AirbyteLogger
from airbyte_cdk.utils import AirbyteTracedException
from source_google_ads.google_ads import GoogleAds
from source_google_ads.source import SourceGoogleAds
from source_google_ads.streams import AdGroupLabels, Labels, ServiceAccounts

from .common import MockGoogleAdsClient, mock_google_ads_request_failure

params = [
    ("USER_PERMISSION_DENIED",
     "Failed to access the customer '123'. Ensure the customer is linked to your manager account or check your permissions to access this customer account."),

    ("CUSTOMER_NOT_FOUND",
     "Failed to access the customer '123'. Ensure the customer is linked to your manager account or check your permissions to access this customer account."),

    ("CUSTOMER_NOT_ENABLED",
     ("The Google Ads account '123' you're trying to access is not enabled. "
      "This may occur if the account hasn't been fully set up or activated. "
      "Please ensure that you've completed all necessary setup steps in the Google Ads platform and that the account is active. "
      "If the account is recently created, it might take some time before it's fully activated.")),

    ("QUERY_ERROR", "Incorrect custom query. Error in query: unexpected end of query."),

    ("RESOURCE_EXHAUSTED",
     "You've exceeded your 24-hour quota limits for operations on your Google Ads account '123'. Try again later."),

    ("UNEXPECTED_ERROR", "Unexpected error message")
]


@pytest.mark.parametrize(("exception", "error_message"), params)
def test_expected_errors(mocker, config, exception, error_message):
    mock_google_ads_request_failure(mocker, exception)
    source = SourceGoogleAds()
    with pytest.raises(AirbyteTracedException) as exception:
        status_ok, error = source.check_connection(AirbyteLogger(), config)
    assert exception.value.message == error_message


@pytest.mark.parametrize(
    ("cls", "raise_expected"),
    (
            (AdGroupLabels, False),
            (Labels, False),
            (ServiceAccounts, True),
    ),
)
def test_read_record_error_handling(mocker, config, customers, cls, raise_expected):
    mock_google_ads_request_failure(mocker, "CUSTOMER_NOT_ENABLED")
    google_api = GoogleAds(credentials=config["credentials"])
    stream = cls(api=google_api, customers=customers)
    if raise_expected:
        with pytest.raises(AirbyteTracedException) as exception:
            for _ in stream.read_records(sync_mode=Mock(), stream_slice={"customer_id": "1234567890"}):
                pass
        assert exception.value.message == ("The Google Ads account '1234567890' you're trying to access is not enabled. "
                                           "This may occur if the account hasn't been fully set up or activated. Please "
                                           "ensure that you've completed all necessary setup steps in the Google Ads "
                                           "platform and that the account is active. If the account is recently created, "
                                           "it might take some time before it's fully activated.")
    else:
        for _ in stream.read_records(sync_mode=Mock(), stream_slice={"customer_id": "1234567890"}):
            pass


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
                True, None, ('Metrics are not available for manager account 8765. Please remove metrics '
                             'fields in your custom query: SELECT campaign.accessible_bidding_strategy, '
                             'metrics.clicks FROM campaigns.')
        ),
        (
                {
                    "query": "SELECT campaign.accessible_bidding_strategy, metrics.clicks from campaigns",
                    "primary_key": None,
                    "cursor_field": None,
                    "table_name": "happytable",
                },
                False, None, None
        ),
        (
                {
                    "query": "SELECT segments.ad_destination_type, segments.date from campaigns",
                    "primary_key": "customer.id",
                    "cursor_field": None,
                    "table_name": "unhappytable",
                },
                False, "Custom query should not contain segments.date", None
        ),
    ]
)
def test_check_custom_queries(mocker, config, custom_query, is_manager_account, error_message, warning):
    config["custom_queries"] = [custom_query]
    mocker.patch(
        "source_google_ads.source.SourceGoogleAds.get_account_info",
        Mock(return_value=[[{"customer.manager": is_manager_account, "customer.time_zone": "Europe/Berlin", "customer.id": "8765"}]]),
    )
    mocker.patch("source_google_ads.google_ads.GoogleAdsClient", return_value=MockGoogleAdsClient)
    source = SourceGoogleAds()

    logger_mock = Mock()
    if error_message:
        with pytest.raises(AirbyteTracedException) as exception:
            status_ok, error = source.check_connection(logger_mock, config)
        assert exception.value.message == error_message
    else:
        status_ok, error = source.check_connection(logger_mock, config)
        if warning:
            logger_mock.warning.assert_called_with(warning)
