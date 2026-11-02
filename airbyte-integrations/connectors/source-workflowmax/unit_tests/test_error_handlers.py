# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
import time
from collections.abc import Iterator
from typing import Any

import pytest
import requests
import requests_mock
import yaml
from conftest import MANIFEST_PATH, get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.models.declarative_component_schema import DefaultErrorHandler as DefaultErrorHandlerModel
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory
from airbyte_cdk.sources.declarative.requesters.error_handlers.backoff_strategies.exponential_backoff_strategy import (
    ExponentialBackoffStrategy,
)
from airbyte_cdk.sources.declarative.requesters.error_handlers.default_error_handler import DefaultErrorHandler
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ResponseAction
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read


_CONFIG = {
    "account_id": "account",
    "start_date": "2024-01-01T00:00:00Z",
    "client_id": "client-id",
    "client_secret": "client-secret",
    "refresh_token": "refresh-token",
}
_STREAMS = [
    "stafflist",
    "clientlist",
    "clients_documents",
    "clientgrouplist",
    "costlist",
    "invoice_current",
    "invoicelist",
    "joblist",
    "job_tasks",
    "leadlist",
    "purchaseorderlist",
    "tasklist",
    "quotelist",
    "supplierlist",
    "timelist",
]
_TOKEN_URL = "https://oauth.workflowmax2.com/oauth/token"
_STAFFLIST_URL = "https://api.workflowmax2.com/staff.api/list"


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


def _response(status_code: int) -> requests.Response:
    response = requests.Response()
    response.status_code = status_code
    response.request = requests.Request("GET", _STAFFLIST_URL).prepare()
    response.url = response.request.url
    return response


def _read_stafflist(mocker: requests_mock.Mocker) -> tuple[EntrypointOutput, Any]:
    mocker.post(
        _TOKEN_URL,
        json={"access_token": "access-token", "refresh_token": "refresh-token", "expires_in": 1800},
    )
    endpoint = mocker.get(
        _STAFFLIST_URL,
        [
            {"status_code": 429, "text": "Rate limited"},
            {
                "status_code": 200,
                "headers": {"Content-Type": "application/xml"},
                "text": "<Response><StaffList><Staff><UUID>staff-1</UUID><Name>Test User</Name></Staff></StaffList></Response>",
            },
        ],
    )
    catalog = CatalogBuilder().with_stream("stafflist", SyncMode.full_refresh).build()
    return read(get_source(_CONFIG), _CONFIG, catalog), endpoint


def test_manifest_has_no_composite_error_handler() -> None:
    manifest = yaml.safe_load(MANIFEST_PATH.read_text())

    composite_handler_type = "Composite" + "ErrorHandler"
    assert not any(node.get("type") == composite_handler_type for node in _walk(manifest))


@pytest.mark.parametrize("stream_name", _STREAMS)
def test_stream_error_handler(stream_name: str) -> None:
    handler, definition = _handler(stream_name)

    assert handler.max_retries == 3
    assert len(handler.backoff_strategies) == 1
    strategy = handler.backoff_strategies[0]
    assert isinstance(strategy, ExponentialBackoffStrategy)
    assert float(strategy.factor) == 2
    assert handler.backoff_time(response_or_exception=_response(429), attempt_count=1) == 4
    assert handler.backoff_time(response_or_exception=_response(429), attempt_count=3) == 16

    expected_actions = {
        200: ResponseAction.SUCCESS,
        429: ResponseAction.RATE_LIMITED,
        500: ResponseAction.RETRY,
        401: ResponseAction.FAIL,
        403: ResponseAction.FAIL,
        404: ResponseAction.FAIL,
    }
    for status_code, expected_action in expected_actions.items():
        result = handler.interpret_response(_response(status_code))
        assert result.response_action == expected_action
        if status_code == 429:
            assert result.error_message == "Rate limits hit"

    assert definition["max_retries"] == 3
    assert definition["backoff_strategies"] == [{"type": "ExponentialBackoffStrategy", "factor": 2}]


def test_stafflist_retries_rate_limit_and_emits_record(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(time, "sleep", lambda _: None)
    with requests_mock.Mocker() as mocker:
        output, endpoint = _read_stafflist(mocker)

    assert output.records
    assert endpoint.call_count == 2
