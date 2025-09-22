#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from unittest.mock import Mock

import pytest
from source_surveymonkey import SourceSurveymonkey
from source_surveymonkey.streams import SurveyIds, Surveys

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.types import StreamSlice


def deep_sort_dict(obj):
    """Recursively sort dictionary keys and list items for consistent comparison"""
    if isinstance(obj, dict):
        return {k: deep_sort_dict(v) for k, v in sorted(obj.items())}
    elif isinstance(obj, list):
        return [deep_sort_dict(item) for item in obj]
    else:
        return obj


@pytest.mark.parametrize(
    "stream, expected_records_file, stream_slice",
    [(SurveyIds, "records_survey_ids.json", None), (Surveys, "records_surveys.json", {"survey_id": "307785415"})],
)
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
            {
                "status_code": 200,
                "headers": {"X-Ratelimit-App-Global-Minute-Remaining": "100"},
                "json": read_json("response_survey_ids.json"),
            },
        ],
    )
    requests_mock.get("https://api.surveymonkey.com/v3/surveys/307785415/details", json=read_json("response_survey_details.json"))
    stream_instance = stream(**args_mock)
    stream_instance.default_backoff_time = 3
    records = stream_instance.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice)
    expected_records = read_json(expected_records_file)
    assert list(records) == expected_records


@pytest.mark.parametrize(
    "additional_arguments, expected_slices",
    [({}, [{"survey_id": "307785415"}, {"survey_id": "307785388"}]), ({"survey_ids": ["307785415"]}, [{"survey_id": "307785415"}])],
)
def test_survey_slices(requests_mock, args_mock, read_json, additional_arguments, expected_slices):
    if not additional_arguments:
        requests_mock.get("https://api.surveymonkey.com/v3/surveys", json=read_json("response_survey_ids.json"))
    args_mock.update(additional_arguments)
    surveys_stream = Surveys(**args_mock)
    mock_session = Mock()
    mock_session.auth = Mock()
    surveys_stream._session = mock_session
    stream_slices = surveys_stream.stream_slices()
    assert list(stream_slices) == expected_slices


@pytest.mark.parametrize(
    "endpoint, records_filename",
    [
        ("survey_pages", "records_survey_pages.json"),
        ("survey_questions", "records_survey_questions.json"),
        ("survey_collectors", "records_survey_collectors.json"),
    ],
)
def test_survey_data(requests_mock, read_json, endpoint, records_filename, config):
    requests_mock.get("https://api.surveymonkey.com/v3/surveys/307785415/details", json=read_json("response_survey_details.json"))
    requests_mock.get("https://api.surveymonkey.com/v3/surveys/307785415/collectors", json=read_json("response_survey_collectors.json"))

    source = SourceSurveymonkey(catalog=None, config=config, state=None)
    stream = next(filter(lambda x: x.name == endpoint, source.streams(config=config)))

    # Use CDK v7 pattern - generate_partitions instead of read_records
    records = []
    try:
        for partition in stream.generate_partitions():
            records.extend(list(partition.read()))
    except AttributeError:
        slice_obj = StreamSlice(partition={"survey_id": "307785415"}, cursor_slice={})
        records = list(stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=slice_obj))

    expected_records = read_json(records_filename)

    actual_records = []
    for record in records:
        if hasattr(record, "data"):
            actual_records.append(record.data)
        elif hasattr(record, "__dict__"):
            actual_records.append(record.__dict__)
        else:
            actual_records.append(record)

    actual_json = json.dumps(deep_sort_dict(actual_records), sort_keys=True)
    expected_json = json.dumps(deep_sort_dict(expected_records), sort_keys=True)

    assert actual_json == expected_json


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
