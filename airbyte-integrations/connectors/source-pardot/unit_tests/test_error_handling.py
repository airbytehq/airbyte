# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
import time
from datetime import timedelta

import pytest
import requests
import yaml
from conftest import get_source
from freezegun import freeze_time

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.sources.declarative.models.declarative_component_schema import DefaultErrorHandler as DefaultErrorHandlerModel
from airbyte_cdk.sources.declarative.parsers.manifest_reference_resolver import ManifestReferenceResolver
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ResponseAction
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.request import ANY_QUERY_PARAMS
from airbyte_cdk.test.state_builder import StateBuilder


_CONFIG = {
    "client_id": "client_id",
    "client_secret": "client_secret",
    "refresh_token": "refresh_token",
    "pardot_business_unit_id": "business_unit_id",
    "start_date": "2024-01-01T00:00:00Z",
    "is_sandbox": False,
}
_TOKEN_REQUEST = HttpRequest(
    url="https://login.salesforce.com/services/oauth2/token",
    query_params=ANY_QUERY_PARAMS,
    body="client_id=client_id&grant_type=refresh_token&client_secret=client_secret&refresh_token=refresh_token",
)
_CAMPAIGNS_REQUEST = HttpRequest(
    url="https://pi.pardot.com/api/v5/objects/campaigns",
    query_params=ANY_QUERY_PARAMS,
)
_DAILY_LIMIT_MESSAGE = (
    "Reached the Pardot daily API request limit. The limit resets at the start of the next day in the Pardot account's time zone."
)
_COMPOSITE_HANDLER_TYPE = "".join(("Composite", "ErrorHandler"))


@pytest.fixture
def sleeps(monkeypatch: pytest.MonkeyPatch) -> list[float]:
    recorded: list[float] = []
    with freeze_time("2025-01-01T00:00:00Z") as frozen:

        def advance_clock(seconds: float = 0, *_args, **_kwargs) -> None:
            if seconds:
                recorded.append(seconds)
            frozen.tick(delta=timedelta(seconds=seconds))

        monkeypatch.setattr(time, "sleep", advance_clock)
        yield recorded


def _read_campaigns() -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream("campaigns", SyncMode.incremental).build()
    source = get_source(_CONFIG, catalog)
    return read(source, _CONFIG, catalog, StateBuilder().build(), expecting_exception=True)


def _mock_authentication(http_mocker: HttpMocker) -> None:
    http_mocker.post(_TOKEN_REQUEST, HttpResponse(body='{"access_token":"token"}', status_code=200))


def _error_trace(output: EntrypointOutput):
    assert output.errors, "expected the sync to emit an error trace"
    return output.errors[0].trace.error


def _resolved_manifest() -> dict:
    from conftest import _YAML_FILE_PATH

    return ManifestReferenceResolver().preprocess_manifest(yaml.safe_load(_YAML_FILE_PATH.read_text()))


def test_manifest_has_no_composite_error_handler() -> None:
    manifest = _resolved_manifest()
    found = []

    def walk(node) -> None:
        if isinstance(node, dict):
            if node.get("type") == _COMPOSITE_HANDLER_TYPE:
                found.append(node)
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(manifest)

    assert not found


def test_every_stream_uses_the_shared_error_handler() -> None:
    manifest = _resolved_manifest()
    shared_handler = manifest["definitions"]["error_handler"]
    streams = manifest["streams"]

    assert len(streams) == 33
    assert shared_handler["type"] == "DefaultErrorHandler"
    assert all(stream["retriever"]["requester"]["error_handler"] == shared_handler for stream in streams)


def test_daily_limit_429_uses_daily_limit_message(sleeps: list[float]) -> None:
    response = HttpResponse(body='{"code":122,"message":"Daily API rate limit met"}', status_code=429)
    with HttpMocker() as http_mocker:
        _mock_authentication(http_mocker)
        http_mocker.get(_CAMPAIGNS_REQUEST, response)

        error = _error_trace(_read_campaigns())

    assert _DAILY_LIMIT_MESSAGE in error.internal_message
    assert error.message == "API rate limit exceeded."
    assert error.failure_type == FailureType.transient_error
    http_mocker.assert_number_of_calls(_CAMPAIGNS_REQUEST, 2)
    assert sleeps == [7201]


def test_daily_limit_message_is_rate_limited_on_any_status() -> None:
    manifest = _resolved_manifest()
    handler_definition = manifest["definitions"]["error_handler"]
    handler = ModelToComponentFactory().create_component(DefaultErrorHandlerModel, handler_definition, config={})
    response = requests.Response()
    response.status_code = 400
    response.request = requests.Request("GET", "https://pi.pardot.com/api/v5/objects/campaigns").prepare()
    response.url = response.request.url
    response.headers["Content-Type"] = "application/json"
    response._content = b'{"@attributes":{"stat":"fail","err_code":122},"err":"Daily API rate limit met"}'

    resolution = handler.interpret_response(response)

    assert resolution.response_action == ResponseAction.RATE_LIMITED
    assert resolution.error_message == _DAILY_LIMIT_MESSAGE


def test_429_without_daily_text_keeps_default_message(sleeps: list[float]) -> None:
    response = HttpResponse(
        body='{"code":66,"message":"You have exceeded your concurrent request limit. Please wait, before trying again"}',
        status_code=429,
    )
    with HttpMocker() as http_mocker:
        _mock_authentication(http_mocker)
        http_mocker.get(_CAMPAIGNS_REQUEST, response)

        error = _error_trace(_read_campaigns())

    assert error.message == "API rate limit exceeded."
    assert "HTTP Status Code: 429. Error: Too many requests." in error.internal_message
    assert _DAILY_LIMIT_MESSAGE not in error.internal_message
    assert error.failure_type == FailureType.transient_error
    http_mocker.assert_number_of_calls(_CAMPAIGNS_REQUEST, 2)
    assert sleeps == [7201]


def test_server_error_waits_7200_seconds_once_before_failing(sleeps: list[float]) -> None:
    response = HttpResponse(body='{"code":500,"message":"Server error"}', status_code=500)
    with HttpMocker() as http_mocker:
        _mock_authentication(http_mocker)
        http_mocker.get(_CAMPAIGNS_REQUEST, response)

        _error_trace(_read_campaigns())

    http_mocker.assert_number_of_calls(_CAMPAIGNS_REQUEST, 2)
    assert sleeps == [7201]


def test_401_fails_without_retry(sleeps: list[float]) -> None:
    response = HttpResponse(body='{"code":66,"message":"Invalid access token"}', status_code=401)
    with HttpMocker() as http_mocker:
        _mock_authentication(http_mocker)
        http_mocker.get(_CAMPAIGNS_REQUEST, response)

        error = _error_trace(_read_campaigns())

    assert error.failure_type == FailureType.config_error
    http_mocker.assert_number_of_calls(_CAMPAIGNS_REQUEST, 1)
    assert sleeps == []
