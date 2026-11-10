# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Tests for the EasyPost error handlers declared in `manifest.yaml`.

Every stream uses one shared `DefaultErrorHandler` (429 -> rate limited, exponential backoff, 3 retries).
`api_keys` adds a 403 filter because the EasyPost API Keys endpoints require a Production API key.
"""

import json

import pytest
import requests
import yaml
from conftest import _YAML_FILE_PATH, get_source

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.sources.declarative.models.declarative_component_schema import DefaultErrorHandler as DefaultErrorHandlerModel
from airbyte_cdk.sources.declarative.parsers.manifest_reference_resolver import ManifestReferenceResolver
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory
from airbyte_cdk.sources.declarative.requesters.error_handlers.backoff_strategies import ExponentialBackoffStrategy
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ResponseAction
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.request import ANY_QUERY_PARAMS


CONFIG = {"username": "test_api_key", "start_date": "2024-01-01T00:00:00Z"}
BASE_URL = "https://api.easypost.com/v2"
PRODUCTION_KEY_MESSAGE = "Need Production API key for accessing this stream"
RATE_LIMIT_MESSAGE = "Rate limits hit"

# stream name -> (path, records field in the response body; None when the body is the record itself)
STREAMS = {
    "batches": ("batches", "batches"),
    "addresses": ("addresses", "addresses"),
    "trackers": ("trackers", "trackers"),
    "metadata_carriers": ("metadata/carriers", "carriers"),
    "end_shippers": ("end_shippers", "end_shippers"),
    "webhooks": ("webhooks", "webhooks"),
    "users_children": ("users/children", "children"),
    "carrier_accounts": ("carrier_accounts", None),
    "api_keys": ("api_keys", None),
}


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    monkeypatch.setattr("time.sleep", lambda *_args, **_kwargs: None)


def _resolved_manifest() -> dict:
    return ManifestReferenceResolver().preprocess_manifest(yaml.safe_load(_YAML_FILE_PATH.read_text()))


def _error_handler(stream_name: str):
    definition = _resolved_manifest()["definitions"]["streams"][stream_name]["retriever"]["requester"]["error_handler"]
    assert definition["type"] == "DefaultErrorHandler"
    return ModelToComponentFactory().create_component(DefaultErrorHandlerModel, definition, config=CONFIG)


def _response(status_code: int) -> requests.Response:
    response = requests.Response()
    response.status_code = status_code
    response._content = json.dumps({"error": {"code": "ERROR", "message": "error"}}).encode()
    response.request = requests.Request("GET", f"{BASE_URL}/example").prepare()
    return response


def _request(stream_name: str) -> HttpRequest:
    path, _ = STREAMS[stream_name]
    return HttpRequest(url=f"{BASE_URL}/{path}", query_params=ANY_QUERY_PARAMS)


def _records_response(stream_name: str) -> HttpResponse:
    _, field = STREAMS[stream_name]
    record = {"id": "rec_1", "name": "rec_1", "created_at": "2024-02-01T00:00:00Z", "updated_at": "2024-02-01T00:00:00Z"}
    body = record if field is None else {field: [record], "has_more": False}
    return HttpResponse(body=json.dumps(body), status_code=200)


def _read(stream_name: str, expecting_exception: bool = False):
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    return read(get_source(CONFIG), CONFIG, catalog, expecting_exception=expecting_exception)


def test_every_error_handler_in_manifest_is_a_single_default_error_handler() -> None:
    handler_types = []

    def walk(node):
        if isinstance(node, dict):
            if "error_handler" in node:
                handler_types.append(node["error_handler"].get("type"))
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(_resolved_manifest())

    assert handler_types
    assert set(handler_types) == {"DefaultErrorHandler"}


@pytest.mark.parametrize("stream_name", list(STREAMS))
def test_every_stream_uses_the_shared_retry_settings(stream_name: str) -> None:
    handler = _error_handler(stream_name)

    assert handler.max_retries == 3
    assert len(handler.backoff_strategies) == 1
    assert isinstance(handler.backoff_strategies[0], ExponentialBackoffStrategy)


@pytest.mark.parametrize("stream_name", list(STREAMS))
def test_429_is_rate_limited_with_rate_limit_message(stream_name: str) -> None:
    resolution = _error_handler(stream_name).interpret_response(_response(429))

    assert resolution.response_action == ResponseAction.RATE_LIMITED
    assert resolution.failure_type == FailureType.transient_error
    assert resolution.error_message == RATE_LIMIT_MESSAGE


def test_api_keys_403_fails_as_config_error_asking_for_production_key() -> None:
    resolution = _error_handler("api_keys").interpret_response(_response(403))

    assert resolution.response_action == ResponseAction.FAIL
    assert resolution.failure_type == FailureType.config_error
    assert resolution.error_message == PRODUCTION_KEY_MESSAGE


@pytest.mark.parametrize("stream_name", [name for name in STREAMS if name != "api_keys"])
def test_403_on_other_streams_keeps_the_default_forbidden_message(stream_name: str) -> None:
    resolution = _error_handler(stream_name).interpret_response(_response(403))

    assert resolution.response_action == ResponseAction.FAIL
    assert resolution.failure_type == FailureType.config_error
    assert PRODUCTION_KEY_MESSAGE not in resolution.error_message


@pytest.mark.parametrize("stream_name", list(STREAMS))
@pytest.mark.parametrize(
    "status_code,action,failure_type",
    [
        pytest.param(401, ResponseAction.FAIL, FailureType.config_error, id="401"),
        pytest.param(404, ResponseAction.FAIL, FailureType.system_error, id="404"),
        pytest.param(500, ResponseAction.RETRY, FailureType.transient_error, id="500"),
        pytest.param(502, ResponseAction.RETRY, FailureType.transient_error, id="502"),
    ],
)
def test_unfiltered_status_codes_fall_back_to_the_cdk_default_mapping(stream_name, status_code, action, failure_type) -> None:
    resolution = _error_handler(stream_name).interpret_response(_response(status_code))

    assert resolution.response_action == action
    assert resolution.failure_type == failure_type


def test_api_keys_read_with_test_key_fails_with_production_key_message() -> None:
    with HttpMocker() as http_mocker:
        request = _request("api_keys")
        http_mocker.get(request, HttpResponse(body=json.dumps({"error": {"code": "FORBIDDEN"}}), status_code=403))

        output = _read("api_keys", expecting_exception=True)

        assert output.errors, "expected the sync to emit an error trace message"
        error = output.errors[0].trace.error
        assert error.failure_type == FailureType.config_error
        assert PRODUCTION_KEY_MESSAGE in error.message
        assert not output.records
        http_mocker.assert_number_of_calls(request, 1)


@pytest.mark.parametrize("stream_name", ["batches", "api_keys"])
def test_429_is_retried_and_the_sync_recovers(stream_name: str) -> None:
    with HttpMocker() as http_mocker:
        request = _request(stream_name)
        http_mocker.get(request, [HttpResponse(body="{}", status_code=429), _records_response(stream_name)])

        output = _read(stream_name)

        assert not output.errors
        assert [record.record.data["id"] for record in output.records] == ["rec_1"]
        http_mocker.assert_number_of_calls(request, 2)
