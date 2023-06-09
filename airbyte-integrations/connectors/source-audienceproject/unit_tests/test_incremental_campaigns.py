#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import requests
from pytest import fixture
from source_audienceproject.auth import AudienceProjectAuthenticator
from source_audienceproject.streams import AudienceprojectStream
from source_audienceproject.streams_campaigns import Campaigns

test_config = {
  "credentials":
  {
    "type": "access_token",
    "access_token": "geA5QTa8TzXwsLegq4c1WgYyQ81ROX8uMhY0gu2f"
  },
  "start_date": "2022-01-01",
  "end_date": "2023-12-28"
}


@fixture
def patch_incremental_campaigns(mocker):
    # Mock abstract methods to enable instantiating abstract class.
    mocker.patch.object(Campaigns, "primary_key", None)


def authorization():
    auth = AudienceProjectAuthenticator(
        url_base=AudienceprojectStream.oauth_url_base,
        config=test_config
    )
    return auth


def fetch_data(url_base, auth_header):
    try:
        resp = requests.get(url=url_base, headers=auth_header)
        if resp:
            return resp
        return False
    except Exception as e:
        return e


def test_cursor_field(patch_incremental_campaigns):
    auth = authorization()
    stream = Campaigns(auth, config=test_config)
    expected_cursor_field = "created"
    assert stream.cursor_field == expected_cursor_field


def test_token(patch_incremental_campaigns):
    auth = authorization()
    try:
        auth_header = auth.get_auth_header()
        return auth_header
    except Exception as e:
        assert str(e) == "Unauthorized Token"


def test_parse_response(patch_incremental_campaigns):
    auth = authorization()
    stream = Campaigns(auth, config=test_config)
    auth_header = test_token(patch_incremental_campaigns)
    if auth_header:
        url_base = AudienceprojectStream.url_base + "campaigns"
        response = fetch_data(url_base, auth_header)
        if response:
            expected_response = isinstance(response.json().get("data")[0], dict)
            parse_resp = list(stream.parse_response(response))
            fetched_resp = isinstance(parse_resp[0], dict)
            assert fetched_resp == expected_response
        else:
            expected_response = [{}]
            assert stream.parse_response([{}]) == expected_response


def test_time_interval(patch_incremental_campaigns):
    try:
        stream_start, stream_end = AudienceprojectStream._get_time_interval(
            test_config.get("start_date"),
            test_config.get("end_date")
        )
        assert test_config.get("start_date") == str(stream_start)
        assert test_config.get("end_date") == str(stream_end)
    except ValueError:
        print("Value Error start date is not before end date.")
