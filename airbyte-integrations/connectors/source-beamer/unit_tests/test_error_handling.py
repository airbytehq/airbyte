# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Tests for Beamer's NPS error handler."""

import json

import pytest
import requests
import yaml
from conftest import _YAML_FILE_PATH, get_source
from freezegun import freeze_time

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    CompositeErrorHandler as CompositeErrorHandlerModel,
)
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    DefaultErrorHandler as DefaultErrorHandlerModel,
)
from airbyte_cdk.sources.declarative.parsers.manifest_reference_resolver import ManifestReferenceResolver
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory
from airbyte_cdk.sources.declarative.requesters.error_handlers import DefaultErrorHandler
from airbyte_cdk.sources.declarative.requesters.error_handlers.backoff_strategies.exponential_backoff_strategy import (
    ExponentialBackoffStrategy,
)
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ResponseAction
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


CONFIG = {"api_key": "test_api_key", "start_date": "2024-01-01T00:00:00Z"}
BASE_URL = "https://api.getbeamer.com/v0/"


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    slept = []
    monkeypatch.setattr("time.sleep", lambda seconds=0, *_args, **_kwargs: slept.append(seconds))
    return slept


def _resolved_manifest():
    return ManifestReferenceResolver().preprocess_manifest(yaml.safe_load(_YAML_FILE_PATH.read_text()))


def _nps_error_handler():
    manifest = _resolved_manifest()
    definition = manifest["definitions"]["streams"]["nps"]["retriever"]["requester"]["error_handler"]
    model = CompositeErrorHandlerModel if definition.get("type") == "CompositeErrorHandler" else DefaultErrorHandlerModel
    return ModelToComponentFactory().create_component(model, definition, config={})


def _read_nps(expecting_exception=False):
    catalog = CatalogBuilder().with_stream("nps", SyncMode.full_refresh).build()
    return read(get_source(CONFIG), CONFIG, catalog, expecting_exception=expecting_exception)


def _nps_request():
    return HttpRequest(
        url=f"{BASE_URL}nps",
        query_params={
            "dateFrom": "2024-01-01T00:00:00Z",
            "dateTo": "2024-01-03T00:00:00Z",
            "maxResults": "100",
        },
        headers={"Authorization": "Bearer test_api_key"},
    )


def _response(status_code):
    response = requests.Response()
    response.status_code = status_code
    response.request = requests.Request("GET", f"{BASE_URL}nps").prepare()
    response.url = response.request.url
    response.headers["Content-Type"] = "application/json"
    response._content = b"{}"
    return response


def test_manifest_has_no_composite_error_handler() -> None:
    manifest = _resolved_manifest()
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


def test_nps_error_handler_retries_five_times_with_exponential_backoff() -> None:
    handler = _nps_error_handler()

    assert isinstance(handler, DefaultErrorHandler)
    assert handler.max_retries == 5
    assert len(handler.backoff_strategies) == 1
    strategy = handler.backoff_strategies[0]
    assert isinstance(strategy, ExponentialBackoffStrategy)
    assert strategy.backoff_time(response_or_exception=None, attempt_count=0) == 5


@pytest.mark.parametrize(
    "status_code, action, failure_type",
    [
        (200, ResponseAction.SUCCESS, None),
        (400, ResponseAction.FAIL, FailureType.system_error),
        (401, ResponseAction.FAIL, FailureType.config_error),
        (403, ResponseAction.FAIL, FailureType.config_error),
        (404, ResponseAction.FAIL, FailureType.system_error),
        (429, ResponseAction.RATE_LIMITED, FailureType.transient_error),
        (500, ResponseAction.RETRY, FailureType.transient_error),
        (503, ResponseAction.RETRY, FailureType.transient_error),
    ],
)
def test_nps_error_handler_classifies_responses(status_code, action, failure_type) -> None:
    resolution = _nps_error_handler().interpret_response(_response(status_code))

    assert resolution.response_action == action
    assert resolution.failure_type == failure_type


@freeze_time("2024-01-03T00:00:00Z")
def test_nps_retries_server_error_then_reads_records() -> None:
    request = _nps_request()
    with HttpMocker() as http_mocker:
        http_mocker.get(
            request,
            [
                HttpResponse(body="{}", status_code=500),
                HttpResponse(
                    body=json.dumps([{"id": "1", "date": "2024-01-02T00:00:00Z", "score": 9}]),
                    status_code=200,
                ),
            ],
        )

        output = _read_nps()

    assert len(output.records) == 1
    assert output.errors == []
    http_mocker.assert_number_of_calls(request, 2)


@freeze_time("2024-01-03T00:00:00Z")
def test_nps_401_fails_as_config_error() -> None:
    request = _nps_request()
    with HttpMocker() as http_mocker:
        http_mocker.get(request, HttpResponse(body="{}", status_code=401))

        output = _read_nps(expecting_exception=True)

    assert output.errors
    assert output.errors[0].trace.error.failure_type == FailureType.config_error
    http_mocker.assert_number_of_calls(request, 1)
