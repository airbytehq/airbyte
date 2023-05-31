#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from source_strava.source import SourceStrava


def test_source_streams(config):
    streams = SourceStrava().streams(config=config)
    assert len(streams) == 2


def test_source_check_connection_success(config, requests_mock):
    requests_mock.post("https://www.strava.com/oauth/token", json={"access_token": "my_access_token", "expires_in": 64000})
    results = SourceStrava().check_connection(logger=None, config=config)
    assert results == (True, None)


def test_source_check_connection_failed(config, requests_mock):
    requests_mock.post("https://www.strava.com/oauth/token", status_code=401)
    results = SourceStrava().check_connection(logger=None, config=config)
    assert results == (False, "HTTPError('401 Client Error: None for url: https://www.strava.com/oauth/token')")
