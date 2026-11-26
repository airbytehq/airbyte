#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
import requests
from source_webflow.auth import WebflowTokenAuthenticator
from source_webflow.source import CollectionContents, SourceWebflow, WebflowStream
from source_webflow.webflow_to_airbyte_mapping import WebflowToAirbyteMapping

from airbyte_cdk.sources.streams.http.error_handlers import ResponseAction


@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(WebflowStream, "path", "v0/example_endpoint")
    mocker.patch.object(WebflowStream, "primary_key", "test_primary_key")
    mocker.patch.object(WebflowStream, "__abstractmethods__", set())


def test_request_params_of_collection_items(patch_base_class):
    stream = CollectionContents()
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": {"offset": 1}}
    expected_params = {"limit": 100, "offset": 1}
    assert stream.request_params(**inputs) == expected_params


def test_next_page_token_of_collection_items(patch_base_class):
    stream = CollectionContents()
    response_data = {"items": [{"item1_key": "item1_val"}], "count": 10, "offset": 100}
    inputs = {"response": MagicMock(json=lambda: response_data)}
    expected_token = {"offset": 110}
    assert stream.next_page_token(**inputs) == expected_token


def test_parse_response_of_collection_items(patch_base_class):
    stream = CollectionContents()
    mock_record = {"item1_key": "item1_val"}
    response_data = {"items": [mock_record]}
    inputs = {"response": MagicMock(json=lambda: response_data)}
    parsed_item = next(stream.parse_response(**inputs))
    assert parsed_item == mock_record


def test_generate_streams(patch_base_class):
    SourceWebflow._get_collection_name_to_id_dict = MagicMock(return_value={"name-1": "id-1", "name-2": "id-2"})
    source = SourceWebflow()
    config_mock = MagicMock()
    streams = source.generate_streams(config_mock, "fake site id")
    assert len(list(streams)) == 2


def test_http_method(patch_base_class):
    stream = WebflowStream()
    expected_method = "GET"
    assert stream.http_method == expected_method


def test_get_json_schema_uses_stream_authenticator(requests_mock):
    authenticator = WebflowTokenAuthenticator(token="test-token", accept_version="1.0.0")
    stream = CollectionContents(
        authenticator=authenticator,
        site_id="s",
        collection_id="c1",
        collection_name="Blog Posts",
    )
    requests_mock.get(
        "https://api.webflow.com/collections/c1",
        json={"fields": [{"slug": "name", "type": "PlainText"}, {"slug": "views", "type": "Number"}]},
    )

    schema = stream.get_json_schema()

    assert schema["properties"]["name"] == WebflowToAirbyteMapping.webflow_to_airbyte_mapping["PlainText"]
    assert schema["properties"]["views"] == WebflowToAirbyteMapping.webflow_to_airbyte_mapping["Number"]
    assert {"_id", "_cid", "_locale"}.issubset(schema["properties"])
    assert requests_mock.last_request.headers["Authorization"] == "Bearer test-token"
    assert requests_mock.last_request.headers["accept-version"] == "1.0.0"


def test_authenticator_property_returns_webflow_authenticator():
    authenticator = WebflowTokenAuthenticator(token="test-token", accept_version="1.0.0")
    stream = CollectionContents(
        authenticator=authenticator,
        site_id="s",
        collection_id="c1",
        collection_name="Blog Posts",
    )

    assert stream.authenticator is authenticator


@pytest.mark.parametrize(
    ("http_status", "response_action"),
    [
        (HTTPStatus.OK, ResponseAction.SUCCESS),
        (HTTPStatus.BAD_REQUEST, ResponseAction.FAIL),
        (HTTPStatus.TOO_MANY_REQUESTS, ResponseAction.RATE_LIMITED),
        (HTTPStatus.INTERNAL_SERVER_ERROR, ResponseAction.RETRY),
    ],
)
def test_default_error_handler_action(patch_base_class, http_status, response_action):
    response = requests.Response()
    response.status_code = http_status
    stream = WebflowStream()
    resolution = stream._http_client._error_handler.interpret_response(response)
    assert resolution.response_action == response_action


def test_default_backoff_strategy(patch_base_class):
    stream = WebflowStream()
    strategy = stream._http_client._backoff_strategies[0]
    assert strategy.backoff_time(None, attempt_count=1) is None
