#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import Mock

import pytest
from airbyte_cdk.models import SyncMode
from source_surveymonkey.streams import SurveyIds, Surveys


@pytest.mark.parametrize("stream, expected_records_file, stream_slice", [
    (SurveyIds, "records_survey_ids.json", None),
    (Surveys, "records_surveys.json", {"survey_id": "307785415"})
])
def test_survey_stream_read_records(requests_mock, args_mock, read_json, stream, expected_records_file, stream_slice):
    requests_mock.get(
        "https://api.surveymonkey.com/v3/surveys",
        [
            {
                "status_code": 429,
                "headers": {"X-Ratelimit-App-Global-Minute-Remaining": "0"},
                "json": {
                    "error": {
                        "id": 1040,
                        "name": "Rate limit reached",
                        "docs": "https://developer.surveymonkey.com/api/v3/#error-codes",
                        "message": "Too many requests were made, try again later.",
                        "http_status_code": 429,
                    }
                },
            },
            {"status_code": 200, "headers": {"X-Ratelimit-App-Global-Minute-Remaining": "100"},
             "json": read_json("response_survey_ids.json")},
        ],
    )
    requests_mock.get("https://api.surveymonkey.com/v3/surveys/307785415/details", json=read_json("response_survey_details.json"))
    stream_instance = stream(**args_mock)
    stream_instance.default_backoff_time = 3
    records = stream_instance.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice)
    expected_records = read_json(expected_records_file)
    assert list(records) == expected_records


@pytest.mark.parametrize("additional_arguments, expected_slices", [
    ({}, [{"survey_id": "307785415"}, {"survey_id": "307785388"}]),
    ({"survey_ids": ["307785415"]}, [{"survey_id": "307785415"}])
])
def test_survey_slices(requests_mock, args_mock, read_json, additional_arguments, expected_slices):
    if not additional_arguments:
        requests_mock.get("https://api.surveymonkey.com/v3/surveys", json=read_json("response_survey_ids.json"))
    args_mock.update(additional_arguments)
    stream_slices = Surveys(**args_mock).stream_slices()
    assert list(stream_slices) == expected_slices


@pytest.mark.parametrize("endpoint, records_filename", [
    ("survey_pages", "records_survey_pages.json"),
    ("survey_questions", "records_survey_questions.json"),
    ("survey_collectors", "records_survey_collectors.json")
])
def test_survey_data(requests_mock, read_records, read_json, endpoint, records_filename):
    requests_mock.get("https://api.surveymonkey.com/v3/surveys/307785415/details", json=read_json("response_survey_details.json"))
    requests_mock.get("https://api.surveymonkey.com/v3/surveys/307785415/collectors", json=read_json("response_survey_collectors.json"))
    records = read_records(endpoint)
    expected_records = read_json(records_filename)
    assert list(records) == expected_records


def test_surveys_next_page_token(args_mock):
    args = {**args_mock, **{"survey_ids": ["307785415"]}}
    stream = SurveyIds(**args)
    mockresponse = Mock()
    mockresponse.json.return_value = {
        "links": {
            "self": "https://api.surveymonkey.com/v3/surveys?page=1&per_page=50",
            "next": "https://api.surveymonkey.com/v3/surveys?page=2&per_page=50",
            "last": "https://api.surveymonkey.com/v3/surveys?page=5&per_page=50",
        }
    }

    params = stream.next_page_token(mockresponse)
    assert params == {"page": "2", "per_page": "50"}
