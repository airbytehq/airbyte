# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Mock-server tests for the ClickUp error handler declared in `manifest.yaml`.

Every requester, including those embedded in parent stream configs, shares one `DefaultErrorHandler`
that skips 500 and 404 responses and otherwise falls back to the CDK's default error mapping.
"""

import json
from typing import Any, List, Mapping

import pytest
import requests
import yaml
from conftest import _YAML_FILE_PATH, get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.models.declarative_component_schema import DefaultErrorHandler as DefaultErrorHandlerModel
from airbyte_cdk.sources.declarative.parsers.manifest_reference_resolver import ManifestReferenceResolver
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ResponseAction
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


API_TOKEN = "test_api_token"
CONFIG: Mapping[str, Any] = {"api_token": API_TOKEN, "include_closed_tasks": False}
BASE_URL = "https://api.clickup.com/api/v2/"
IGNORED_500_MESSAGE = "Something wrong with API, Please recheck all ids"


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    monkeypatch.setattr("time.sleep", lambda *_args, **_kwargs: None)


def _resolved_manifest() -> Mapping[str, Any]:
    return ManifestReferenceResolver().preprocess_manifest(yaml.safe_load(_YAML_FILE_PATH.read_text()))


def _walk(node: Any):
    if isinstance(node, dict):
        yield node
        for value in node.values():
            yield from _walk(value)
    elif isinstance(node, list):
        for value in node:
            yield from _walk(value)


def _request(path: str) -> HttpRequest:
    return HttpRequest(url=f"{BASE_URL}{path}", headers={"Authorization": API_TOKEN})


def _json(body: Mapping[str, Any], status_code: int = 200) -> HttpResponse:
    return HttpResponse(body=json.dumps(body), status_code=status_code)


def _read(stream_name: str, expecting_exception: bool = False) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    return read(get_source(CONFIG), CONFIG, catalog, expecting_exception=expecting_exception)


def _shared_error_handler():
    definition = _resolved_manifest()["definitions"]["error_handler"]
    return ModelToComponentFactory().create_component(DefaultErrorHandlerModel, definition, config=CONFIG)


def _response(status_code: int) -> requests.Response:
    response = requests.Response()
    response.status_code = status_code
    response._content = b"{}"
    response.request = requests.Request("GET", f"{BASE_URL}user").prepare()
    return response


def test_manifest_has_no_composite_error_handler() -> None:
    composite_handlers = [node for node in _walk(_resolved_manifest()) if node.get("type") == "CompositeErrorHandler"]

    assert not composite_handlers


def test_every_requester_uses_the_shared_error_handler() -> None:
    manifest = _resolved_manifest()
    shared = manifest["definitions"]["error_handler"]
    stream_requesters: List[Mapping[str, Any]] = [
        node for stream in manifest["streams"] for node in _walk(stream) if node.get("type") == "HttpRequester"
    ]

    # 13 top-level streams plus their embedded parent stream requesters.
    assert len(stream_requesters) == 41
    assert all(requester["error_handler"] == shared for requester in stream_requesters)


@pytest.mark.parametrize(
    "status_code, expected_action",
    [
        (200, ResponseAction.SUCCESS),
        (500, ResponseAction.IGNORE),
        (404, ResponseAction.IGNORE),
        (400, ResponseAction.FAIL),
        (401, ResponseAction.FAIL),
        (403, ResponseAction.FAIL),
        (429, ResponseAction.RATE_LIMITED),
        (502, ResponseAction.RETRY),
        (503, ResponseAction.RETRY),
        (504, ResponseAction.RETRY),
        (402, ResponseAction.RETRY),
    ],
)
def test_shared_error_handler_status_mapping(status_code: int, expected_action: ResponseAction) -> None:
    resolution = _shared_error_handler().interpret_response(_response(status_code))

    assert resolution.response_action == expected_action


def test_shared_error_handler_keeps_default_retry_policy() -> None:
    handler = _shared_error_handler()

    assert handler.max_retries == 5
    assert not handler.backoff_strategies


def test_500_is_ignored_with_existing_message() -> None:
    with HttpMocker() as http_mocker:
        user = _request("user")
        http_mocker.get(user, _json({"err": "Internal error"}, status_code=500))

        output = _read("user")

        assert not output.errors
        assert not output.records
        assert output.is_in_logs(IGNORED_500_MESSAGE)
        http_mocker.assert_number_of_calls(user, 1)


def test_404_is_ignored() -> None:
    with HttpMocker() as http_mocker:
        user = _request("user")
        http_mocker.get(user, _json({"err": "Not found"}, status_code=404))

        output = _read("user")

        assert not output.errors
        assert not output.records
        http_mocker.assert_number_of_calls(user, 1)


def test_401_fails_the_sync() -> None:
    with HttpMocker() as http_mocker:
        user = _request("user")
        http_mocker.get(user, _json({"err": "Token invalid"}, status_code=401))

        output = _read("user", expecting_exception=True)

        assert output.errors
        assert not output.records
        http_mocker.assert_number_of_calls(user, 1)


def test_503_is_retried() -> None:
    with HttpMocker() as http_mocker:
        user = _request("user")
        http_mocker.get(user, [_json({"err": "Unavailable"}, status_code=503), _json({"user": {"id": 1, "username": "a"}})])

        output = _read("user")

        assert not output.errors
        assert [record.record.data["id"] for record in output.records] == [1]
        http_mocker.assert_number_of_calls(user, 2)


@pytest.mark.parametrize("status_code", [404, 500])
def test_substream_skips_failing_parent_partition(status_code: int) -> None:
    with HttpMocker() as http_mocker:
        http_mocker.get(_request("team"), _json({"teams": [{"id": "1"}, {"id": "2"}]}))
        http_mocker.get(_request("team/1/space"), _json({"err": "error"}, status_code=status_code))
        http_mocker.get(_request("team/2/space"), _json({"spaces": [{"id": "20", "name": "Space"}]}))

        output = _read("space")

        assert not output.errors
        assert [record.record.data["id"] for record in output.records] == ["20"]
