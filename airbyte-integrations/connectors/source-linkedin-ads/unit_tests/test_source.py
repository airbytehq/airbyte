#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import logging
import pytest
import requests
from unittest.mock import patch, MagicMock
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.exceptions import DefaultBackoffException, RateLimitBackoffException
from airbyte_cdk.sources.streams.http.requests_native_auth import Oauth2Authenticator, TokenAuthenticator
from airbyte_cdk.sources.streams.http import HttpStream
from conftest import find_stream
from source_linkedin_ads.source import SourceLinkedinAds

logger = logging.getLogger("airbyte")

LINKEDIN_VERSION_API = 202404

# Test configurations
TEST_OAUTH_CONFIG: dict = {
    "start_date": "2021-08-01",
    "account_ids": [],
    "credentials": {
        "auth_method": "oAuth2.0",
        "client_id": "client_id",
        "client_secret": "client_secret",
        "refresh_token": "refresh_token",
    },
}

TEST_CONFIG: dict = {
    "start_date": "2021-08-01",
    "account_ids": [1, 2],
    "credentials": {
        "auth_method": "access_token",
        "access_token": "access_token",
        "authenticator": TokenAuthenticator(token="123"),
    },
}

TEST_CONFIG_DUPLICATE_CUSTOM_AD_ANALYTICS_REPORTS: dict = {
    "start_date": "2021-01-01",
    "account_ids": [],
    "credentials": {
        "auth_method": "oAuth2.0",
        "client_id": "client_id",
        "client_secret": "client_secret",
        "refresh_token": "refresh_token",
    },
    "ad_analytics_reports": [
        {"name": "ShareAdByMonth", "pivot_by": "COMPANY", "time_granularity": "MONTHLY"},
        {"name": "ShareAdByMonth", "pivot_by": "COMPANY", "time_granularity": "MONTHLY"},
    ],
}


class TestAllStreams:
    _instance: SourceLinkedinAds = SourceLinkedinAds()

    @pytest.mark.parametrize(
        "error_code, response_headers, response_text, expected_exception",
        [
            (429, {"Retry-After": "2"}, "Too many requests", RateLimitBackoffException),
            (500, {}, "Internal Server Error", DefaultBackoffException),
            (503, {}, "Service Unavailable", DefaultBackoffException),
        ],
    )
    def test_should_retry_on_error(
        self, error_code, response_headers, response_text, expected_exception, requests_mock, mocker, caplog
    ):
        mocker.patch("time.sleep", lambda x: None)
        stream = find_stream("accounts", TEST_CONFIG)

        # Mock HTTP request and response
        mock_request = MagicMock()
        mock_request.url = "https://api.linkedin.com/rest/adAccounts"
        mock_request.method = "GET"

        mock_response = MagicMock()
        mock_response.status_code = error_code
        mock_response.headers = response_headers
        mock_response.text = response_text

        # Mock `read_records` instead of `_read_pages`
        with patch.object(HttpStream, "read_records") as mock_read_records:
            mock_read_records.side_effect = expected_exception(request=mock_request, response=mock_response)

            with caplog.at_level("INFO", logger="airbyte_cdk"):
                with pytest.raises(expected_exception):
                    list(stream.read_records(sync_mode=SyncMode.full_refresh))

            retry_logs = [line for line in caplog.text.splitlines() if "Backing off" in line or "retrying" in line]
            assert retry_logs, f"No retry logs detected for error_code {error_code}."

    def test_custom_streams(self):
        config = {"ad_analytics_reports": [{"name": "ShareAdByMonth", "pivot_by": "COMPANY", "time_granularity": "MONTHLY"}], **TEST_CONFIG}
        ad_campaign_analytics = find_stream("ad_campaign_analytics", config)
        for stream in self._instance._create_custom_ad_analytics_streams(config=config):
            assert isinstance(stream, type(ad_campaign_analytics))

    @pytest.mark.parametrize(
        "stream_name, expected",
        [
            ("accounts", "adAccounts"),
            ("account_users", "adAccountUsers"),
            ("campaign_groups", "adAccounts/{{stream_slice.get('account_id')}}/adCampaignGroups"),
            ("campaigns", "adAccounts/{{stream_slice.get('account_id')}}/adCampaigns"),
            ("creatives", "adAccounts/{{stream_slice.get('account_id')}}/creatives"),
            ("ad_campaign_analytics", "adAnalytics"),
            ("ad_creative_analytics", "adAnalytics"),
        ],
    )
    def test_path(self, stream_name, expected):
        stream = find_stream(stream_name, config=TEST_CONFIG)
        result = stream.retriever.requester.path
        assert result == expected

    @pytest.mark.parametrize(
        ("status_code", "is_connection_successful", "error_msg"),
        [
            (400, False, "Bad request. Please check your request parameters."),
            (403, False, "Forbidden. You don't have permission to access this resource."),
            (200, True, None),
        ],
    )
    def test_check_connection(self, requests_mock, status_code, is_connection_successful, error_msg):
        # Mock the API response
        json = (
            {"elements": [{"data": []}] * 500}
            if 200 <= status_code < 300
            else {"error": {"message": error_msg}}
        )
        requests_mock.register_uri(
            "GET",
            "https://api.linkedin.com/rest/adAccounts?q=search&pageSize=500",
            status_code=status_code,
            json=json,
        )

        # Call check_connection
        success, error = self._instance.check_connection(logger=logger, config=TEST_CONFIG)

        # Verify the result
        assert success is is_connection_successful, f"Expected {is_connection_successful} but got {success}"
        assert error == error_msg, f"Expected error '{error_msg}' but got '{error}'"


class TestLinkedinAdsStream:
    stream: Stream = find_stream("accounts", TEST_CONFIG)
    url = f"{stream.retriever.requester.url_base}/{stream.retriever.requester.path}"

    @pytest.mark.parametrize(
        "response_json, expected",
        [
            ({"elements": []}, None),
            (
                {"elements": [{"data": []}] * 500, "metadata": {"nextPageToken": "next_page_token"}, "paging": {"start": 0, "total": 600}},
                {"next_page_token": "next_page_token"},
            ),
        ],
    )
    def test_next_page_token(self, requests_mock, response_json, expected):
        requests_mock.get(self.url, json=response_json)
        test_response = requests.get(self.url)

        result = self.stream.retriever._next_page_token(test_response)
        assert expected == result
