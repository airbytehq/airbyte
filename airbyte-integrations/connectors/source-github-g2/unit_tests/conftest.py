# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import copy
import hashlib
import json
import os
import shutil
import sys
from collections import Counter
from functools import wraps
from pathlib import Path
from typing import Any

import pytest
import yaml

from airbyte_cdk.models import Type
from airbyte_cdk.sources.declarative import concurrent_declarative_source as concurrent_source_module
from airbyte_cdk.sources.declarative.concurrent_declarative_source import ConcurrentDeclarativeSource
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
AGGREGATED_VALIDATED_RECORD_COUNTS: Counter[str] = Counter()
AGGREGATED_STREAM_NAMES: set[str] = set()


def _stable_manifest_key(manifest: dict[str, Any]) -> str:
    serialized_manifest = json.dumps(manifest, sort_keys=True, default=str).encode()
    return hashlib.sha256(serialized_manifest).hexdigest()


def _manifest_stream_count() -> int:
    with MANIFEST_PATH.open() as manifest_file:
        return len(yaml.safe_load(manifest_file)["streams"])


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
    if "object" in allowed:
        return isinstance(value, dict)
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


@pytest.fixture(scope="session", autouse=True)
def cache_declarative_manifest_processing():
    original_component_schema_loader = concurrent_source_module._get_declarative_component_schema
    original_preprocess_manifest = ConcurrentDeclarativeSource._pre_process_manifest
    original_validate_source = ConcurrentDeclarativeSource._validate_source
    component_schema = None
    preprocessed_manifests: dict[str, dict[str, Any]] = {}
    validated_manifests: set[str] = set()

    @wraps(original_component_schema_loader)
    def get_component_schema():
        nonlocal component_schema
        if component_schema is None:
            component_schema = original_component_schema_loader()
        return copy.deepcopy(component_schema)

    @wraps(original_preprocess_manifest)
    def preprocess_manifest(source, manifest):
        key = _stable_manifest_key(manifest)
        if key not in preprocessed_manifests:
            preprocessed_manifests[key] = copy.deepcopy(original_preprocess_manifest(source, copy.deepcopy(manifest)))
        return copy.deepcopy(preprocessed_manifests[key])

    @wraps(original_validate_source)
    def validate_source(source):
        key = _stable_manifest_key(source._source_config)
        if key not in validated_manifests:
            original_validate_source(source)
            validated_manifests.add(key)

    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(concurrent_source_module, "_get_declarative_component_schema", get_component_schema)
    monkeypatch.setattr(ConcurrentDeclarativeSource, "_pre_process_manifest", preprocess_manifest)
    monkeypatch.setattr(ConcurrentDeclarativeSource, "_validate_source", validate_source)
    yield
    monkeypatch.undo()


@pytest.fixture(autouse=True)
def clear_request_cache(request):
    """The manifest resolver streams use `use_cache: true`, which persists HTTP
    responses in a sqlite file across tests — a cached listing from one test would
    shadow another test's mock for the same URL. Start every test with a clean cache."""
    worker_id = getattr(request.config, "workerinput", {}).get("workerid", "master")
    cache_path = f"REQUEST_CACHE_PATH_{worker_id}"
    os.environ["REQUEST_CACHE_PATH"] = cache_path
    shutil.rmtree(cache_path, ignore_errors=True)
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
    if hasattr(session.config, "workeroutput"):
        session.config.workeroutput["validated_record_counts"] = dict(VALIDATED_RECORD_COUNTS)
        session.config.workeroutput["stream_names"] = {
            item.callspec.params["stream_name"]
            for item in session.items
            if hasattr(item, "callspec") and "stream_name" in item.callspec.params
        }
        return

    if exitstatus != 0 or options.file_or_dir or options.keyword or options.markexpr:
        return

    is_xdist_controller = bool(getattr(options, "numprocesses", None))
    stream_names = (
        AGGREGATED_STREAM_NAMES
        if is_xdist_controller
        else {
            item.callspec.params["stream_name"]
            for item in session.items
            if hasattr(item, "callspec") and "stream_name" in item.callspec.params
        }
    )
    if len(stream_names) != _manifest_stream_count():
        return
    validated_record_counts = AGGREGATED_VALIDATED_RECORD_COUNTS if is_xdist_controller else VALIDATED_RECORD_COUNTS
    missing = stream_names - validated_record_counts.keys()
    if missing:
        session.exitstatus = pytest.ExitCode.TESTS_FAILED
        print(f"\nNo validated records were emitted for streams: {sorted(missing)}")


@pytest.hookimpl(optionalhook=True)
def pytest_testnodedown(node, error):
    worker_output = getattr(node, "workeroutput", {})
    AGGREGATED_STREAM_NAMES.update(worker_output.get("stream_names", set()))
    for stream_name, count in worker_output.get("validated_record_counts", {}).items():
        AGGREGATED_VALIDATED_RECORD_COUNTS[stream_name] += count


@pytest.fixture(name="rate_limit_mock_response")
def rate_limit_mock_response(requests_mock):
    rate_limit_response = {
        "resources": {
            "core": {"limit": 5000, "used": 0, "remaining": 5000, "reset": 4070908800},
            "graphql": {"limit": 5000, "used": 0, "remaining": 5000, "reset": 4070908800},
        }
    }
    requests_mock.get("https://api.github.com/rate_limit", json=rate_limit_response)
