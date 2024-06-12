#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from unittest.mock import Mock, patch

import pytest
import requests
from airbyte_cdk.sources.streams.http.requests_native_auth import Oauth2Authenticator, TokenAuthenticator
from airbyte_cdk.utils import AirbyteTracedException
from source_linkedin_ads.source import (
    Accounts,
    AccountUsers,
    AdCampaignAnalytics,
    AdCreativeAnalytics,
    CampaignGroups,
    Campaigns,
    Creatives,
    SourceLinkedinAds,
)
from source_linkedin_ads.streams import LINKEDIN_VERSION_API

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
        "stream_cls",
        [
            Accounts,
            AccountUsers,
            CampaignGroups,
            Campaigns,
            Creatives,
            AdCampaignAnalytics,
            AdCreativeAnalytics,
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
    def test_streams(self, stream_cls):
        streams = self._instance.streams(config=TEST_CONFIG)
        for stream in streams:
            if stream_cls in streams:
                assert isinstance(stream, stream_cls)

    def test_custom_streams(self):
        config = {"ad_analytics_reports": [{"name": "ShareAdByMonth", "pivot_by": "COMPANY", "time_granularity": "MONTHLY"}], **TEST_CONFIG}
        for stream in self._instance.get_custom_ad_analytics_reports(config=config):
            assert isinstance(stream, AdCampaignAnalytics)

    @patch("source_linkedin_ads.source.Accounts.check_availability")
    def test_check_connection(self, check_availability_mock):
        check_availability_mock.return_value = (True, None)
        is_available, error = self._instance.check_connection(logger=Mock(), config=TEST_CONFIG)
        assert is_available
        assert not error

    @patch("source_linkedin_ads.source.Accounts.check_availability")
    def test_check_connection_failure(self, check_availability_mock):
        check_availability_mock.side_effect = Exception("Not available")
        is_available, error = self._instance.check_connection(logger=Mock(), config=TEST_CONFIG)
        assert not is_available
        assert str(error) == "Not available"

    @pytest.mark.parametrize(
        "stream_cls, stream_slice, expected",
        [
            (Accounts, None, "adAccounts"),
            (AccountUsers, None, "adAccountUsers"),
            (CampaignGroups, {"account_id": 123}, "adAccounts/123/adCampaignGroups"),
            (Campaigns, {"account_id": 123}, "adAccounts/123/adCampaigns"),
            (Creatives, {"account_id": 123}, "adAccounts/123/creatives"),
            (AdCampaignAnalytics, None, "adAnalytics"),
            (AdCreativeAnalytics, None, "adAnalytics"),
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
    def test_path(self, stream_cls, stream_slice, expected):
        stream = stream_cls(config=TEST_CONFIG)
        result = stream.path(stream_slice=stream_slice)
        assert result == expected


class TestLinkedinAdsStream:
    stream: Accounts = Accounts(TEST_CONFIG)
    url = f"{stream.url_base}/{stream.path()}"

    def test_accounts(self):
        result = self.stream.accounts
        assert result == ",".join(map(str, TEST_CONFIG["account_ids"]))

    @pytest.mark.parametrize(
        "response_json, expected",
        (
            ({"elements": []}, None),
            (
                {"elements": [{"data": []}] * 500, "metadata": {"nextPageToken": "next_page_token"}, "paging": {"start": 0, "total": 600}},
                {"pageToken": "next_page_token"},
            ),
        ),
    )
    def test_next_page_token(self, requests_mock, response_json, expected):
        requests_mock.get(self.url, json=response_json)
        test_response = requests.get(self.url)

        result = self.stream.next_page_token(test_response)
        assert expected == result

    def test_request_params(self):
        expected = "pageSize=500&q=search&search=(id:(values:List(urn%3Ali%3AsponsoredAccount%3A1,urn%3Ali%3AsponsoredAccount%3A2)))"
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
        expected = {"X-RestLi-Protocol-Version": "2.0.0", "Linkedin-Version": LINKEDIN_VERSION_API}
        result = self.stream.request_headers(stream_state={})
        assert result == expected


class TestAccountUsers:
    stream: AccountUsers = AccountUsers(TEST_CONFIG)

    def test_state_checkpoint_interval(self):
        assert self.stream.state_checkpoint_interval == 100

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
                "count=500&q=accounts&accounts=urn:li:sponsoredAccount:123",
            ),
            (
                CampaignGroups,
                {"account_id": 123},
                "pageSize=500&q=search&search=(status:(values:List(ACTIVE,ARCHIVED,CANCELED,DRAFT,PAUSED,PENDING_DELETION,REMOVED)))",
            ),
            (
                Campaigns,
                {"account_id": 123},
                "pageSize=500&q=search&search=(status:(values:List(ACTIVE,PAUSED,ARCHIVED,COMPLETED,CANCELED,DRAFT,PENDING_DELETION,REMOVED)))",
            ),
            (
                Creatives,
                {"campaign_id": 123},
                "pageSize=100&q=criteria",
            ),
        ],
        ids=["AccountUsers", "CampaignGroups", "Campaigns", "Creatives"],
    )
    def test_request_params(self, stream_cls, slice, expected):
        stream = stream_cls(TEST_CONFIG)
        result = stream.request_params(stream_state={}, stream_slice=slice)
        assert result == expected

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
            (AdCampaignAnalytics, {"pivot": "(value:CAMPAIGN)", "q": "analytics", "timeGranularity": "(value:DAILY)"}),
            (AdCreativeAnalytics, {"pivot": "(value:CREATIVE)", "q": "analytics", "timeGranularity": "(value:DAILY)"}),
        ],
        ids=[
            "AdCampaignAnalytics",
            "AdCreativeAnalytics",
        ],
    )
    def test_base_analytics_params(self, stream_cls, expected):
        stream = stream_cls(config=TEST_CONFIG)
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
                "q=analytics&pivot=(value:CAMPAIGN)&timeGranularity=(value:DAILY)&dateRange=(start:(year:1,month:1,day:1),end:(year:2,month:2,day:2))&fields=%5B%27field1%27,+%27field2%27%5D&campaigns=List(urn%3Ali%3AsponsoredCampaign%3ANone)",
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
                    "creative_id": "urn:li:sponsoredCreative:1234",
                },
                "q=analytics&pivot=(value:CREATIVE)&timeGranularity=(value:DAILY)&dateRange=(start:(year:1,month:1,day:1),end:(year:2,month:2,day:2))&fields=%5B%27field1%27,+%27field2%27%5D&creatives=List(urn%3Ali%3AsponsoredCreative%3A1234)",
            ),
        ],
        ids=[
            "AdCampaignAnalytics",
            "AdCreativeAnalytics",
        ],
    )
    def test_request_params(self, stream_cls, slice, expected):
        stream = stream_cls(config=TEST_CONFIG)
        result = stream.request_params(stream_state={}, stream_slice=slice)
        assert expected == result


def test_retry_get_access_token(requests_mock):
    requests_mock.register_uri(
        "POST",
        "https://www.linkedin.com/oauth/v2/accessToken",
        [{"status_code": 429}, {"status_code": 429}, {"status_code": 200, "json": {"access_token": "token", "expires_in": 3600}}],
    )
    auth = Oauth2Authenticator(
        token_refresh_endpoint="https://www.linkedin.com/oauth/v2/accessToken",
        client_id="client_id",
        client_secret="client_secret",
        refresh_token="refresh_token",
    )
    token = auth.get_access_token()
    assert len(requests_mock.request_history) == 3
    assert token == "token"


@pytest.mark.parametrize(
    "record, expected",
    [
        ({}, {}),
        ({"lastModified": "2021-05-27 11:59:53.710000"}, {"lastModified": "2021-05-27T11:59:53.710000+00:00"}),
        ({"lastModified": None}, {"lastModified": None}),
        ({"lastModified": ""}, {"lastModified": ""}),
    ],
    ids=["empty_record", "transformed_record", "null_value", "empty_value"],
)
def test_date_time_to_rfc3339(record, expected):
    stream = Accounts(TEST_CONFIG)
    result = stream._date_time_to_rfc3339(record)
    assert result == expected


def test_duplicated_custom_ad_analytics_report():
    with pytest.raises(AirbyteTracedException) as e:
        SourceLinkedinAds().streams(TEST_CONFIG_DUPLICATE_CUSTOM_AD_ANALYTICS_REPORTS)
    expected_message = "Stream names for Custom Ad Analytics reports should be unique, duplicated streams: {'ShareAdByMonth'}"
    assert e.value.message == expected_message
