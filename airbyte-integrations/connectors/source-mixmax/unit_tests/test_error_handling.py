# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import json

import pytest
import yaml
from conftest import _YAML_FILE_PATH, get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.parsers.manifest_reference_resolver import ManifestReferenceResolver
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from airbyte_cdk.test.mock_http.request import ANY_QUERY_PARAMS, HttpRequest


CONFIG = {"api_key": "test-key", "start_date": "2024-01-01T00:00:00Z"}
FACTOR_2_STREAM = "codesnippets"
STREAM_NAMES = tuple(yaml.safe_load(_YAML_FILE_PATH.read_text())["definitions"]["streams"])
assert len(STREAM_NAMES) == 20


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    slept = []
    monkeypatch.setattr("time.sleep", lambda seconds=0, *_args, **_kwargs: slept.append(seconds))
    return slept


def _resolved_manifest():
    manifest = yaml.safe_load(_YAML_FILE_PATH.read_text())
    return ManifestReferenceResolver().preprocess_manifest(manifest)


def _strip_parameters(value):
    if isinstance(value, dict):
        return {key: _strip_parameters(item) for key, item in value.items() if key != "$parameters"}
    if isinstance(value, list):
        return [_strip_parameters(item) for item in value]
    return value


def _request(stream_name: str) -> HttpRequest:
    path = "livefeed" if stream_name == "livefeed" else "codesnippets"
    return HttpRequest(url=f"https://api.mixmax.com/v1/{path}", query_params=ANY_QUERY_PARAMS)


def _read_stream(stream_name: str, expecting_exception: bool = False):
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    return read(get_source(CONFIG), CONFIG, catalog, expecting_exception=expecting_exception)


def _record_response(record_id: str) -> HttpResponse:
    return HttpResponse(
        body=json.dumps({"results": [{"_id": record_id, "createdAt": "2024-01-01T00:00:00.000Z"}], "hasNext": False}),
        status_code=200,
    )


def _rate_limited_response() -> HttpResponse:
    return HttpResponse(body=json.dumps({"error": "Rate limits hit"}), status_code=429)


def test_manifest_has_no_composite_error_handler() -> None:
    manifest = _resolved_manifest()
    composite_handlers = []

    def walk(node):
        if isinstance(node, dict):
            if node.get("type") == "".join(("Composite", "ErrorHandler")):
                composite_handlers.append(node)
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(manifest)
    assert not composite_handlers


@pytest.mark.parametrize("stream_name", STREAM_NAMES)
def test_error_handler_configuration(stream_name: str) -> None:
    manifest = _resolved_manifest()
    error_handler = manifest["definitions"]["streams"][stream_name]["retriever"]["requester"]["error_handler"]
    expected = {
        "type": "DefaultErrorHandler",
        "max_retries": 3,
        "backoff_strategies": [{"type": "ExponentialBackoffStrategy", "factor": 6 if stream_name == "livefeed" else 2}],
        "response_filters": [
            {
                "type": "HttpResponseFilter",
                "action": "RATE_LIMITED",
                "http_codes": [429],
                "error_message": "Rate limits hit",
            }
        ],
    }

    assert _strip_parameters(error_handler) == expected


def test_factor_2_handler_retries_and_emits_records(no_sleep) -> None:
    request = _request(FACTOR_2_STREAM)
    with HttpMocker() as http_mocker:
        http_mocker.get(request, [_rate_limited_response(), _record_response("code-1")])

        output = _read_stream(FACTOR_2_STREAM)

        assert not output.errors
        assert [record.record.data["_id"] for record in output.records] == ["code-1"]
        http_mocker.assert_number_of_calls(request, 2)
        assert no_sleep == [5, 0]


def test_factor_2_handler_fails_after_retries(no_sleep) -> None:
    request = _request(FACTOR_2_STREAM)
    with HttpMocker() as http_mocker:
        http_mocker.get(request, _rate_limited_response())

        output = _read_stream(FACTOR_2_STREAM, expecting_exception=True)

        assert output.errors
        http_mocker.assert_number_of_calls(request, 4)
        assert no_sleep == [5, 0, 9, 0, 17, 0]


def test_livefeed_backoff_matches_current_behavior(no_sleep) -> None:
    factor_2_request = _request(FACTOR_2_STREAM)
    livefeed_request = _request("livefeed")
    with HttpMocker() as http_mocker:
        http_mocker.get(factor_2_request, [_rate_limited_response(), _record_response("code-2")])
        factor_2_output = _read_stream(FACTOR_2_STREAM)
        factor_2_backoff = next(seconds for seconds in no_sleep if seconds > 0)

        http_mocker.get(livefeed_request, [_rate_limited_response(), _record_response("livefeed-1")])
        livefeed_output = _read_stream("livefeed")
        livefeed_backoff = next(seconds for seconds in reversed(no_sleep) if seconds > 0)

        assert not factor_2_output.errors
        assert not livefeed_output.errors
        assert [record.record.data["_id"] for record in factor_2_output.records] == ["code-2"]
        assert [record.record.data["_id"] for record in livefeed_output.records] == ["livefeed-1"]
        http_mocker.assert_number_of_calls(factor_2_request, 2)
        http_mocker.assert_number_of_calls(livefeed_request, 2)
        assert factor_2_backoff == 5
        assert livefeed_backoff == 13
        assert no_sleep == [5, 0, 13, 0]
