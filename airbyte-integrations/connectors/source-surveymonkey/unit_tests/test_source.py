#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
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


def test_source_check_connection_old_config(requests_mock):
    requests_mock.get(
        "https://api.surveymonkey.com/v3/users/me", json={"scopes": {"granted": ["responses_read_detail", "surveys_read", "users_read"]}}
    )

    results = SourceSurveymonkey().check_connection(logger=None, config=source_config)
    assert results == (True, None)


def test_source_check_connection_new_config(requests_mock):
    requests_mock.get(
        "https://api.surveymonkey.com/v3/users/me", json={"scopes": {"granted": ["responses_read_detail", "surveys_read", "users_read"]}}
    )

    results = SourceSurveymonkey().check_connection(logger=None, config=new_source_config)
    assert results == (True, None)


def test_source_check_connection_failed_missing_scopes(requests_mock):
    requests_mock.get("https://api.surveymonkey.com/v3/users/me", json={"scopes": {"granted": ["surveys_read", "users_read"]}})

    results = SourceSurveymonkey().check_connection(logger=None, config=new_source_config)
    assert results == (False, "missed required scopes: responses_read_detail")


@pytest.mark.parametrize(
    "config, err_msg",
    [
        (
            {
                "start_date": "2021-01-01T00:00:00",
                "origin": "USA",
            },
            "credentials fields are not provided",
        ),
        (
            {
                "start_date": "2021-01-01T00:00:00",
                "origin": "USA",
                "credentials": {"access_token": "something", "client_secret": "client_secret", "client_id": "client_id"},
            },
            "auth_method in credentials is not provided",
        ),
        (
            {
                "start_date": "2021-01-01T00:00:00",
                "origin": "USA",
                "credentials": {"auth_method": "something", "client_secret": "client_secret", "client_id": "client_id"},
            },
            "access_token in credentials is not provided",
        ),
    ],
)
def test_source_check_connection_failed_missing_credentials(config, err_msg):
    results = SourceSurveymonkey().check_connection(logger=None, config=config)
    assert results == (False, err_msg)
