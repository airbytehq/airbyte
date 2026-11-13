# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest
import requests
import requests_mock
import yaml
from _helpers import _MANIFEST_PATH, get_source

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


_STREAMS = (
    "customers",
    "locations",
    "shifts",
    "team_members",
    "team_member_wages",
    "items",
    "categories",
    "discounts",
    "taxes",
    "modifier_list",
    "refunds",
    "inventory",
    "payments",
    "orders",
    "bank_accounts",
    "cash_drawers",
    "loyalty",
)
_CONFIG = {
    "credentials": {
        "auth_type": "API Key",
        "api_key": "test_api_key",
    },
    "is_sandbox": False,
    "start_date": "2021-01-01",
    "include_deleted_objects": False,
}
_LOCATIONS_URL = "https://connect.squareup.com/v2/locations"
_AUTHORIZATION_ERROR = "Failed to authorize request. Please update your access token to continue using the source."


def _load_manifest():
    return yaml.safe_load(_MANIFEST_PATH.read_text())


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
    response.request = requests.Request("GET", _LOCATIONS_URL).prepare()
    return response


@pytest.mark.parametrize("stream_name", _STREAMS)
def test_streams_reference_the_shared_error_handler(stream_name):
    manifest_text = _MANIFEST_PATH.read_text()
    assert "Composite" + "ErrorHandler" not in manifest_text
    stream_manifest = _load_manifest()["definitions"]["streams"][stream_name]
    assert stream_manifest["retriever"]["requester"]["error_handler"] == {"$ref": "#/definitions/error_handler"}


@pytest.mark.parametrize("stream_name", _STREAMS)
def test_error_handler_is_default_error_handler(stream_name):
    assert isinstance(_build_requester(stream_name).error_handler, DefaultErrorHandler)


@pytest.mark.parametrize(
    "status_code, expected_action",
    [
        (403, ResponseAction.IGNORE),
        (404, ResponseAction.IGNORE),
        (429, ResponseAction.RETRY),
    ],
)
@pytest.mark.parametrize("stream_name", _STREAMS)
def test_filtered_status_codes_preserve_actions(stream_name, status_code, expected_action):
    handler = _build_requester(stream_name).error_handler
    assert handler.interpret_response(_response(status_code)).response_action == expected_action


@pytest.mark.parametrize("stream_name", _STREAMS)
def test_401_fails_with_authorization_message(stream_name):
    result = _build_requester(stream_name).error_handler.interpret_response(_response(401))
    assert result.response_action == ResponseAction.FAIL
    assert result.error_message == _AUTHORIZATION_ERROR


@pytest.mark.parametrize("stream_name", _STREAMS)
def test_max_retries_is_five(stream_name):
    assert _build_requester(stream_name).error_handler.max_retries == 5


@pytest.mark.parametrize("stream_name", _STREAMS)
def test_backoff_is_one_constant_thirty_second_strategy(stream_name):
    handler = _build_requester(stream_name).error_handler
    assert len(handler.backoff_strategies) == 1
    strategy = handler.backoff_strategies[0]
    assert isinstance(strategy, ConstantBackoffStrategy)
    assert strategy.backoff_time(_response(429), attempt_count=1) == 30


@pytest.mark.parametrize(
    "status_code, expected_action",
    [
        (200, ResponseAction.SUCCESS),
        (400, ResponseAction.FAIL),
        (500, ResponseAction.RETRY),
        (502, ResponseAction.RETRY),
        (503, ResponseAction.RETRY),
    ],
)
@pytest.mark.parametrize("stream_name", _STREAMS)
def test_unfiltered_status_code_parity(stream_name, status_code, expected_action):
    handler = _build_requester(stream_name).error_handler
    assert handler.interpret_response(_response(status_code)).response_action == expected_action


def test_locations_404_is_ignored_without_records_or_error_trace():
    catalog = CatalogBuilder().with_stream("locations", SyncMode.full_refresh).build()
    with requests_mock.Mocker() as mocker:
        mocker.get(_LOCATIONS_URL, status_code=404)
        output = read(get_source(_CONFIG), _CONFIG, catalog)

    assert output.records == []
    assert output.errors == []
