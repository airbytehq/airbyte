# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest
import requests
import requests_mock
import yaml
from conftest import MANIFEST_PATH, get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.models.declarative_component_schema import HttpRequester as HttpRequesterModel
from airbyte_cdk.sources.declarative.parsers.manifest_component_transformer import ManifestComponentTransformer
from airbyte_cdk.sources.declarative.parsers.manifest_reference_resolver import ManifestReferenceResolver
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory
from airbyte_cdk.sources.declarative.requesters.error_handlers.backoff_strategies.constant_backoff_strategy import (
    ConstantBackoffStrategy,
)
from airbyte_cdk.sources.declarative.requesters.error_handlers.default_error_handler import DefaultErrorHandler
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ResponseAction
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


_STREAMS = ("accounts", "leads", "visits")
_CONFIG = {"api_token": "test_api_token", "start_date": "2024-01-01T00:00:00Z"}
_ACCOUNTS_URL = "https://api.leadfeeder.com/accounts"


def _load_manifest():
    return yaml.safe_load(MANIFEST_PATH.read_text())


def _build_requester(stream_name):
    manifest = _load_manifest()
    resolved = ManifestReferenceResolver().preprocess_manifest(manifest)
    resolved = ManifestComponentTransformer().propagate_types_and_parameters("", resolved, {})
    requester_model = resolved["definitions"]["streams"][stream_name]["retriever"]["requester"]
    return ModelToComponentFactory().create_component(
        HttpRequesterModel,
        requester_model,
        _CONFIG,
        name=stream_name,
        decoder=None,
    )


def _response(status_code):
    response = requests.Response()
    response.status_code = status_code
    response._content = b"{}"
    response.request = requests.Request("GET", _ACCOUNTS_URL).prepare()
    return response


@pytest.mark.parametrize("stream_name", _STREAMS)
def test_streams_reference_the_shared_error_handler(stream_name):
    manifest_text = MANIFEST_PATH.read_text()
    assert "CompositeErrorHandler" not in manifest_text
    stream_manifest = _load_manifest()["definitions"]["streams"][stream_name]
    assert stream_manifest["retriever"]["requester"]["error_handler"] == {"$ref": "#/definitions/error_handler"}


@pytest.mark.parametrize("stream_name", _STREAMS)
def test_error_handler_is_default_error_handler(stream_name):
    assert isinstance(_build_requester(stream_name).error_handler, DefaultErrorHandler)


@pytest.mark.parametrize("stream_name", _STREAMS)
def test_402_is_ignored(stream_name):
    handler = _build_requester(stream_name).error_handler
    assert handler.interpret_response(_response(402)).response_action == ResponseAction.IGNORE


@pytest.mark.parametrize("stream_name", _STREAMS)
def test_429_is_retried(stream_name):
    handler = _build_requester(stream_name).error_handler
    assert handler.interpret_response(_response(429)).response_action == ResponseAction.RETRY


@pytest.mark.parametrize("stream_name", _STREAMS)
def test_max_retries_is_five(stream_name):
    assert _build_requester(stream_name).error_handler.max_retries == 5


@pytest.mark.parametrize("stream_name", _STREAMS)
def test_backoff_is_one_constant_sixty_second_strategy(stream_name):
    handler = _build_requester(stream_name).error_handler
    assert len(handler.backoff_strategies) == 1
    strategy = handler.backoff_strategies[0]
    assert isinstance(strategy, ConstantBackoffStrategy)
    assert strategy.backoff_time(_response(429), attempt_count=1) == 60


@pytest.mark.parametrize(
    "status_code, expected_action",
    [
        (400, ResponseAction.FAIL),
        (401, ResponseAction.FAIL),
        (403, ResponseAction.FAIL),
        (404, ResponseAction.FAIL),
        (408, ResponseAction.RETRY),
        (200, ResponseAction.SUCCESS),
        (500, ResponseAction.RETRY),
        (502, ResponseAction.RETRY),
        (503, ResponseAction.RETRY),
    ],
)
@pytest.mark.parametrize("stream_name", _STREAMS)
def test_unfiltered_status_code_parity(stream_name, status_code, expected_action):
    handler = _build_requester(stream_name).error_handler
    assert handler.interpret_response(_response(status_code)).response_action == expected_action


def _read_accounts():
    catalog = CatalogBuilder().with_stream("accounts", SyncMode.full_refresh).build()
    return read(get_source(_CONFIG), _CONFIG, catalog)


def test_402_read_is_ignored_without_records_or_error_trace():
    with requests_mock.Mocker() as mocker:
        mocker.get(_ACCOUNTS_URL, status_code=402)
        output = _read_accounts()

    assert output.records == []
    assert output.errors == []


def test_429_read_retries_and_emits_record(monkeypatch):
    monkeypatch.setattr("time.sleep", lambda _: None)
    response = {"data": [{"id": "1", "type": "accounts", "attributes": {}}]}
    with requests_mock.Mocker() as mocker:
        mocker.get(
            _ACCOUNTS_URL,
            [{"status_code": 429}, {"status_code": 200, "json": response}],
        )
        output = _read_accounts()

    assert len(output.records) == 1
    assert output.records[0].record.data["id"] == "1"
    assert len(mocker.request_history) == 2
