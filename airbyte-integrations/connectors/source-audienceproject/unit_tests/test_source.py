#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

from source_audienceproject.auth import AudienceProjectAuthenticator
from source_audienceproject.source import SourceAudienceproject
from source_audienceproject.streams import AudienceprojectStream

test_config = {
  "credentials":
  {
    "type": "access_token",
    "access_token": "xyz"
  },
  "start_date": "2022-01-01",
  "end_date": "2023-12-28"
}


def test_check_connection(mocker):
    auth = AudienceProjectAuthenticator(
        url_base=AudienceprojectStream.oauth_url_base,
        config=test_config
    )
    try:
        auth.get_auth_header()
    except Exception as e:
        assert "Unauthorized Token" == str(e)


def test_streams(mocker):
    source = SourceAudienceproject()
    config_mock = MagicMock()
    streams = source.streams(config_mock)
    expected_streams_number = 5
    assert len(streams) == expected_streams_number
