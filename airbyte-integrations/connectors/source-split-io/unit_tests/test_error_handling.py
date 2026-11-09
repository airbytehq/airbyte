# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Mock-server tests for the Split.io error handlers declared in `manifest.yaml`."""

import json
from typing import Any, Mapping

import pytest
import yaml
from conftest import _YAML_FILE_PATH, get_source

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.sources.declarative.parsers.manifest_reference_resolver import ManifestReferenceResolver
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder


CONFIG: Mapping[str, Any] = {"api_key": "test_key", "start_date": "2024-01-01T00:00:00Z"}
BASE_URL = "https://api.split.io/internal/api/"


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    """Skip real waits during retry tests."""
    monkeypatch.setattr("time.sleep", lambda *_args, **_kwargs: None)


def _request(path: str) -> HttpRequest:
    return HttpRequest(
        url=f"{BASE_URL}{path}",
        query_params={"offset": "0", "limit": "50"},
        headers={"Authorization": "Bearer test_key"},
    )


def _response(body: Any, status_code: int = 200) -> HttpResponse:
    return HttpResponse(body=json.dumps(body), status_code=status_code)


def _read_stream(stream_name: str, expecting_exception: bool = False) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    return read(
        get_source(CONFIG),
        CONFIG,
        catalog,
        state=StateBuilder().build(),
        expecting_exception=expecting_exception,
    )


def _error_trace(output: EntrypointOutput):
    assert output.errors, "expected the sync to emit an error trace"
    return output.errors[0].trace.error


def _walk(node: Any) -> list[dict[str, Any]]:
    matches = []
    if isinstance(node, dict):
        if node.get("type") == "Composite" + "ErrorHandler":
            matches.append(node)
        for value in node.values():
            matches.extend(_walk(value))
    elif isinstance(node, list):
        for value in node:
            matches.extend(_walk(value))
    return matches


def test_manifest_has_no_composite_error_handler() -> None:
    manifest = ManifestReferenceResolver().preprocess_manifest(yaml.safe_load(_YAML_FILE_PATH.read_text()))

    assert not _walk(manifest)


def test_segments_keys_404_is_ignored() -> None:
    workspaces = _request("v2/workspaces")
    environments = _request("v2/environments/ws/workspace-1")
    segments = _request("v2/segments/ws/workspace-1")
    segment_a_keys = _request("v2/segments/environment-1/segment-a/keys")
    segment_b_keys = _request("v2/segments/environment-1/segment-b/keys")

    with HttpMocker() as http_mocker:
        http_mocker.get(workspaces, _response({"objects": [{"id": "workspace-1"}]}))
        http_mocker.get(environments, _response([{"id": "environment-1"}]))
        http_mocker.get(
            segments,
            _response(
                {
                    "objects": [
                        {"name": "segment-a", "creationTime": 1704153600000},
                        {"name": "segment-b", "creationTime": 1704153600000},
                    ]
                }
            ),
        )
        http_mocker.get(segment_a_keys, _response({"message": "Segment not found"}, status_code=404))
        http_mocker.get(segment_b_keys, _response([{"keys": ["user-1"], "count": 1}]))

        output = _read_stream("segments_keys")

        assert not output.errors
        assert len(output.records) == 1
        assert output.records[0].record.data["keys"] == ["user-1"]
        http_mocker.assert_number_of_calls(segment_a_keys, 1)


def test_404_fails_on_streams_without_ignore_filter() -> None:
    change_requests = _request("v2/changeRequests")

    with HttpMocker() as http_mocker:
        http_mocker.get(change_requests, _response({"message": "not found"}, status_code=404))

        error = _error_trace(_read_stream("changeRequests", expecting_exception=True))

        assert error
        http_mocker.assert_number_of_calls(change_requests, 1)


def test_429_is_retried_then_succeeds() -> None:
    change_requests = _request("v2/changeRequests")

    with HttpMocker() as http_mocker:
        http_mocker.get(
            change_requests,
            [
                _response({"message": "too many requests"}, status_code=429),
                _response({"data": [{"id": "change-request-1"}]}),
            ],
        )

        output = _read_stream("changeRequests")

        assert not output.errors
        assert [record.record.data["id"] for record in output.records] == ["change-request-1"]
        http_mocker.assert_number_of_calls(change_requests, 2)


def test_429_gives_up_after_max_retries() -> None:
    change_requests = _request("v2/changeRequests")

    with HttpMocker() as http_mocker:
        http_mocker.get(change_requests, _response({"message": "too many requests"}, status_code=429))

        error = _error_trace(_read_stream("changeRequests", expecting_exception=True))

        assert error.failure_type == FailureType.transient_error
        http_mocker.assert_number_of_calls(change_requests, 4)
