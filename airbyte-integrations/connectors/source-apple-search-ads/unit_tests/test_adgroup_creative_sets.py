#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
import responses

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http.auth.core import NoAuth

from source_apple_search_ads.authenticator import AppleSearchAdsAuthenticator
from source_apple_search_ads.basic_streams import AppleSearchAdsStream
from source_apple_search_ads.with_campaign_streams import AdgroupCreativeSets

DEFAULT_CONFIG = {
  "client_id": "client_id",
  "team_id": "secret",
  "key_id": "account_id",
  "org_id": "org_id",
  "private_key": """-----BEGIN PRIVATE KEY-----
MIIBVQIBADANBgkqhkiG9w0BAQEFAASCAT8wggE7AgEAAkEAvpFnccjANDjqo4dZ
jYqxbn8CbOuxUo0dDsUMDiO5rxTFxYCsGQkuSZxMI5/yKmJ1/8GqLOUusAvsETDB
lXo3hwIDAQABAkAu+nFh33diaFWPkqJE/lfXQYA7ka7ZBuiO54ydP7laq3r4bDWB
Pu816K0oGX9PcCiomEa8tKCycQOxC0WumqJBAiEA8K5cexEqbxrBzJ7Ys1Uaai7L
KALWLKNQ4Knf2RJm/8kCIQDKsoDzx9jojuEKkQhI5WONa6nj4kHBOYO92tCENkBE
zwIhAKePHD9pkftLy4RjSkZ/hyZJcZJndygYgyQF4BvF3gNRAiAVNTIKz6khQ/nF
ykDsp5uP62jeIAkzN1pSXfedLbPxvwIhAIJpDcCY/C9mjzsv6/pc9ap92TCKnMwK
57lm5MTC3Z2m
-----END PRIVATE KEY-----""",
    "algorithm": "RS256"
}

def setup_responses():
    responses.add(
        responses.GET,
        "https://api.searchads.apple.com/api/v4/campaigns",
        json={
            "data": [{
                "id": 1001,
                "adamId": 2002
            }, {
                "id": 1002,
                "adamId": 2002
            }],
            "pagination": {
                "totalResults": 1,
                "startIndex": 0,
                "itemsPerPage": 1
            }
        },
    )
    responses.add(
        responses.POST,
        "https://appleid.apple.com/auth/oauth2/token",
        json={"access_token": "my_token"}
    )

@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(AppleSearchAdsStream, "path", "v0/example_endpoint")
    mocker.patch.object(AppleSearchAdsStream, "primary_key", "test_primary_key")
    mocker.patch.object(AppleSearchAdsStream, "__abstractmethods__", set())


def test_adgroup_creative_sets_request_params(patch_base_class):
    stream = AdgroupCreativeSets(org_id=DEFAULT_CONFIG["org_id"], authenticator=NoAuth)

    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_params = {"limit": 1000, "offset": 0}

    assert stream.request_params(**inputs) == expected_params


def test_adgroup_creative_sets_next_page_token(patch_base_class):
    stream = AdgroupCreativeSets(org_id=DEFAULT_CONFIG["org_id"], authenticator=NoAuth)

    response = MagicMock()
    response.json.return_value = {"pagination": {"totalResults": 100, "startIndex": 0, "itemsPerPage": 10}}
    inputs = {"response": response}
    expected_token = {"limit": 1000, "offset": 10}

    assert stream.next_page_token(**inputs) == expected_token


def test_adgroup_creative_sets_parse_response(patch_base_class):
    stream = AdgroupCreativeSets(org_id=DEFAULT_CONFIG["org_id"], authenticator=NoAuth)

    records = [
        {"key": "value"},
        {"key": "value2"},
    ]
    response = MagicMock()
    response.json.return_value = {"data": records}
    inputs = {"response": response}
    expected_parsed_object = records

    assert list(stream.parse_response(**inputs)) == expected_parsed_object


def test_adgroup_creative_sets_request_headers(patch_base_class):
    stream = AdgroupCreativeSets(org_id=DEFAULT_CONFIG["org_id"], authenticator=NoAuth)
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_headers = {'X-AP-Context': f"orgId={DEFAULT_CONFIG['org_id']}"}
    assert stream.request_headers(**inputs) == expected_headers


def test_adgroup_creative_sets_http_method(patch_base_class):
    stream = AdgroupCreativeSets(org_id=DEFAULT_CONFIG["org_id"], authenticator=NoAuth)
    expected_method = "POST"
    assert stream.http_method == expected_method

def test_adgroup_creative_sets_request_body_json(patch_base_class):
    stream = AdgroupCreativeSets(org_id=DEFAULT_CONFIG["org_id"], authenticator=NoAuth)

    inputs = {"stream_slice": {"campaign_id": 2001}, "stream_state": None, "next_page_token": None}
    expected_params = {
        "selector": {
            "conditions": [{
                "field": "campaignId",
                "operator": "EQUALS",
                "values": [
                    2001
                ]
            }]
        }
    }

    assert stream.request_body_json(**inputs) == expected_params

@responses.activate
def test_stream_slices(patch_base_class):
    setup_responses()

    auth = AppleSearchAdsAuthenticator(
        client_id=DEFAULT_CONFIG["client_id"],
        team_id=DEFAULT_CONFIG["team_id"],
        key_id=DEFAULT_CONFIG["key_id"],
        private_key=DEFAULT_CONFIG["private_key"],
        algorithm=DEFAULT_CONFIG["algorithm"]
    )

    stream = AdgroupCreativeSets(org_id=DEFAULT_CONFIG["org_id"], authenticator=auth)
    inputs = {"sync_mode": SyncMode.incremental, "cursor_field": [], "stream_state": {}}
    expected_stream_slice = [
        {"adam_id": 2002, "campaign_id": 1001},
        {"adam_id": 2002, "campaign_id": 1002}
    ]
    assert stream.stream_slices(**inputs) == expected_stream_slice


@pytest.mark.parametrize(
    ("http_status", "should_retry"),
    [
        (HTTPStatus.OK, False),
        (HTTPStatus.BAD_REQUEST, False),
        (HTTPStatus.TOO_MANY_REQUESTS, True),
        (HTTPStatus.INTERNAL_SERVER_ERROR, True),
    ],
)
def test_adgroup_creative_sets_should_retry(patch_base_class, http_status, should_retry):
    response_mock = MagicMock()
    response_mock.status_code = http_status
    stream = AdgroupCreativeSets(org_id=DEFAULT_CONFIG["org_id"], authenticator=NoAuth)
    assert stream.should_retry(response_mock) == should_retry


def test_adgroup_creative_sets_backoff_time(patch_base_class):
    response_mock = MagicMock()
    stream = AdgroupCreativeSets(org_id=DEFAULT_CONFIG["org_id"], authenticator=NoAuth)
    expected_backoff_time = None
    assert stream.backoff_time(response_mock) == expected_backoff_time
