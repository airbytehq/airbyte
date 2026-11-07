# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest
import requests
import yaml
from conftest import _YAML_FILE_PATH, get_source
from freezegun import freeze_time

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.sources.declarative.models.declarative_component_schema import DefaultErrorHandler as DefaultErrorHandlerModel
from airbyte_cdk.sources.declarative.parsers.manifest_reference_resolver import ManifestReferenceResolver
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory
from airbyte_cdk.sources.declarative.requesters.error_handlers.backoff_strategies.exponential_backoff_strategy import (
    ExponentialBackoffStrategy,
)
from airbyte_cdk.sources.declarative.requesters.error_handlers.default_error_handler import DefaultErrorHandler
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_CONFIG = {
    "advertiserId": "123",
    "api_key": "test-key",
    "step_increment": "P400D",
    "lookback_days": 0,
    "start_date": "2026-10-29",
}
_TRANSACTIONS_URL = "https://api.awin.com/advertisers/123/transactions/"
_TRANSACTIONS_REQUEST = HttpRequest(url=_TRANSACTIONS_URL, query_params="any query_parameters")


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    slept = []
    monkeypatch.setattr("time.sleep", lambda seconds=0, *_args, **_kwargs: slept.append(seconds))
    return slept


def _resolved_manifest() -> dict:
    return ManifestReferenceResolver().preprocess_manifest(yaml.safe_load(_YAML_FILE_PATH.read_text()))


def _transactions_handler():
    source = get_source(_CONFIG)
    stream = next(stream for stream in source.streams(config=_CONFIG) if stream.name == "transactions")
    return next(iter(stream.generate_partitions()))._retriever.requester.error_handler


def _read_transactions(*, expecting_exception: bool = False):
    catalog = CatalogBuilder().with_stream("transactions", SyncMode.full_refresh).build()
    source = get_source(_CONFIG)
    return read(source, _CONFIG, catalog, expecting_exception=expecting_exception)


def _response(status_code: int) -> requests.Response:
    response = requests.Response()
    response.status_code = status_code
    response._content = b"{}"
    response.headers["Content-Type"] = "application/json"
    response.request = requests.Request("GET", _TRANSACTIONS_URL).prepare()
    response.url = _TRANSACTIONS_URL
    return response


def _success_response() -> HttpResponse:
    return HttpResponse(
        body=json.dumps([{"id": 1, "transactionDate": "2026-10-30T12:00:00"}]),
        status_code=200,
    )


def test_manifest_has_no_composite_error_handler() -> None:
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

    walk(_resolved_manifest())

    assert not composite_handlers


def test_transactions_error_handler_uses_three_exponential_retries() -> None:
    manifest = _resolved_manifest()
    stream = next(stream for stream in manifest["streams"] if stream["name"] == "transactions")
    definition = stream["retriever"]["requester"]["error_handler"]
    handler = ModelToComponentFactory().create_component(DefaultErrorHandlerModel, definition, config={})

    assert isinstance(handler, DefaultErrorHandler)
    assert handler.max_retries == 3
    assert len(handler.backoff_strategies) == 1
    strategy = handler.backoff_strategies[0]
    assert isinstance(strategy, ExponentialBackoffStrategy)
    assert float(strategy.factor) == 2


@pytest.mark.parametrize("status_code", [200, 400, 401, 403, 404, 429, 500, 502, 503])
def test_transactions_handler_matches_cdk_default_status_mapping(status_code: int) -> None:
    manifest_result = _transactions_handler().interpret_response(_response(status_code))
    default_handler = ModelToComponentFactory().create_component(
        DefaultErrorHandlerModel,
        {"type": "DefaultErrorHandler"},
        config={},
    )
    default_result = default_handler.interpret_response(_response(status_code))

    assert (
        manifest_result.response_action,
        manifest_result.failure_type,
        manifest_result.error_message,
    ) == (
        default_result.response_action,
        default_result.failure_type,
        default_result.error_message,
    )


@freeze_time("2026-11-01T12:00:00Z")
def test_429_then_200_retries_and_reads_one_transaction(no_sleep) -> None:
    with HttpMocker() as http_mocker:
        http_mocker.get(
            _TRANSACTIONS_REQUEST,
            [HttpResponse(body="{}", status_code=429), _success_response()],
        )

        output = _read_transactions()

        assert not output.errors
        assert len(output.records) == 1
        http_mocker.assert_number_of_calls(_TRANSACTIONS_REQUEST, 2)

    assert no_sleep
    assert no_sleep[0] > 0


@freeze_time("2026-11-01T12:00:00Z")
def test_429_retries_three_times_then_fails() -> None:
    with HttpMocker() as http_mocker:
        http_mocker.get(
            _TRANSACTIONS_REQUEST,
            [HttpResponse(body="{}", status_code=429) for _ in range(4)],
        )

        output = _read_transactions(expecting_exception=True)

        assert output.errors
        http_mocker.assert_number_of_calls(_TRANSACTIONS_REQUEST, 4)


@freeze_time("2026-11-01T12:00:00Z")
def test_500_then_200_retries_and_reads_one_transaction() -> None:
    with HttpMocker() as http_mocker:
        http_mocker.get(
            _TRANSACTIONS_REQUEST,
            [HttpResponse(body="{}", status_code=500), _success_response()],
        )

        output = _read_transactions()

        assert not output.errors
        assert len(output.records) == 1
        http_mocker.assert_number_of_calls(_TRANSACTIONS_REQUEST, 2)


@freeze_time("2026-11-01T12:00:00Z")
def test_401_fails_once_as_config_error() -> None:
    with HttpMocker() as http_mocker:
        http_mocker.get(_TRANSACTIONS_REQUEST, HttpResponse(body="{}", status_code=401))

        output = _read_transactions(expecting_exception=True)

        assert output.errors
        assert output.errors[0].trace.error.failure_type == FailureType.config_error
        http_mocker.assert_number_of_calls(_TRANSACTIONS_REQUEST, 1)
