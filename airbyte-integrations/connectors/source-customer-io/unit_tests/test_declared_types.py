# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Declared types match the OpenAPI spec for the fields 1.0.0 retypes: records in the documented shape validate, and values
or array items of another type do not."""

import pytest
import requests_mock
from _helpers import get_source
from jsonschema import Draft7Validator
from test_error_handling_and_lookback import _API
from test_pagination_region_incremental import _BASE_CONFIG, _action, _campaign, _newsletter, _read

from airbyte_cdk.test.entrypoint_wrapper import discover


_UPDATED = 1759179716


def _schemas() -> dict:
    output = discover(get_source(_BASE_CONFIG), _BASE_CONFIG)
    return {stream.name: stream.json_schema for stream in output.catalog.catalog.streams}


def _documented_campaign() -> dict:
    return {**_campaign(1, _UPDATED), "tags": ["new", "welcome"], "trigger_segment_ids": [90]}


def _documented_action() -> dict:
    """`id` arrives as a JSON string live, although the spec documents an integer (AGENTS.md section 6)."""
    return {**_action(2, 1, _UPDATED), "id": "2", "from_id": 1, "reply_to_id": 38}


def _documented_newsletter() -> dict:
    return {**_newsletter(3, _UPDATED), "sent_at": _UPDATED, "tags": ["launch"], "content_ids": [4, 5]}


@pytest.mark.parametrize(
    "stream_name, responses",
    [
        ("campaigns", {"/campaigns": {"campaigns": [_documented_campaign()]}}),
        (
            "campaigns_actions",
            {
                "/campaigns": {"campaigns": [_documented_campaign()]},
                "/campaigns/1/actions": {"actions": [_documented_action()], "next": ""},
            },
        ),
        ("newsletters", {"/newsletters": {"newsletters": [_documented_newsletter()], "next": None}}),
    ],
)
def test_documented_records_validate_against_the_declared_schema(stream_name, responses):
    with requests_mock.Mocker() as mocker:
        for path, body in responses.items():
            mocker.get(f"{_API}{path}", json=body)
        output = _read(stream_name, _BASE_CONFIG)

    validator = Draft7Validator(_schemas()[stream_name])
    assert output.records
    for record in output.records:
        assert not [error.message for error in validator.iter_errors(record.record.data)]


@pytest.mark.parametrize(
    "stream_name, field, wrong_value",
    [
        ("campaigns", "tags", [1]),
        ("campaigns", "trigger_segment_ids", ["90"]),
        ("campaigns", "trigger_segment_ids", [1.5]),
        ("newsletters", "tags", [1]),
        ("newsletters", "content_ids", ["4"]),
        ("newsletters", "content_ids", [1.5]),
        ("newsletters", "sent_at", "1759179716"),
        ("newsletters", "sent_at", 1.5),
        ("campaigns_actions", "from_id", "1"),
        ("campaigns_actions", "from_id", 1.5),
        ("campaigns_actions", "reply_to_id", "38"),
        ("campaigns_actions", "reply_to_id", 1.5),
    ],
)
def test_values_of_another_type_fail_validation(stream_name, field, wrong_value):
    """Pins the scalar and item types: under the old schemas any array passed, and `from_id` and `reply_to_id` took strings."""
    errors = Draft7Validator(_schemas()[stream_name]).iter_errors({field: wrong_value})
    assert [error for error in errors if list(error.absolute_path)[:1] == [field]]
