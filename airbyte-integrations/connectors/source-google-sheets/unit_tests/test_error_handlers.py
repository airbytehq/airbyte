#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import json
from copy import deepcopy
from typing import Any, Iterator
from unittest.mock import Mock, patch

import pytest
import requests
from components import GridDataErrorHandler

from airbyte_cdk.connector_builder.connector_builder_handler import resolve_manifest
from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.declarative import models
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory
from airbyte_cdk.sources.declarative.requesters.error_handlers.default_error_handler import DefaultErrorHandler
from airbyte_cdk.sources.declarative.requesters.error_handlers.http_response_filter import HttpResponseFilter
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.sources.streams.http.error_handlers import ErrorHandler
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ResponseAction
from unit_tests.conftest import _YAML_FILE_PATH
from unit_tests.integration.conftest import oauth_credentials


CONFIG = {"spreadsheet_id": "a_spreadsheet_id", "credentials": oauth_credentials}
RESOLVED_MANIFEST = resolve_manifest(source=YamlDeclarativeSource(path_to_yaml=str(_YAML_FILE_PATH), config=CONFIG))
assert RESOLVED_MANIFEST.record is not None
MANIFEST = RESOLVED_MANIFEST.record.data["manifest"]
HANDLER_PATHS: dict[str, list[str | int]] = {
    "schema": ["dynamic_streams", 0, "stream_template", "schema_loader", "retriever", "requester", "error_handler"],
    "metadata": ["definitions", "streams", "get_spreadsheet_info_and_sheets", "retriever", "requester", "error_handler"],
    "grid": ["definitions", "retrievers", "components_resolver_retriever", "requester", "error_handler"],
}


def handler_definition(location: str) -> dict[str, Any]:
    definition = MANIFEST
    for key in HANDLER_PATHS[location]:
        definition = definition[key]
    return definition


def build_handler(definition: dict[str, Any]) -> ErrorHandler:
    return ModelToComponentFactory().create_component(
        model_type=getattr(models, definition["type"]), component_definition=deepcopy(definition), config=CONFIG
    )


def response(status: int, body: dict) -> requests.Response:
    result = requests.Response()
    result.status_code = status
    result._content = json.dumps(body).encode()
    result.request = requests.Request(
        "GET", "https://sheets.googleapis.com/v4/spreadsheets/a_spreadsheet_id?includeGridData=true&ranges=TestSheet!1:1"
    ).prepare()
    return result


@pytest.fixture(params=HANDLER_PATHS)
def handler(request: pytest.FixtureRequest) -> ErrorHandler:
    return build_handler(handler_definition(request.param))


def walk_components(component: object) -> Iterator[dict]:
    if isinstance(component, dict):
        yield component
        for value in component.values():
            yield from walk_components(value)
    elif isinstance(component, list):
        for value in component:
            yield from walk_components(value)


def test_handlers_are_not_chained() -> None:
    assert not any("error_handlers" in component and "type" in component for component in walk_components(MANIFEST))


def test_handler_retry_configuration(handler: ErrorHandler) -> None:
    assert isinstance(handler, DefaultErrorHandler)
    assert handler.max_retries == 5
    assert handler.max_time == 600
    assert handler.backoff_strategies is not None
    assert len(handler.backoff_strategies) == 1
    assert handler.backoff_strategies[0].__class__.__name__ == "ExponentialBackoffStrategy"


@pytest.mark.parametrize(
    "status,body,action,message",
    [
        (
            403,
            {"error": {"code": 403, "message": "Sheets API has not been used"}},
            ResponseAction.FAIL,
            "A required Google API is disabled",
        ),
        (401, {}, ResponseAction.FAIL, "Google authentication failed"),
        (403, {}, ResponseAction.FAIL, "Spreadsheet access is denied"),
        (404, {}, ResponseAction.FAIL, "Spreadsheet was not found or is inaccessible"),
        (429, {}, ResponseAction.RATE_LIMITED, "Rate limit has been"),
    ],
    ids=["api_disabled", "unauthorized", "forbidden", "not_found", "rate_limit"],
)
def test_shared_response_filters(handler: ErrorHandler, status: int, body: dict, action: ResponseAction, message: str) -> None:
    resolution = handler.interpret_response(response(status, body))
    assert resolution.response_action == action
    assert resolution.error_message is not None and message in resolution.error_message
    if action == ResponseAction.FAIL:
        assert resolution.failure_type == FailureType.config_error


@pytest.mark.parametrize("sheet_count", [0, 2])
@pytest.mark.parametrize("location", ["schema", "grid"])
def test_expected_one_sheet_filter(location: str, sheet_count: int) -> None:
    handler = build_handler(handler_definition(location))
    resolution = handler.interpret_response(response(200, {"sheets": [{}] * sheet_count}))
    assert resolution.response_action == ResponseAction.FAIL
    assert resolution.failure_type == FailureType.config_error
    assert resolution.error_message is not None and "exactly 1 sheet" in resolution.error_message


@pytest.mark.parametrize("location", ["schema", "grid"])
def test_duplicate_headers_filter(location: str) -> None:
    handler = build_handler(handler_definition(location))
    body = {"sheets": [{"properties": {"title": "TestSheet"}, "data": [{"rowData": [{"values": [{"formattedValue": "Name"}] * 2}]}]}]}
    resolution = handler.interpret_response(response(200, body))
    assert resolution.response_action == ResponseAction.IGNORE
    assert resolution.error_message is not None and "Duplicate headers found in sheet TestSheet" in resolution.error_message
    assert "Name" in resolution.error_message


@pytest.mark.parametrize("status", [500, 502, 503])
def test_metadata_server_error_filter(status: int) -> None:
    handler = build_handler(handler_definition("metadata"))
    resolution = handler.interpret_response(response(status, {}))
    assert resolution.response_action == ResponseAction.RETRY
    assert resolution.error_message is not None and "There was an issue" in resolution.error_message


@pytest.mark.parametrize("status", [200, 201, 204, 301, 400, 402, 405, 408, 410, 415, 418, 422, 501, 502, 503, 504])
def test_default_status_mapping(handler: ErrorHandler, status: int) -> None:
    body = {"sheets": [{"data": [{"rowData": [{"values": [{"formattedValue": "Name"}]}]}]}]}
    result = response(status, body)
    expected = DefaultErrorHandler(config=CONFIG, parameters={}).interpret_response(result)
    actual = handler.interpret_response(result)
    assert actual.response_action == expected.response_action
    assert actual.failure_type == expected.failure_type


@pytest.mark.parametrize("exception", [requests.ConnectionError("offline"), requests.Timeout("timeout"), ValueError("unexpected")])
def test_default_exception_mapping(handler: ErrorHandler, exception: Exception) -> None:
    expected = DefaultErrorHandler(config=CONFIG, parameters={}).interpret_response(exception)
    assert handler.interpret_response(exception) == expected


@pytest.mark.parametrize("status,action", [(200, ResponseAction.SUCCESS), (429, ResponseAction.RATE_LIMITED)])
def test_standalone_grid_handler_delegates(status: int, action: ResponseAction) -> None:
    handler = GridDataErrorHandler(
        config=CONFIG,
        parameters={},
        response_filters=[HttpResponseFilter(config=CONFIG, parameters={}, http_codes={429}, action=ResponseAction.RATE_LIMITED)],
    )
    assert handler.interpret_response(response(status, {})).response_action == action


@pytest.mark.parametrize(
    "probe_result,action", [(200, ResponseAction.IGNORE), (503, ResponseAction.RETRY), (requests.Timeout("offline"), ResponseAction.RETRY)]
)
@patch("components.requests.get")
def test_configured_grid_handler_probes_before_filters(mock_get: Mock, probe_result: int | Exception, action: ResponseAction) -> None:
    if isinstance(probe_result, Exception):
        mock_get.side_effect = probe_result
    else:
        mock_get.return_value = response(probe_result, {})
    handler = build_handler(handler_definition("grid"))
    resolution = handler.interpret_response(response(500, {"sheets": []}))
    assert resolution.response_action == action
    assert resolution.failure_type == (FailureType.transient_error if action == ResponseAction.RETRY else None)
    mock_get.assert_called_once_with(
        "https://sheets.googleapis.com/v4/spreadsheets/a_spreadsheet_id?includeGridData=false&ranges=TestSheet!1:1", headers={}, timeout=30
    )
