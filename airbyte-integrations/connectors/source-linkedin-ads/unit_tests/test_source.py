#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import pytest
import requests
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.requests_native_auth import Oauth2Authenticator, TokenAuthenticator
from conftest import find_stream
from source_linkedin_ads.source import SourceLinkedinAds

LINKEDIN_VERSION_API = 202404

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

    def test_custom_streams(self):
        config = {"ad_analytics_reports": [{"name": "ShareAdByMonth", "pivot_by": "COMPANY", "time_granularity": "MONTHLY"}], **TEST_CONFIG}
        ad_campaign_analytics = find_stream('ad_campaign_analytics', config)
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
        ids=[
            "Accounts",
            "AccountUsers",
            "CampaignGroups",
            "Campaigns",
            "Creatives",
            "AdCampaignAnalytics",
            "AdCreativeAnalytics",
        ],
    )
    def test_path(self, stream_name, expected):
        stream = find_stream(stream_name, config=TEST_CONFIG)
        result = stream.retriever.requester.path
        assert result == expected

    def test_check_connection(self, check_availability_mock):
        check_availability_mock.return_value = (True, None)
        is_available, error = self._instance.check_connection(logger=Mock(), config=TEST_CONFIG)
        assert is_available
        assert not error


class TestLinkedinAdsStream:
    stream: Stream = find_stream("accounts", TEST_CONFIG)
    url = f"{stream.retriever.requester.url_base}/{stream.retriever.requester.path}"

    @pytest.mark.parametrize(
        "response_json, expected",
        (
            ({"elements": []}, None),
            (
                {"elements": [{"data": []}] * 500, "metadata": {"nextPageToken": "next_page_token"}, "paging": {"start": 0, "total": 600}},
                {"next_page_token": "next_page_token"},
            ),
        ),
    )
    def test_next_page_token(self, requests_mock, response_json, expected):
        requests_mock.get(self.url, json=response_json)
        test_response = requests.get(self.url)

        result = self.stream.retriever._next_page_token(test_response)
        assert expected == result
