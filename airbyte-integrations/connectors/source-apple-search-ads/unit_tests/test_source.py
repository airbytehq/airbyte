#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

from source_apple_search_ads.source import SourceAppleSearchAds

import responses

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
        "https://api.searchads.apple.com/api/v4/me",
        json={"id": "My ID"},
    )
    responses.add(
        responses.POST,
        "https://appleid.apple.com/auth/oauth2/token",
        json={"access_token": "my_token"}
    )

@responses.activate
def test_check_connection(mocker):
    setup_responses()
    source = SourceAppleSearchAds()
    logger_mock = MagicMock()
    assert source.check_connection(logger_mock, DEFAULT_CONFIG) == (True, None)

@responses.activate
def test_streams(mocker):
    setup_responses()
    source = SourceAppleSearchAds()
    streams = source.streams(DEFAULT_CONFIG)
    expected_streams_number = 12
    assert len(streams) == expected_streams_number
