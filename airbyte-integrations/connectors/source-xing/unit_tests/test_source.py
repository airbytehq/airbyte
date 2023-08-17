#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from source_xing.source import SourceXing

test_config = {
  "access_token":"xyz",
  "daily_insights":{
    "end_date":"2023-01-02",
    "start_date":"2023-01-01"
  }
}


def test_check_connection(mocker):
    auth = TokenAuthenticator(test_config["access_token"])
    try:
        auth.get_auth_header()
    except Exception as e:
        assert "Unauthorized Token" == str(e)


def test_streams(mocker):
    source = SourceXing()
    config_mock = MagicMock()
    streams = source.streams(config_mock)
    # TODO: replace this with your streams number
    expected_streams_number = 4
    assert len(streams) == expected_streams_number
