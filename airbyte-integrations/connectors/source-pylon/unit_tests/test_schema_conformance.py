# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from pathlib import Path

import pytest
import yaml
from jsonschema import Draft7Validator, FormatChecker, ValidationError


FIXTURES = Path(__file__).parent / "resource/http/response"
STREAMS = sorted(path.stem for path in FIXTURES.glob("*.json") if not path.name.startswith("_"))


@pytest.mark.parametrize("stream", STREAMS)
def test_synthetic_fixture_conforms_to_stream_schema(manifest_path: Path, stream: str) -> None:
    schema = yaml.safe_load(manifest_path.read_text())["schemas"][stream]
    record = json.loads((FIXTURES / f"{stream}.json").read_text())
    Draft7Validator.check_schema(schema)
    validator = Draft7Validator(schema, format_checker=FormatChecker())
    validator.validate(record)
    declared = set(schema["properties"])
    assert set(record) <= declared
    for field, definition in schema["properties"].items():
        if isinstance(definition.get("type"), list) and "null" in definition["type"]:
            validator.validate({**record, field: None})
    if schema.get("required"):
        with pytest.raises(ValidationError):
            validator.validate({})


def test_timestamp_formats_are_enforced(manifest_path: Path) -> None:
    schema = yaml.safe_load(manifest_path.read_text())["schemas"]["knowledge_base_articles"]
    validator = Draft7Validator(schema, format_checker=FormatChecker())
    record = json.loads((FIXTURES / "knowledge_base_articles.json").read_text())
    with pytest.raises(ValidationError):
        validator.validate({**record, "created_at": "not-a-timestamp"})


@pytest.mark.parametrize("value", [None, "", "synthetic-future-delivery-mode"])
def test_issue_thread_delivery_mode_is_nullable_and_open(manifest_path: Path, value: str | None) -> None:
    schema = yaml.safe_load(manifest_path.read_text())["schemas"]["issue_threads"]
    validator = Draft7Validator(schema)
    validator.validate({**json.loads((FIXTURES / "issue_threads.json").read_text()), "delivery_mode": value})
    with pytest.raises(ValidationError):
        validator.validate({"delivery_mode": 123})


def test_audit_log_action_specific_objects_are_loose(manifest_path: Path) -> None:
    schema = yaml.safe_load(manifest_path.read_text())["schemas"]["audit_logs"]
    record = json.loads((FIXTURES / "audit_logs.json").read_text())
    varying = {"nested": {"synthetic": [1, None, True]}, "number": 2, "text": "synthetic"}
    Draft7Validator(schema).validate({**record, "metadata": varying, "attributes": varying})


@pytest.mark.parametrize("stream,field", [("surveys", "type"), ("training_data", "type"), ("training_data", "visibility")])
def test_new_stream_string_values_are_not_enumerated(manifest_path: Path, stream: str, field: str) -> None:
    schema = yaml.safe_load(manifest_path.read_text())["schemas"][stream]
    record = json.loads((FIXTURES / f"{stream}.json").read_text())
    Draft7Validator(schema).validate({**record, field: "synthetic-future-value"})


@pytest.mark.parametrize(
    "value,valid", [(None, True), ("", True), ("synthetic-unformatted-time", True), ("2026-01-01T00:00:00Z", True), (123, False)]
)
def test_vendor_activity_time_has_no_undocumented_format(manifest_path: Path, value: str | int | None, valid: bool) -> None:
    schema = yaml.safe_load(manifest_path.read_text())["schemas"]["accounts"]
    assert "format" not in schema["properties"]["latest_vendor_activity_time"]
    validator = Draft7Validator(schema, format_checker=FormatChecker())
    record = {**json.loads((FIXTURES / "accounts.json").read_text()), "latest_vendor_activity_time": value}
    if valid:
        validator.validate(record)
    else:
        with pytest.raises(ValidationError):
            validator.validate(record)
