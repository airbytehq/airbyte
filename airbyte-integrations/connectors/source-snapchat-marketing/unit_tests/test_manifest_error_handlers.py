# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from pathlib import Path

import pytest
import yaml


try:
    from conftest import _YAML_FILE_PATH
except ImportError:
    source_declarative_manifest_path = Path("/airbyte/integration_code/source_declarative_manifest")
    if source_declarative_manifest_path.exists():
        _YAML_FILE_PATH = source_declarative_manifest_path / "manifest.yaml"
    else:
        _YAML_FILE_PATH = Path(__file__).parent.parent / "manifest.yaml"


def _load_manifest():
    return yaml.safe_load(_YAML_FILE_PATH.read_text())


def _collect_error_handlers(value):
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "error_handler" and isinstance(child, dict):
                yield child
            yield from _collect_error_handlers(child)
    elif isinstance(value, list):
        for child in value:
            yield from _collect_error_handlers(child)


def test_all_error_handlers_are_default_error_handlers():
    manifest = _load_manifest()

    error_handlers = list(_collect_error_handlers(manifest))

    assert error_handlers
    assert all(handler["type"] == "DefaultErrorHandler" for handler in error_handlers)


@pytest.mark.parametrize("stream_name", ["organizations", "adaccounts"])
def test_organizations_and_adaccounts_keep_error_response_filters(stream_name):
    manifest = _load_manifest()
    error_handler = manifest["definitions"]["streams"][stream_name]["retriever"]["requester"]["error_handler"]

    response_filters = error_handler["response_filters"]

    assert len(response_filters) == 2
    assert {
        "action": response_filters[0]["action"],
        "http_codes": response_filters[0]["http_codes"],
    } == {"action": "RETRY", "http_codes": [403]}
    assert {
        "action": response_filters[1]["action"],
        "failure_type": response_filters[1]["failure_type"],
        "http_codes": response_filters[1]["http_codes"],
    } == {"action": "FAIL", "failure_type": "config_error", "http_codes": [404]}
