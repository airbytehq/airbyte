# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import json
from typing import Any

import pytest
import yaml
from conftest import _YAML_FILE_PATH, get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.parsers.manifest_reference_resolver import ManifestReferenceResolver
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


CONFIG = {"api_key": "test", "start_date": "2024-01-01T00:00:00Z", "page_limit": "50"}
EXPECTED_ERROR_HANDLER = {
    "type": "DefaultErrorHandler",
    "max_retries": 3,
    "backoff_strategies": [{"type": "ExponentialBackoffStrategy", "factor": 2}],
    "response_filters": [
        {
            "type": "HttpResponseFilter",
            "action": "RATE_LIMITED",
            "http_codes": [429],
            "error_message": "Rate limit hit",
        }
    ],
}
ACCOUNTS_REQUEST = HttpRequest(url="https://api2.frontapp.com/accounts", query_params="any query_parameters")


def _resolved_manifest() -> dict[str, Any]:
    manifest = yaml.safe_load(_YAML_FILE_PATH.read_text())
    return ManifestReferenceResolver().preprocess_manifest(manifest)


def _resolved_streams(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    streams = {}
    for stream_ref in manifest["streams"]:
        if "$ref" in stream_ref:
            stream_name = stream_ref["$ref"].rsplit("/", 1)[-1]
            stream = manifest["definitions"]["streams"][stream_name]
        else:
            stream = stream_ref
            stream_name = stream["name"]
        streams[stream_name] = stream
    return streams


def test_manifest_has_no_composite_error_handler() -> None:
    composite_handlers = []
    composite_handler_type = "".join(("Composite", "ErrorHandler"))

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            if node.get("type") == composite_handler_type:
                composite_handlers.append(node)
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(_resolved_manifest())

    assert not composite_handlers


@pytest.mark.parametrize("stream_name", _resolved_streams(_resolved_manifest()))
def test_every_stream_uses_a_single_default_error_handler(stream_name: str) -> None:
    streams = _resolved_streams(_resolved_manifest())

    assert len(streams) == 35
    assert streams[stream_name]["retriever"]["requester"]["error_handler"] == EXPECTED_ERROR_HANDLER


@pytest.fixture
def recorded_sleeps(monkeypatch: pytest.MonkeyPatch) -> list[float]:
    sleeps = []
    monkeypatch.setattr("time.sleep", lambda seconds=0, *_args, **_kwargs: sleeps.append(seconds))
    return sleeps


def _read_accounts(expecting_exception: bool = False) -> Any:
    catalog = CatalogBuilder().with_stream("accounts", SyncMode.full_refresh).build()
    return read(get_source(CONFIG), CONFIG, catalog, expecting_exception=expecting_exception)


def test_rate_limit_retries_then_reads_record(recorded_sleeps: list[float]) -> None:
    record = {"id": "acc_1", "updated_at": 1704067200}
    success_response = HttpResponse(
        body=json.dumps({"_results": [record], "_pagination": {"next": None}}),
        status_code=200,
    )
    with HttpMocker() as http_mocker:
        http_mocker.get(
            ACCOUNTS_REQUEST,
            [HttpResponse(body="{}", status_code=429), success_response],
        )

        output = _read_accounts()

        assert len(output.records) == 1
        assert not output.errors
        http_mocker.assert_number_of_calls(ACCOUNTS_REQUEST, 2)
        assert recorded_sleeps


def test_rate_limit_fails_after_max_retries(recorded_sleeps: list[float]) -> None:
    with HttpMocker() as http_mocker:
        http_mocker.get(ACCOUNTS_REQUEST, [HttpResponse(body="{}", status_code=429) for _ in range(4)])

        output = _read_accounts(expecting_exception=True)

        assert output.errors
        http_mocker.assert_number_of_calls(ACCOUNTS_REQUEST, 4)
