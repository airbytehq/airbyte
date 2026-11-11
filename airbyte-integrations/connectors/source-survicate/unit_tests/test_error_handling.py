# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Tests for Survicate error handlers declared in `manifest.yaml`."""

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


CONFIG = {"api_key": "test_api_key", "start_date": "2024-01-01T00:00:00Z"}
BASE_URL = "https://data-api.survicate.com/v2"
RATE_LIMIT_MESSAGE = "Rate limit hit"
STREAMS = [
    "surveys",
    "surveys_questions",
    "surveys_responses",
    "respondents_attributes",
    "respondents_responses",
]
DEFAULT_STATUS_MAPPINGS = [
    pytest.param(401, ResponseAction.FAIL, FailureType.config_error, id="401"),
    pytest.param(403, ResponseAction.FAIL, FailureType.config_error, id="403"),
    pytest.param(404, ResponseAction.FAIL, FailureType.system_error, id="404"),
    pytest.param(500, ResponseAction.RETRY, FailureType.transient_error, id="500"),
    pytest.param(502, ResponseAction.RETRY, FailureType.transient_error, id="502"),
]


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    monkeypatch.setattr("time.sleep", lambda *_args, **_kwargs: None)


def _resolved_manifest() -> dict:
    return ManifestReferenceResolver().preprocess_manifest(yaml.safe_load(_YAML_FILE_PATH.read_text()))


def _error_handler_definition(stream_name: str) -> dict:
    return _resolved_manifest()["definitions"]["streams"][stream_name]["retriever"]["requester"]["error_handler"]


def _error_handler(stream_name: str):
    definition = _error_handler_definition(stream_name)
    return ModelToComponentFactory().create_component(DefaultErrorHandlerModel, definition, config=CONFIG)


def _response(status_code: int) -> requests.Response:
    response = requests.Response()
    response.status_code = status_code
    response._content = json.dumps({"error": {"code": "ERROR", "message": "error"}}).encode()
    response.request = requests.Request("GET", f"{BASE_URL}/example").prepare()
    return response


def test_every_error_handler_in_manifest_is_a_single_default_error_handler() -> None:
    manifest = _resolved_manifest()
    handler_types = [stream["retriever"]["requester"]["error_handler"].get("type") for stream in manifest["streams"]]

    assert handler_types
    assert len(handler_types) == 5
    assert set(handler_types) == {"DefaultErrorHandler"}


@pytest.mark.parametrize("stream_name", STREAMS)
def test_each_stream_uses_a_default_error_handler_with_retry_settings(stream_name: str) -> None:
    handler = _error_handler(stream_name)

    assert type(handler).__name__ == "DefaultErrorHandler"
    assert handler.max_retries == 3
    assert len(handler.backoff_strategies) == 1
    assert isinstance(handler.backoff_strategies[0], ExponentialBackoffStrategy)
    assert float(handler.backoff_strategies[0].factor) == 2


@pytest.mark.parametrize("stream_name", STREAMS)
def test_429_is_rate_limited_with_rate_limit_message(stream_name: str) -> None:
    resolution = _error_handler(stream_name).interpret_response(_response(429))

    assert resolution.response_action == ResponseAction.RATE_LIMITED
    assert resolution.failure_type == FailureType.transient_error
    assert resolution.error_message == RATE_LIMIT_MESSAGE


@pytest.mark.parametrize("stream_name", STREAMS)
@pytest.mark.parametrize("status_code,action,failure_type", DEFAULT_STATUS_MAPPINGS)
def test_unfiltered_status_codes_fall_back_to_the_cdk_default_mapping(
    stream_name: str, status_code: int, action: ResponseAction, failure_type: FailureType
) -> None:
    resolution = _error_handler(stream_name).interpret_response(_response(status_code))

    assert resolution.response_action == action
    assert resolution.failure_type == failure_type


def test_surveys_read_retries_rate_limit_and_recovers() -> None:
    catalog = CatalogBuilder().with_stream("surveys", SyncMode.full_refresh).build()
    request = HttpRequest(url=f"{BASE_URL}/surveys", query_params=ANY_QUERY_PARAMS)
    rate_limited_response = HttpResponse(body="{}", status_code=429)
    records_response = HttpResponse(
        body=json.dumps(
            {
                "data": [{"id": "s1", "created_at": "2024-02-01T00:00:00.000000Z"}],
                "pagination": {"has_more": False, "next_url": None},
            }
        ),
        status_code=200,
    )

    with HttpMocker() as http_mocker:
        http_mocker.get(request, [rate_limited_response, records_response])
        output = read(get_source(CONFIG), CONFIG, catalog)

        assert not output.errors
        assert [record.record.data["id"] for record in output.records] == ["s1"]
        http_mocker.assert_number_of_calls(request, 2)
