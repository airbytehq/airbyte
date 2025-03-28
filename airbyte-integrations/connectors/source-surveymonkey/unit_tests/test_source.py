#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from source_surveymonkey.source import SourceSurveymonkey


source_config = {"start_date": "2021-01-01T00:00:00", "access_token": "something"}
new_source_config = {
    "start_date": "2021-01-01T00:00:00",
    "origin": "USA",
    "credentials": {"auth_method": "something", "access_token": "something", "client_secret": "client_secret", "client_id": "client_id"},
}


def test_source_streams():
    streams = SourceSurveymonkey().streams(config=new_source_config)
    assert len(streams) == 6


def test_source_check_connection_failed_missing_scopes(requests_mock):
    requests_mock.get("https://api.surveymonkey.com/v3/users/me", json={"scopes": {"granted": ["surveys_read", "users_read"]}})

    results = SourceSurveymonkey().check_connection(logger=None, config=new_source_config)
    assert results == (False, "missed required scopes: responses_read_detail")
