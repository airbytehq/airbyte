# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import pytest
import yaml
from jsonschema import Draft7Validator
from unit_tests._helpers import _MANIFEST_PATH


def _schema(stream_name):
    manifest = yaml.safe_load(_MANIFEST_PATH.read_text())
    return manifest["schemas"][stream_name]


def _is_valid(stream_name, record):
    return Draft7Validator(_schema(stream_name)).is_valid(record)


@pytest.mark.parametrize(
    "record",
    [
        {"metaData": {"id": "1"}, "parties": [{"speakerId": "s1", "context": []}]},
        {"metaData": {"id": "1"}, "parties": [{"speakerId": "s1", "context": [{"system": "Salesforce", "objects": []}]}]},
        {"metaData": {"id": "1"}, "parties": [{"speakerId": "s1", "context": None}]},
        {"metaData": {"id": "1"}, "media": {"audioUrl": "https://example.com/a.mp3", "videoUrl": None}},
        {"metaData": {"id": "1"}, "media": None},
    ],
)
def test_extensive_calls_accepts_live_shapes(record):
    assert _is_valid("extensiveCalls", record)


@pytest.mark.parametrize(
    "record",
    [
        {"metaData": {"id": "1"}, "parties": [{"speakerId": "s1", "context": {"system": "Salesforce"}}]},
        {"metaData": {"id": "1"}, "parties": [{"speakerId": "s1", "context": "bogus"}]},
        {"metaData": {"id": "1"}, "media": "https://example.com/a.mp3"},
    ],
)
def test_extensive_calls_rejects_wrong_shapes(record):
    assert not _is_valid("extensiveCalls", record)


def test_added_fields_are_declared_nullable():
    users = _schema("users")["properties"]["conferencingProviders"]
    assert set(users["type"]) == {"null", "array"}
    assert set(users["items"]["properties"]) == {"provider", "isDefault"}
    for stream in ("scorecards", "answeredScorecards"):
        review_method = _schema(stream)["properties"]["reviewMethod"]
        assert set(review_method["type"]) == {"null", "string"}


def test_added_fields_validate():
    assert _is_valid("users", {"id": "u1", "conferencingProviders": [{"provider": "zoom", "isDefault": True}]})
    assert _is_valid("scorecards", {"scorecardId": "1", "reviewMethod": "MANUAL"})
    assert _is_valid("answeredScorecards", {"answeredScorecardId": "1", "reviewMethod": None})
