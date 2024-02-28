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
