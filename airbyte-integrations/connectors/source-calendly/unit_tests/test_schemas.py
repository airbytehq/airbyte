# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import hashlib
import json

import pytest
import yaml
from conftest import _YAML_FILE_PATH


ADDED_FIELDS = {
    "event_types": {"/is_paid", "/internal_note"},
    "api_user": {"/avatar_url"},
    "groups": set(),
    "organization_memberships": set(),
    "scheduled_events": {"/meeting_notes_plain"},
    "event_invitees": {
        "/last_name",
        "/scheduling_method",
        "/no_show",
        "/reconfirmation",
        "/routing_form_submission",
        *{f"/tracking/{name}" for name in ["utm_campaign", "utm_source", "utm_medium", "utm_content", "utm_term", "salesforce_uuid"]},
    },
}
ORIGINAL_TYPE_FORMAT_DIGESTS = {
    "event_types": "d6f6a0cd2dcce2b3a3c6478edce8bd899b885ed5985cc5611c63029839b53917",
    "api_user": "74ff802202af8dd7c57b826d7daf12b096b4cc668ec370f2a3b655a9a952b9bf",
    "groups": "df21a27f8c99f19f6416764146b6939f3254da9c1b84f49cb55db194451d7bae",
    "organization_memberships": "06162530402c1f813e3a204752a834369359fa7e847ca76339167c136575d6ad",
    "scheduled_events": "8278e5678f3dffa2c708abb5361e90d37ce88984418a266236471afc9ed719cc",
    "event_invitees": "d957a5847b327f05233dbd95d3a0a4c4d9d17e91e450098afadf03f1437e34f3",
}


def schema_fields(node: dict, path: str = "") -> dict:
    result = {}
    if "type" in node or "format" in node:
        result[path] = {key: node[key] for key in ("type", "format") if key in node}
    for name, child in node.get("properties", {}).items():
        result.update(schema_fields(child, f"{path}/{name}"))
    if "items" in node:
        result.update(schema_fields(node["items"], f"{path}/[]"))
    return result


@pytest.mark.parametrize("stream", ORIGINAL_TYPE_FORMAT_DIGESTS)
def test_every_preexisting_field_retains_its_type_and_format(stream: str) -> None:
    fields = schema_fields(yaml.safe_load(_YAML_FILE_PATH.read_text())["schemas"][stream])
    original = {
        path: value
        for path, value in fields.items()
        if not any(path == added or path.startswith(added + "/") for added in ADDED_FIELDS[stream])
    }
    assert hashlib.sha256(json.dumps(original, sort_keys=True).encode()).hexdigest() == ORIGINAL_TYPE_FORMAT_DIGESTS[stream]
    for path, definition in original.items():
        if path.rsplit("/", 1)[-1] in {"start_time", "end_time", "created_at", "updated_at", "buffered_start_time", "buffered_end_time"}:
            assert "format" not in definition, path


@pytest.mark.parametrize("stream", ADDED_FIELDS)
def test_new_fields_are_nullable_and_declared(stream: str) -> None:
    fields = schema_fields(yaml.safe_load(_YAML_FILE_PATH.read_text())["schemas"][stream])
    for path in ADDED_FIELDS[stream]:
        assert path in fields
        assert "null" in fields[path]["type"]


def test_documented_nested_fields_and_types() -> None:
    schemas = yaml.safe_load(_YAML_FILE_PATH.read_text())["schemas"]
    assert schemas["event_types"]["properties"]["is_paid"]["type"] == ["boolean", "null"]
    assert schemas["api_user"]["properties"]["avatar_url"] == {"type": ["string", "null"], "format": "uri"}
    events = schemas["scheduled_events"]["properties"]
    assert events["meeting_notes_plain"]["type"] == ["string", "null"]
    assert set(events["cancellation"]["properties"]) == {"canceled_by", "canceler_type", "reason", "created_at"}
    invitees = schemas["event_invitees"]["properties"]
    assert invitees["new_invitee"]["type"] == ["string", "null"]
    assert set(invitees["no_show"]["properties"]) == {"uri", "created_at"}
    assert set(invitees["reconfirmation"]["properties"]) == {"created_at", "confirmed_at"}
    for name in ["no_show", "reconfirmation"]:
        assert invitees[name]["type"] == ["object", "null"]
        assert invitees[name]["properties"]["created_at"]["format"] == "date-time"
    assert invitees["reconfirmation"]["properties"]["confirmed_at"]["format"] == "date-time"
    assert set(invitees["tracking"]["properties"]) == {
        "utm_campaign",
        "utm_source",
        "utm_medium",
        "utm_content",
        "utm_term",
        "salesforce_uuid",
    }
