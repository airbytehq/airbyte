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
