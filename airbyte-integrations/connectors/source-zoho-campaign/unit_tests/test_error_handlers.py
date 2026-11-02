# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from collections.abc import Iterator
from typing import Any

import pytest
import requests
import requests_mock
import yaml

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.models.declarative_component_schema import DefaultErrorHandler as DefaultErrorHandlerModel
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory
from airbyte_cdk.sources.declarative.requesters.error_handlers.default_error_handler import DefaultErrorHandler
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ResponseAction
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from conftest import MANIFEST_PATH, get_source


_CONFIG = {
    "client_id_2": "id",
    "client_secret_2": "secret",
    "client_refresh_token": "refresh",
    "data_center": "com",
}
_CONSTANT_BACKOFF_STREAMS = [
    "recent_campaigns",
    "subscribers",
    "campaign_recipients",
    "campaign_reports",
    "recent_sent_campaigns",
    "totalcontacts",
    "topics",
    "campaign_details",
    "all_tags",
]
_BASE_URL = "https://campaigns.zoho.com/api/v1.1"
_TOKEN_URL = "https://accounts.zoho.com/oauth/v2/token"
_MAILING_LISTS_URL = f"{_BASE_URL}/getmailinglists"


def _walk(value: Any) -> Iterator[dict[str, Any]]:
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk(child)


def _handler(stream_name: str) -> tuple[DefaultErrorHandler, dict[str, Any]]:
    source = get_source(_CONFIG)
    stream_definition = next(stream for stream in source.resolved_manifest["streams"] if stream["name"] == stream_name)
    definition = stream_definition["retriever"]["requester"]["error_handler"]
    assert definition["type"] == "DefaultErrorHandler"
    return ModelToComponentFactory().create_component(DefaultErrorHandlerModel, definition, _CONFIG), definition


def _response(status_code: int, body: dict[str, Any] | None = None) -> requests.Response:
    response = requests.Response()
    response.status_code = status_code
    response.headers["Content-Type"] = "application/json"
    response._content = json.dumps(body or {}).encode()
    response.request = requests.Request("GET", _MAILING_LISTS_URL).prepare()
    response.url = response.request.url
    return response


def _sync_mailing_lists(
    mocker: requests_mock.Mocker,
    status_code: int,
    body: dict[str, Any],
) -> EntrypointOutput:
    mocker.post(
        _TOKEN_URL,
        json={"access_token": "token", "refresh_token": "refresh", "expires_in": 3600},
    )
    mocker.get(_MAILING_LISTS_URL, status_code=status_code, json=body)
    catalog = CatalogBuilder().with_stream("mailing_lists", SyncMode.full_refresh).build()
    return read(get_source(_CONFIG), _CONFIG, catalog)


def test_manifest_has_no_composite_error_handler() -> None:
    manifest = yaml.safe_load(MANIFEST_PATH.read_text())

    composite_handler_type = "Composite" + "ErrorHandler"
    assert not any(node.get("type") == composite_handler_type for node in _walk(manifest))


@pytest.mark.parametrize("stream_name", _CONSTANT_BACKOFF_STREAMS)
def test_constant_backoff_streams(stream_name: str) -> None:
    handler, _ = _handler(stream_name)

    for status_code in (429, 500):
        response = _response(status_code)
        assert handler.backoff_time(response_or_exception=response, attempt_count=1) == 1800
        assert handler.backoff_time(response_or_exception=response, attempt_count=3) == 1800

    assert handler.max_retries == 5
    expected_actions = {
        200: ResponseAction.SUCCESS,
        429: ResponseAction.RATE_LIMITED,
        500: ResponseAction.RETRY,
        401: ResponseAction.FAIL,
        403: ResponseAction.FAIL,
        404: ResponseAction.FAIL,
    }
    for status_code, expected_action in expected_actions.items():
        assert handler.interpret_response(_response(status_code)).response_action == expected_action


def test_mailing_lists_error_handler() -> None:
    handler, definition = _handler("mailing_lists")

    assert "response_filters" not in definition
    assert "backoff_strategies" not in definition
    assert handler.interpret_response(_response(200, {"code": "2401"})).response_action == ResponseAction.SUCCESS
    assert handler.interpret_response(_response(400, {"code": 2401})).response_action == ResponseAction.FAIL
    assert handler.interpret_response(_response(401)).response_action == ResponseAction.FAIL
    assert handler.interpret_response(_response(404)).response_action == ResponseAction.FAIL
    assert handler.interpret_response(_response(429)).response_action == ResponseAction.RATE_LIMITED
    assert handler.interpret_response(_response(500)).response_action == ResponseAction.RETRY
    assert handler.backoff_time(response_or_exception=_response(500), attempt_count=1) != 1800


def test_mailing_lists_successful_read_emits_one_record() -> None:
    with requests_mock.Mocker() as mocker:
        output = _sync_mailing_lists(
            mocker,
            200,
            {"list_of_details": [{"listunino": 1, "listname": "a"}]},
        )

    assert len(output.records) == 1
    assert not output.errors


def test_mailing_lists_400_2401_emits_error_trace_instead_of_ignoring() -> None:
    with requests_mock.Mocker() as mocker:
        output = _sync_mailing_lists(mocker, 400, {"code": 2401, "message": "x"})

    assert output.records == []
    assert output.errors
    assert output.errors[0].trace.error.message
