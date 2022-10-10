#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json
import os
from unittest.mock import MagicMock

from airbyte_cdk.sources.streams.http.auth.core import NoAuth
from source_youtube_analytics.source import SourceYoutubeAnalytics


def test_check_connection(requests_mock):
    access_token = "token"
    mock_oauth_call = requests_mock.post("https://oauth2.googleapis.com/token", json={"access_token": access_token, "expires_in": 0})

    mock_jobs_call = requests_mock.get("https://youtubereporting.googleapis.com/v1/jobs", json={"jobs": [1, 2, 3]})

    source = SourceYoutubeAnalytics()
    logger_mock, config_mock = MagicMock(), MagicMock()
    assert source.check_connection(logger_mock, config_mock) == (True, None)
    assert mock_oauth_call.called_once
    assert mock_jobs_call.called_once
    assert mock_jobs_call.last_request.headers["Authorization"] == "Bearer " + access_token


def test_streams(requests_mock):
    requests_mock.get("https://youtubereporting.googleapis.com/v1/jobs", json={})

    with open(os.path.join(os.path.dirname(__file__), "../source_youtube_analytics/defaults/channel_reports.json")) as fp:
        channel_reports = json.load(fp)

    source = SourceYoutubeAnalytics()
    source.get_authenticator = MagicMock(return_value=NoAuth())
    config_mock = MagicMock()
    streams = source.streams(config_mock)
    assert len(streams) == len(channel_reports)
