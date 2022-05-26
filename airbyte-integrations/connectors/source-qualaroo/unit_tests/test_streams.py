#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from unittest.mock import MagicMock

from pytest import fixture
from source_qualaroo.source import QualarooStream, Responses, Surveys

from .helpers import NO_SLEEP_HEADERS, read_all_records


@fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(QualarooStream, "path", "v0/example_endpoint")
    mocker.patch.object(QualarooStream, "primary_key", "test_primary_key")
    mocker.patch.object(QualarooStream, "__abstractmethods__", set())


def test_request_params(patch_base_class, config):
    stream = QualarooStream(**config)
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": {"before": "id"}}
    expected_params = {"limit": 500, "start_date": "start_date", "before": "id"}
    assert stream.request_params(**inputs) == expected_params


def test_next_page_token(patch_base_class, config):
    stream = QualarooStream(**config)
    inputs = {"response": MagicMock()}
    expected_token = None
    assert stream.next_page_token(**inputs) == expected_token


def test_surveys_stream(requests_mock):
    mock_surveys_request = requests_mock.get(
        "https://api.qualaroo.com/api/v1/nudges?limit=500&start_date=2021-02-11T08%3A35%3A49.540Z",
        headers=NO_SLEEP_HEADERS,
        json=[{"id": "b11111111111111111111111", "name": "survey_1"}, {"id": "b22222222222222222222222", "name": "survey_2"}],
    )

    args = {"authenticator": None, "start_date": "2021-02-11T08:35:49.540Z", "survey_ids": []}
    stream1 = Surveys(**args)
    records = read_all_records(stream1)
    assert records == [{"id": "b11111111111111111111111", "name": "survey_1"}, {"id": "b22222222222222222222222", "name": "survey_2"}]

    args["survey_ids"] = ["b22222222222222222222222"]
    stream2 = Surveys(**args)
    records = read_all_records(stream2)
    assert records == [{"id": "b22222222222222222222222", "name": "survey_2"}]

    args["survey_ids"] = ["not-found"]
    stream3 = Surveys(**args)
    records = read_all_records(stream3)
    assert records == []

    assert mock_surveys_request.call_count == 3


def test_responses_stream(requests_mock):
    mock_surveys_request = requests_mock.get(
        "https://api.qualaroo.com/api/v1/nudges?limit=500&start_date=2021-02-11T08%3A35%3A49.540Z",
        headers=NO_SLEEP_HEADERS,
        json=[{"id": "b11111111111111111111111", "name": "survey_1"}, {"id": "b22222222222222222222222", "name": "survey_2"}],
    )

    mock_responses_request_1 = requests_mock.get(
        "https://api.qualaroo.com/api/v1/nudges/b11111111111111111111111/responses.json",
        headers=NO_SLEEP_HEADERS,
        json=[{"id": "c11111111111111111111111", "name": "response_1"}, {"id": "c22222222222222222222222", "name": "response_2"}],
    )

    mock_responses_request_2 = requests_mock.get(
        "https://api.qualaroo.com/api/v1/nudges/b22222222222222222222222/responses.json",
        headers=NO_SLEEP_HEADERS,
        json=[{"id": "c33333333333333333333333", "name": "response_3"}, {"id": "c44444444444444444444444", "name": "response_4"}],
    )

    args = {"authenticator": None, "start_date": "2021-02-11T08:35:49.540Z", "survey_ids": []}
    stream1 = Responses(**args)
    records = read_all_records(stream1)
    assert records == [
        {"id": "c11111111111111111111111", "name": "response_1"},
        {"id": "c22222222222222222222222", "name": "response_2"},
        {"id": "c33333333333333333333333", "name": "response_3"},
        {"id": "c44444444444444444444444", "name": "response_4"},
    ]

    args["survey_ids"] = ["b22222222222222222222222"]
    stream2 = Responses(**args)
    records = read_all_records(stream2)
    assert records == [{"id": "c33333333333333333333333", "name": "response_3"}, {"id": "c44444444444444444444444", "name": "response_4"}]

    args["survey_ids"] = ["not-found"]
    stream3 = Responses(**args)
    records = read_all_records(stream3)
    assert records == []

    assert mock_surveys_request.call_count == 3
    assert mock_responses_request_1.call_count == 1
    assert mock_responses_request_2.call_count == 2
