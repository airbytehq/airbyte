#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from source_surveymonkey.source import SourceSurveymonkey

source_config = {"start_date": "2021-01-01T00:00:00", "access_token": "something"}


def test_source_streams():
    streams = SourceSurveymonkey().streams(config=source_config)
    assert len(streams) == 4


def test_source_check_connection(requests_mock):
    requests_mock.get(
        "https://api.surveymonkey.com/v3/users/me", json={"scopes": {"granted": ["responses_read_detail", "surveys_read", "users_read"]}}
    )

    results = SourceSurveymonkey().check_connection(logger=None, config=source_config)
    assert results == (True, None)


def test_source_check_connection_failed(requests_mock):
    requests_mock.get("https://api.surveymonkey.com/v3/users/me", json={"scopes": {"granted": ["surveys_read", "users_read"]}})

    results = SourceSurveymonkey().check_connection(logger=None, config=source_config)
    assert results == (False, "missed required scopes: responses_read_detail")
