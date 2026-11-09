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


_CONFIG = {"api_key_2": "test_api_key", "start_date": "2024-01-01T00:00:00Z"}
_VENDORS_URL = "https://api.samanage.com/vendors.json"


def _load_manifest():
    return yaml.safe_load(MANIFEST_PATH.read_text())


_STREAMS = tuple(_load_manifest()["definitions"]["streams"].keys())


def _build_requester(stream_name):
    resolved = ManifestReferenceResolver().preprocess_manifest(_load_manifest())
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
    response.request = requests.Request("GET", _VENDORS_URL).prepare()
    return response


def test_manifest_has_no_composite_error_handler():
    assert len(_STREAMS) == 22
    assert "CompositeErrorHandler" not in MANIFEST_PATH.read_text()


@pytest.mark.parametrize("stream_name", _STREAMS)
def test_stream_references_the_shared_error_handler(stream_name):
    stream_manifest = _load_manifest()["definitions"]["streams"][stream_name]
    assert stream_manifest["retriever"]["requester"]["error_handler"] == {"$ref": "#/definitions/error_handler"}


@pytest.mark.parametrize("stream_name", _STREAMS)
def test_error_handler_is_default_error_handler(stream_name):
    assert isinstance(_build_requester(stream_name).error_handler, DefaultErrorHandler)


@pytest.mark.parametrize("stream_name", _STREAMS)
def test_429_is_rate_limited(stream_name):
    handler = _build_requester(stream_name).error_handler
    resolution = handler.interpret_response(_response(429))
    assert resolution.response_action == ResponseAction.RATE_LIMITED
    assert resolution.error_message == "Rate limits has been hit"


@pytest.mark.parametrize("stream_name", _STREAMS)
def test_max_retries_is_two(stream_name):
    assert _build_requester(stream_name).error_handler.max_retries == 2


@pytest.mark.parametrize("stream_name", _STREAMS)
def test_backoff_is_one_constant_five_second_strategy(stream_name):
    handler = _build_requester(stream_name).error_handler
    assert len(handler.backoff_strategies) == 1
    strategy = handler.backoff_strategies[0]
    assert isinstance(strategy, ConstantBackoffStrategy)
    assert strategy.backoff_time(_response(429), attempt_count=1) == 5


@pytest.mark.parametrize(
    "status_code, expected_action",
    [
        (200, ResponseAction.SUCCESS),
        (400, ResponseAction.FAIL),
        (401, ResponseAction.FAIL),
        (403, ResponseAction.FAIL),
        (404, ResponseAction.FAIL),
        (408, ResponseAction.RETRY),
        (500, ResponseAction.RETRY),
        (502, ResponseAction.RETRY),
        (503, ResponseAction.RETRY),
    ],
)
@pytest.mark.parametrize("stream_name", _STREAMS)
def test_unfiltered_status_code_parity(stream_name, status_code, expected_action):
    handler = _build_requester(stream_name).error_handler
    assert handler.interpret_response(_response(status_code)).response_action == expected_action


def test_429_read_retries_and_emits_record(monkeypatch):
    monkeypatch.setattr("time.sleep", lambda _: None)
    catalog = CatalogBuilder().with_stream("vendors", SyncMode.full_refresh).build()
    with requests_mock.Mocker() as mocker:
        mocker.get(
            _VENDORS_URL,
            [{"status_code": 429}, {"status_code": 200, "json": [{"id": 1, "name": "Vendor"}]}],
        )
        output = read(get_source(_CONFIG), _CONFIG, catalog)

    assert [record.record.data["id"] for record in output.records] == [1]
    assert len(mocker.request_history) == 2
    assert mocker.request_history[0].qs == {"page": ["1"], "per_page": ["50"]}
