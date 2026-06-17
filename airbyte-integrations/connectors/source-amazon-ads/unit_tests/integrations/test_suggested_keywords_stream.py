# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import json
from unittest import TestCase

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse

from .ad_requests import OAuthRequestBuilder, ProfilesRequestBuilder
from .ad_requests.constants import BASE_URL
from .ad_responses import OAuthResponseBuilder, ProfilesResponseBuilder
from .ad_responses.records import ProfilesRecordBuilder
from .config import ConfigBuilder
from .utils import read_stream


_AD_GROUP_ID = 123456789
_CAMPAIGN_ID = 987654321

_SP_AD_GROUPS_RESPONSE = json.dumps(
    {
        "adGroups": [
            {
                "adGroupId": _AD_GROUP_ID,
                "campaignId": _CAMPAIGN_ID,
                "name": "Test Ad Group",
                "state": "ENABLED",
                "defaultBid": 1.0,
            }
        ],
        "totalResults": 1,
    }
)

_KEYWORD_RECOMMENDATIONS_RESPONSE = json.dumps(
    {
        "keywordTargetList": [
            {
                "keyword": "wireless earbuds",
                "recId": "rec-1234567890",
                "translation": "wireless earbuds",
                "userSelectedKeyword": False,
                "searchTermImpressionShare": 0.12,
                "searchTermImpressionRank": 8,
                "bidInfo": [
                    {
                        "rank": 1,
                        "matchType": "BROAD",
                        "bid": 120,
                        "theme": "CONVERSION_OPPORTUNITIES",
                        "suggestedBid": {"low": 95, "medium": 120, "high": 150},
                    }
                ],
            }
        ]
    }
)

_KEYWORD_RECOMMENDATIONS_EMPTY_RESPONSE = json.dumps({"keywordTargetList": []})

_KEYWORD_RECOMMENDATIONS_REQUEST_BODY = json.dumps(
    {
        "recommendationType": "KEYWORDS_FOR_ADGROUP",
        "adGroupId": _AD_GROUP_ID,
        "campaignId": _CAMPAIGN_ID,
        "maxRecommendations": 200,
    }
)

_SP_AD_GROUPS_REQUEST_BODY = json.dumps({"maxResults": 100})


class TestSuggestedKeywordsStream(TestCase):
    @property
    def _config(self):
        return ConfigBuilder().build()

    def _given_oauth_and_profiles(self, http_mocker: HttpMocker, config: dict) -> None:
        oauth_request = OAuthRequestBuilder.oauth_endpoint(
            client_id=config["client_id"], client_secred=config["client_secret"], refresh_token=config["refresh_token"]
        ).build()
        oauth_response = OAuthResponseBuilder.token_response().build()
        http_mocker.post(oauth_request, [oauth_response, oauth_response, oauth_response])
        http_mocker.get(
            ProfilesRequestBuilder.profiles_endpoint(client_id=config["client_id"], client_access_token=config["access_token"]).build(),
            ProfilesResponseBuilder.profiles_response().with_record(ProfilesRecordBuilder.profiles_record()).build(),
        )

    def _mock_sp_ad_groups(self, http_mocker: HttpMocker, config: dict, profile_id: str) -> None:
        http_mocker.post(
            HttpRequest(
                url=f"{BASE_URL}/sp/adGroups/list",
                headers={
                    "Amazon-Advertising-API-ClientId": config["client_id"],
                    "Amazon-Advertising-API-Scope": str(profile_id),
                    "Authorization": f"Bearer {config['access_token']}",
                },
                body=_SP_AD_GROUPS_REQUEST_BODY,
            ),
            HttpResponse(body=_SP_AD_GROUPS_RESPONSE, status_code=200),
        )

    def _mock_keyword_recommendations(self, http_mocker: HttpMocker, config: dict, profile_id: str, response_body: str = None) -> None:
        http_mocker.post(
            HttpRequest(
                url=f"{BASE_URL}/sp/targets/keywords/recommendations",
                headers={
                    "Amazon-Advertising-API-ClientId": config["client_id"],
                    "Amazon-Advertising-API-Scope": str(profile_id),
                    "Authorization": f"Bearer {config['access_token']}",
                },
                body=_KEYWORD_RECOMMENDATIONS_REQUEST_BODY,
            ),
            HttpResponse(body=response_body or _KEYWORD_RECOMMENDATIONS_RESPONSE, status_code=200),
        )

    @HttpMocker()
    def test_read_suggested_keywords_returns_records_with_new_api(self, http_mocker: HttpMocker):
        config = self._config
        profile_id = config["profiles"][0]

        self._given_oauth_and_profiles(http_mocker, config)
        self._mock_sp_ad_groups(http_mocker, config, profile_id)
        self._mock_keyword_recommendations(http_mocker, config, profile_id)

        output = read_stream("sponsored_product_ad_group_suggested_keywords", SyncMode.full_refresh, config)

        assert len(output.records) == 1
        record = output.records[0].record.data
        assert record["keyword"] == "wireless earbuds"
        assert record["recId"] == "rec-1234567890"
        assert record["adGroupId"] == str(_AD_GROUP_ID)
        assert record["campaignId"] == str(_CAMPAIGN_ID)
        assert record["userSelectedKeyword"] is False
        assert len(record["bidInfo"]) == 1
        assert record["bidInfo"][0]["matchType"] == "BROAD"
        assert record["bidInfo"][0]["bid"] == 120

    @HttpMocker()
    def test_read_suggested_keywords_empty_response(self, http_mocker: HttpMocker):
        config = self._config
        profile_id = config["profiles"][0]

        self._given_oauth_and_profiles(http_mocker, config)
        self._mock_sp_ad_groups(http_mocker, config, profile_id)
        self._mock_keyword_recommendations(
            http_mocker,
            config,
            profile_id,
            response_body=_KEYWORD_RECOMMENDATIONS_EMPTY_RESPONSE,
        )

        output = read_stream("sponsored_product_ad_group_suggested_keywords", SyncMode.full_refresh, config)
        assert len(output.records) == 0

    @HttpMocker()
    def test_read_suggested_keywords_422_ignored(self, http_mocker: HttpMocker):
        config = self._config
        profile_id = config["profiles"][0]

        self._given_oauth_and_profiles(http_mocker, config)
        self._mock_sp_ad_groups(http_mocker, config, profile_id)
        http_mocker.post(
            HttpRequest(
                url=f"{BASE_URL}/sp/targets/keywords/recommendations",
                headers={
                    "Amazon-Advertising-API-ClientId": config["client_id"],
                    "Amazon-Advertising-API-Scope": str(profile_id),
                    "Authorization": f"Bearer {config['access_token']}",
                },
                body=_KEYWORD_RECOMMENDATIONS_REQUEST_BODY,
            ),
            HttpResponse(body=json.dumps({"message": "Ad group has no asins"}), status_code=422),
        )

        output = read_stream("sponsored_product_ad_group_suggested_keywords", SyncMode.full_refresh, config)
        assert len(output.records) == 0
