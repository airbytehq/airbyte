#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#
import logging
from typing import Any, Dict, List

import pytest
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.manifest_declarative_source import ManifestDeclarativeSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.exceptions import DefaultBackoffException
from airbyte_cdk.sources.streams.http.requests_native_auth import Oauth2Authenticator, TokenAuthenticator
from conftest import find_stream
from source_linkedin_ads.source import SourceLinkedinAds

logger = logging.getLogger("airbyte")

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

    @staticmethod
    def _mock_initialize_cache_for_parent_streams(stream_configs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        parent_streams = set()

        def update_with_cache_parent_configs(parent_configs: list[dict[str, Any]]) -> None:
            for parent_config in parent_configs:
                parent_streams.add(parent_config["stream"]["name"])
                parent_config["stream"]["retriever"]["requester"]["use_cache"] = False

        for stream_config in stream_configs:
            if stream_config.get("incremental_sync", {}).get("parent_stream"):
                parent_streams.add(stream_config["incremental_sync"]["parent_stream"]["name"])
                stream_config["incremental_sync"]["parent_stream"]["retriever"]["requester"]["use_cache"] = False

            elif stream_config.get("retriever", {}).get("partition_router", {}):
                partition_router = stream_config["retriever"]["partition_router"]

                if isinstance(partition_router, dict) and partition_router.get("parent_stream_configs"):
                    update_with_cache_parent_configs(partition_router["parent_stream_configs"])
                elif isinstance(partition_router, list):
                    for router in partition_router:
                        if router.get("parent_stream_configs"):
                            update_with_cache_parent_configs(router["parent_stream_configs"])

        for stream_config in stream_configs:
            if stream_config["name"] in parent_streams:
                stream_config["retriever"]["requester"]["use_cache"] = False

        return stream_configs

    @pytest.mark.parametrize("error_code", [429, 500, 503])
    def test_should_retry_on_error(self, error_code, requests_mock, mocker):
        # Define a helper function
        mocker.patch.object(ManifestDeclarativeSource, "_initialize_cache_for_parent_streams", side_effect=self._mock_initialize_cache_for_parent_streams)
        mocker.patch("time.sleep", lambda x: None)
        stream = find_stream("accounts", TEST_CONFIG)
        requests_mock.register_uri(
            "GET", "https://api.linkedin.com/rest/adAccounts", [{"status_code": error_code, "json": {"elements": []}}]
        )
        stream.exit_on_rate_limit = True

        with pytest.raises(DefaultBackoffException):
            list(stream.read_records(sync_mode=SyncMode.full_refresh))

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

    @pytest.mark.parametrize(
        ("status_code", "is_connection_successful", "error_msg"),
        (
                (
                        400,
                        False,
                        (
                                "Bad request. Please check your request parameters."
                        ),
                ),
                (
                        403,
                        False,
                        (
                                "Forbidden. You don't have permission to access this resource."
                        ),
                ),
                (200, True, None),
        ),
    )
    def test_check_connection(self, requests_mock, status_code, is_connection_successful, error_msg, mocker):
        mocker.patch("time.sleep", lambda x: None)
        json = {"elements": [{"data": []}] * 500} if 200 >= status_code < 300 else {}
        requests_mock.register_uri(
            "GET",
            "https://api.linkedin.com/rest/adAccounts?q=search&pageSize=500",
            status_code=status_code,
            json=json,
        )
        success, error = self._instance.check_connection(logger=logger, config=TEST_CONFIG)
        assert success is is_connection_successful
        assert error == error_msg


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
