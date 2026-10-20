# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import os
import shutil
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import pytest

from airbyte_cdk.models import Type
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from unit_tests.utils import FLATTEN_EXEMPTIONS


pytest_plugins = ["airbyte_cdk.test.utils.manifest_only_fixtures"]


def _get_manifest_path() -> Path:
    source_declarative_manifest_path = Path("/airbyte/integration_code/source_declarative_manifest")
    if source_declarative_manifest_path.exists():
        return source_declarative_manifest_path
    return Path(__file__).parent.parent


_SOURCE_FOLDER_PATH = _get_manifest_path()
MANIFEST_PATH = _SOURCE_FOLDER_PATH / "manifest.yaml"

sys.path.append(str(_SOURCE_FOLDER_PATH))  # to allow loading custom components


os.environ["REQUEST_CACHE_PATH"] = "REQUEST_CACHE_PATH"

SCALAR_TYPES = {"string", "integer", "number", "boolean"}
VALIDATED_RECORD_COUNTS: Counter[str] = Counter()
DECLARED_SCHEMAS: dict[str, dict[str, Any]] = {}


def _matches_type(value: Any, type_declaration: Any) -> bool:
    allowed = type_declaration if isinstance(type_declaration, list) else [type_declaration]
    if value is None:
        return "null" in allowed
    if "array" in allowed:
        return isinstance(value, list)
    if "string" in allowed:
        return isinstance(value, str)
    if "integer" in allowed:
        return type(value) is int
    if "number" in allowed:
        return type(value) in (int, float)
    if "boolean" in allowed:
        return isinstance(value, bool)
    return False


def _validate_record(stream_name: str, record: dict[str, Any], schema: dict[str, Any]) -> None:
    properties = schema["properties"]
    undeclared = set(record) - set(properties)
    assert not undeclared, f"{stream_name}: undeclared record keys {sorted(undeclared)}"
    for field_name, value in record.items():
        if field_name in FLATTEN_EXEMPTIONS.get(stream_name, {}):
            continue
        field_schema = properties[field_name]
        field_type = field_schema.get("type")
        allowed = field_type if isinstance(field_type, list) else [field_type]
        if value is None and "null" in allowed:
            continue
        if "array" in allowed:
            assert isinstance(value, list), f"{stream_name}.{field_name}: expected an array"
            item_types = field_schema.get("items", {}).get("type")
            for index, item in enumerate(value):
                assert _matches_type(item, item_types), f"{stream_name}.{field_name}[{index}]: invalid item type"
        else:
            assert _matches_type(value, field_type), f"{stream_name}.{field_name}: invalid type for {value!r}"


@pytest.fixture(autouse=True)
def clear_request_cache():
    """The manifest resolver streams use `use_cache: true`, which persists HTTP
    responses in a sqlite file across tests — a cached listing from one test would
    shadow another test's mock for the same URL. Start every test with a clean cache."""
    shutil.rmtree(os.environ["REQUEST_CACHE_PATH"], ignore_errors=True)
    yield


@pytest.fixture(autouse=True)
def validate_materialized_records(monkeypatch):
    original_read = YamlDeclarativeSource.read

    def read_with_validation(source, logger, config, catalog, state=None):
        if not DECLARED_SCHEMAS:
            DECLARED_SCHEMAS.update({stream.name: stream.get_json_schema() for stream in source.streams(config)})
        for message in original_read(source, logger, config, catalog, state):
            if message.type == Type.RECORD:
                stream_name = message.record.stream
                _validate_record(stream_name, message.record.data, DECLARED_SCHEMAS[stream_name])
                VALIDATED_RECORD_COUNTS[stream_name] += 1
            yield message

    monkeypatch.setattr(YamlDeclarativeSource, "read", read_with_validation)


def pytest_sessionfinish(session, exitstatus):
    options = session.config.option
    if exitstatus != 0 or options.file_or_dir or options.keyword or options.markexpr:
        return

    stream_names = {
        item.callspec.params["stream_name"] for item in session.items if hasattr(item, "callspec") and "stream_name" in item.callspec.params
    }
    if len(stream_names) != 42:
        return
    missing = stream_names - VALIDATED_RECORD_COUNTS.keys()
    if missing:
        session.exitstatus = pytest.ExitCode.TESTS_FAILED
        print(f"\nNo validated records were emitted for streams: {sorted(missing)}")


@pytest.fixture(name="rate_limit_mock_response")
def rate_limit_mock_response(requests_mock):
    rate_limit_response = {
        "resources": {
            "core": {"limit": 5000, "used": 0, "remaining": 5000, "reset": 4070908800},
            "graphql": {"limit": 5000, "used": 0, "remaining": 5000, "reset": 4070908800},
        }
    }
    requests_mock.get("https://api.github.com/rate_limit", json=rate_limit_response)
