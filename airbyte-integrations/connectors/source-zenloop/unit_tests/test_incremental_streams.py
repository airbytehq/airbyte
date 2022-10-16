#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from unittest.mock import MagicMock

from airbyte_cdk.models import SyncMode
from pytest import fixture
from source_zenloop.source import Answers, AnswersSurveyGroup, IncrementalZenloopStream


@fixture
def patch_incremental_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(IncrementalZenloopStream, "path", "v0/example_endpoint")
    mocker.patch.object(IncrementalZenloopStream, "primary_key", "test_primary_key")
    mocker.patch.object(IncrementalZenloopStream, "__abstractmethods__", set())


def test_cursor_field(patch_incremental_base_class, config):
    stream = IncrementalZenloopStream(config["api_token"], config["date_from"], config["survey_id"], config["survey_group_id"])
    expected_cursor_field = "inserted_at"
    assert stream.cursor_field == expected_cursor_field


def test_get_updated_state(patch_incremental_base_class, config):
    stream = IncrementalZenloopStream(config["api_token"], config["date_from"], config["survey_id"], config["survey_group_id"])
    expected_cursor_field = "inserted_at"
    inputs = {
        "current_stream_state": {expected_cursor_field: "2021-07-24T03:30:30.038549Z"},
        "latest_record": {"inserted_at": "2021-10-20T03:30:30.038549Z"},
    }
    expected_state = {expected_cursor_field: "2021-10-20T03:30:31.038549Z"}
    assert stream.get_updated_state(**inputs) == expected_state


def test_stream_slices(patch_incremental_base_class, config):
    expected_cursor_field = "inserted_at"
    inputs = {
        "sync_mode": SyncMode.incremental,
        "cursor_field": expected_cursor_field,
        "stream_state": {expected_cursor_field: "2021-10-20T03:30:30Z"},
    }
    expected_stream_slice = [None]

    stream = IncrementalZenloopStream(config["api_token"], config["date_from"], config["survey_id"], config["survey_group_id"])
    assert list(stream.stream_slices(**inputs)) == expected_stream_slice

    stream = IncrementalZenloopStream(config["api_token"], config["date_from"], config["survey_id"], None)
    assert list(stream.stream_slices(**inputs)) == expected_stream_slice

    stream = IncrementalZenloopStream(config["api_token"], config["date_from"], None, config["survey_group_id"])
    assert list(stream.stream_slices(**inputs)) == expected_stream_slice


def test_supports_incremental(patch_incremental_base_class, mocker, config):
    mocker.patch.object(IncrementalZenloopStream, "cursor_field", "dummy_field")
    stream = IncrementalZenloopStream(config["api_token"], config["date_from"], config["survey_id"], config["survey_group_id"])
    assert stream.supports_incremental


def test_source_defined_cursor(patch_incremental_base_class, config):
    stream = IncrementalZenloopStream(config["api_token"], config["date_from"], config["survey_id"], config["survey_group_id"])
    assert stream.source_defined_cursor


def test_stream_checkpoint_interval(patch_incremental_base_class, config):
    stream = IncrementalZenloopStream(config["api_token"], config["date_from"], config["survey_id"], config["survey_group_id"])
    expected_checkpoint_interval = 1000
    assert stream.state_checkpoint_interval == expected_checkpoint_interval


def test_parse_response_answers(patch_incremental_base_class, config):
    stream = Answers(**config)
    response = MagicMock()
    response.json.return_value = {"answers": [{"id": 123, "name": "John Doe"}]}
    inputs = {"response": response}
    expected_parsed_object = {"id": 123, "name": "John Doe"}
    assert next(stream.parse_response(**inputs)) == expected_parsed_object


def test_parse_response_answers_survey_groups(patch_incremental_base_class, config):
    stream = AnswersSurveyGroup(**config)
    response = MagicMock()
    response.json.return_value = {"answers": [{"id": 123, "name": "John Doe"}]}
    inputs = {"response": response}
    expected_parsed_object = {"id": 123, "name": "John Doe"}
    assert next(stream.parse_response(**inputs)) == expected_parsed_object


def test_surveys_path(config):
    stream = Answers(**config)
    expected = "surveys/<survey_id>/answers"
    assert stream.path() == expected


def test_survey_groups_path(config):
    stream = AnswersSurveyGroup(**config)
    expected = "survey_groups/<survey_group_id>/answers"
    assert stream.path() == expected
