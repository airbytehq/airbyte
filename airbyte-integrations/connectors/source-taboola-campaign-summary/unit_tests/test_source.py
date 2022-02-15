#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import responses

from source_taboola_campaign_summary.source import SourceTaboolaCampaignSummary

DEFAULT_CONFIG = {
  "client_id": "client_id",
  "client_secret": "secret",
  "account_id": "account_id"
}

def setup_responses():
    responses.add(
        responses.GET,
        "https://backstage.taboola.com/backstage/api/1.0/users/current/account",
        json={"id": "My ID"},
    )
    responses.add(
        responses.POST,
        "https://backstage.taboola.com/backstage/oauth/token",
        json={"access_token": "my_token"}
    )

@responses.activate
def test_check_connection(mocker):
    setup_responses()
    source = SourceTaboolaCampaignSummary()
    logger_mock = MagicMock()
    assert source.check_connection(logger_mock, DEFAULT_CONFIG) == (True, None)

@responses.activate
def test_streams(mocker):
    setup_responses()
    source = SourceTaboolaCampaignSummary()
    streams = source.streams(DEFAULT_CONFIG)
    expected_streams_number = 3
    assert len(streams) == expected_streams_number
