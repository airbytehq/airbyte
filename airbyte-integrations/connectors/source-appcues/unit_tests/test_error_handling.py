# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import json

import pytest
import yaml
from conftest import _YAML_FILE_PATH, get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.parsers.manifest_reference_resolver import ManifestReferenceResolver
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


CONFIG = {"username": "u", "password": "p", "account_id": "123", "start_date": "2024-01-01T00:00:00Z"}
BASE_URL = "https://api.appcues.com/v2/accounts/123/"
STREAMS = [
    ("launchpads", "updated_at", 1704067200000),
    ("flows", "created_at", "2024-02-01T00:00:00.000Z"),
    ("banners", "updated_at", 1704067200000),
    ("checklists", "created_at", "2024-02-01T00:00:00.000Z"),
    ("pins", "updated_at", 1704067200000),
    ("tags", "updated_at", "2024-02-01T00:00:00.000Z"),
    ("segments", "updated_at", "2024-02-01T00:00:00.000Z"),
]


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    monkeypatch.setattr("time.sleep", lambda *_args, **_kwargs: None)


def _request(stream_name: str) -> HttpRequest:
    return HttpRequest(url=f"{BASE_URL}{stream_name}", query_params={})


def _read_stream(stream_name: str, expecting_exception: bool = False) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.incremental).build()
    return read(get_source(CONFIG), CONFIG, catalog, expecting_exception=expecting_exception)


@pytest.mark.parametrize("stream_name,cursor_field,cursor_value", STREAMS)
def test_429_is_retried_then_succeeds(stream_name: str, cursor_field: str, cursor_value: int | str) -> None:
    with HttpMocker() as http_mocker:
        request = _request(stream_name)
        http_mocker.get(
            request,
            [
                HttpResponse(body="{}", status_code=429),
                HttpResponse(body=json.dumps([{"id": 1, cursor_field: cursor_value}]), status_code=200),
            ],
        )

        output = _read_stream(stream_name)

        assert len(output.records) == 1
        assert not output.errors
        http_mocker.assert_number_of_calls(request, 2)


@pytest.mark.parametrize("stream_name", [stream_name for stream_name, _, _ in STREAMS])
def test_429_exhausts_three_retries_then_fails(stream_name: str) -> None:
    with HttpMocker() as http_mocker:
        request = _request(stream_name)
        http_mocker.get(request, HttpResponse(body="{}", status_code=429))

        output = _read_stream(stream_name, expecting_exception=True)

        assert output.errors, "expected the sync to emit an error trace message"
        assert output.errors[0].trace.error.message
        assert output.is_in_logs("Rate limits hit")
        http_mocker.assert_number_of_calls(request, 4)


def test_manifest_has_no_composite_error_handler() -> None:
    manifest = ManifestReferenceResolver().preprocess_manifest(yaml.safe_load(_YAML_FILE_PATH.read_text()))
    composite_handlers = []

    def walk(node):
        if isinstance(node, dict):
            if node.get("type") == "CompositeErrorHandler":
                composite_handlers.append(node)
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(manifest)

    assert not composite_handlers
