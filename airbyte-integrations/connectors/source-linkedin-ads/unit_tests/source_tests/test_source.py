#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from unittest.mock import patch

import pytest
import requests
from airbyte_cdk import AirbyteLogger
from airbyte_cdk.sources.streams.http.auth import Oauth2Authenticator, TokenAuthenticator
from source_linkedin_ads.source import (
    Accounts,
    AccountUsers,
    AdCampaignAnalytics,
    AdCreativeAnalytics,
    AdDirectSponsoredContents,
    CampaignGroups,
    Campaigns,
    Creatives,
    LinkedinAdsOAuth2Authenticator,
    SourceLinkedinAds,
)

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


class TestAllStreams:

    _instance: SourceLinkedinAds = SourceLinkedinAds()

    @pytest.mark.parametrize(
        "config",
        [
            (TEST_CONFIG),
            (TEST_OAUTH_CONFIG),
        ],
        ids=[
            "access_token",
            "oauth2.0",
        ],
    )
    def test_get_authenticator(self, config: dict):
        test = self._instance.get_authenticator(config)
        assert isinstance(test, (Oauth2Authenticator, TokenAuthenticator))

    @pytest.mark.parametrize(
        "response, check_passed",
        [
            (iter({"id": 123}), True),
            (requests.HTTPError(), False),
        ],
        ids=["Success", "Fail"],
    )
    def test_check(self, response, check_passed):
        with patch.object(Accounts, "read_records", return_value=response) as mock_method:
            result = self._instance.check_connection(logger=AirbyteLogger, config=TEST_CONFIG)
            mock_method.assert_called()
            assert check_passed == result[0]

    @pytest.mark.parametrize(
        "stream_cls",
        [
            (Accounts),
            (AccountUsers),
            (CampaignGroups),
            (Campaigns),
            (Creatives),
            (AdDirectSponsoredContents),
            (AdCampaignAnalytics),
            (AdCreativeAnalytics),
        ],
        ids=[
            "Accounts",
            "AccountUsers",
            "CampaignGroups",
            "Campaigns",
            "Creatives",
            "AdDirectSponsoredContents",
            "AdCampaignAnalytics",
            "AdCreativeAnalytics",
        ],
    )
    def test_streams(self, stream_cls):
        streams = self._instance.streams(config=TEST_CONFIG)
        for stream in streams:
            if stream_cls in streams:
                assert isinstance(stream, stream_cls)

    @pytest.mark.parametrize(
        "stream_cls, expected",
        [
            (Accounts, "adAccountsV2"),
            (AccountUsers, "adAccountUsersV2"),
            (CampaignGroups, "adCampaignGroupsV2"),
            (Campaigns, "adCampaignsV2"),
            (Creatives, "adCreativesV2"),
            (AdDirectSponsoredContents, "adDirectSponsoredContents"),
            (AdCampaignAnalytics, "adAnalyticsV2"),
            (AdCreativeAnalytics, "adAnalyticsV2"),
        ],
        ids=[
            "Accounts",
            "AccountUsers",
            "CampaignGroups",
            "Campaigns",
            "Creatives",
            "AdDirectSponsoredContents",
            "AdCampaignAnalytics",
            "AdCreativeAnalytics",
        ],
    )
    def test_path(self, stream_cls, expected):
        stream = stream_cls(TEST_CONFIG)
        result = stream.path()
        assert result == expected


class TestLinkedinAdsStream:

    stream: Accounts = Accounts(TEST_CONFIG)
    url = f"{stream.url_base}/{stream.path()}"

    def test_accounts(self):
        result = self.stream.accounts
        assert result == ",".join(map(str, TEST_CONFIG["account_ids"]))

    def test_next_page_token(self, requests_mock):
        requests_mock.get(self.url, json={"elements": []})
        test_response = requests.get(self.url)

        expected = None
        result = self.stream.next_page_token(test_response)
        assert expected == result

    def test_request_params(self):
        expected = "count=500&q=search&search=(id:(values:List(1,2)))"
        result = self.stream.request_params(stream_state={}, stream_slice={"account_id": 123})
        assert expected == result

    def test_parse_response(self, requests_mock):
        requests_mock.get(self.url, json={"elements": [{"test": "test"}]})
        test_response = requests.get(self.url)

        expected = {"test": "test"}
        result = list(self.stream.parse_response(test_response))
        assert result[0] == expected

    def test_should_retry(self, requests_mock):
        requests_mock.get(self.url, json={}, status_code=429)
        test_response = requests.get(self.url)
        result = self.stream.should_retry(test_response)
        assert result is True

    def test_request_headers(self):
        expected = {"X-RestLi-Protocol-Version": "2.0.0"}
        result = self.stream.request_headers(stream_state={})
        assert result == expected


class TestAccountUsers:
    stream: AccountUsers = AccountUsers(TEST_CONFIG)

    def test_state_checkpoint_interval(self):
        assert self.stream.state_checkpoint_interval == 500

    def test_get_updated_state(self):
        state = self.stream.get_updated_state(
            current_stream_state={"lastModified": "2021-01-01"}, latest_record={"lastModified": "2021-08-01"}
        )
        assert state == {"lastModified": "2021-08-01"}


class TestLinkedInAdsStreamSlicing:
    @pytest.mark.parametrize(
        "stream_cls, slice, expected",
        [
            (
                AccountUsers,
                {"account_id": 123},
                {"count": 500, "q": "accounts", "accounts": "urn:li:sponsoredAccount:123"},
            ),
            (
                CampaignGroups,
                {"account_id": 123},
                {"count": 500, "q": "search", "search.account.values[0]": "urn:li:sponsoredAccount:123"},
            ),
            (
                Campaigns,
                {"account_id": 123},
                {"count": 500, "q": "search", "search.account.values[0]": "urn:li:sponsoredAccount:123"},
            ),
            (
                Creatives,
                {"campaign_id": 123},
                {"count": 500, "q": "search", "search.campaign.values[0]": "urn:li:sponsoredCampaign:123"},
            ),
            (
                AdDirectSponsoredContents,
                {"account_id": 123},
                {"count": 500, "q": "account", "account": "urn:li:sponsoredAccount:123", "owner": None},
            ),
        ],
        ids=["AccountUsers", "CampaignGroups", "Campaigns", "Creatives", "AdDirectSponsoredContents"],
    )
    def test_request_params(self, stream_cls, slice, expected):
        stream = stream_cls(TEST_CONFIG)
        result = stream.request_params(stream_state={}, stream_slice=slice)
        assert expected == result

    @pytest.mark.parametrize(
        "stream_cls, state, records_slice, expected",
        [
            (AccountUsers, {"lastModified": 1}, [{"lastModified": 2}], [{"lastModified": 2}]),
            (CampaignGroups, {"lastModified": 3}, [{"lastModified": 3}], [{"lastModified": 3}]),
            (Campaigns, {}, [], []),
            (Creatives, {}, [], []),
        ],
        ids=[
            "AccountUsers",
            "CampaignGroups",
            "Campaigns",
            "Creatives",
        ],
    )
    def test_filter_records_newer_than_state(self, stream_cls, state, records_slice, expected):
        stream = stream_cls(TEST_CONFIG)
        result = list(stream.filter_records_newer_than_state(state, records_slice))
        assert result == expected


class TestLinkedInAdsAnalyticsStream:
    @pytest.mark.parametrize(
        "stream_cls, expected",
        [
            (AdCampaignAnalytics, {"q": "analytics", "pivot": "CAMPAIGN", "timeGranularity": "DAILY"}),
            (AdCreativeAnalytics, {"q": "analytics", "pivot": "CREATIVE", "timeGranularity": "DAILY"}),
        ],
        ids=[
            "AdCampaignAnalytics",
            "AdCreativeAnalytics",
        ],
    )
    def test_base_analytics_params(self, stream_cls, expected):
        stream = stream_cls(TEST_CONFIG)
        result = stream.base_analytics_params
        assert result == expected

    @pytest.mark.parametrize(
        "stream_cls, slice, expected",
        [
            (
                AdCampaignAnalytics,
                {
                    "dateRange": {"start.day": 1, "start.month": 1, "start.year": 1, "end.day": 2, "end.month": 2, "end.year": 2},
                    "fields": ["field1", "field2"],
                },
                {
                    "q": "analytics",
                    "pivot": "CAMPAIGN",
                    "timeGranularity": "DAILY",
                    "campaigns[0]": "urn:li:sponsoredCampaign:None",
                    "dateRange.start.day": 1,
                    "dateRange.start.month": 1,
                    "dateRange.start.year": 1,
                    "dateRange.end.day": 2,
                    "dateRange.end.month": 2,
                    "dateRange.end.year": 2,
                    "fields": [
                        "field1",
                        "field2",
                    ],
                },
            ),
            (
                AdCreativeAnalytics,
                {
                    "dateRange": {
                        "start.day": 1,
                        "start.month": 1,
                        "start.year": 1,
                        "end.day": 2,
                        "end.month": 2,
                        "end.year": 2,
                    },
                    "fields": [
                        "field1",
                        "field2",
                    ],
                },
                {
                    "q": "analytics",
                    "pivot": "CREATIVE",
                    "timeGranularity": "DAILY",
                    "creatives[0]": "urn:li:sponsoredCreative:None",
                    "dateRange.start.day": 1,
                    "dateRange.start.month": 1,
                    "dateRange.start.year": 1,
                    "dateRange.end.day": 2,
                    "dateRange.end.month": 2,
                    "dateRange.end.year": 2,
                    "fields": [
                        "field1",
                        "field2",
                    ],
                },
            ),
        ],
        ids=[
            "AdCampaignAnalytics",
            "AdCreativeAnalytics",
        ],
    )
    def test_request_params(self, stream_cls, slice, expected):
        stream = stream_cls(TEST_CONFIG)
        result = stream.request_params(stream_state={}, stream_slice=slice)
        assert expected == result


def test_retry_get_access_token(requests_mock):
    requests_mock.register_uri(
        "POST",
        "https://www.linkedin.com/oauth/v2/accessToken",
        [{"status_code": 429}, {"status_code": 429}, {"status_code": 200, "json": {"access_token": "token", "expires_in": 3600}}],
    )
    auth = LinkedinAdsOAuth2Authenticator(
        token_refresh_endpoint="https://www.linkedin.com/oauth/v2/accessToken",
        client_id="client_id",
        client_secret="client_secret",
        refresh_token="refresh_token",
    )
    token = auth.get_access_token()
    assert len(requests_mock.request_history) == 3
    assert token == "token"
