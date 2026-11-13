# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from pathlib import Path
from urllib.parse import urlparse

import pytest
import requests
import yaml

from airbyte_cdk.sources.declarative.models import DefaultErrorHandler as DefaultErrorHandlerModel
from airbyte_cdk.sources.declarative.models import HttpRequester
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory
from airbyte_cdk.sources.declarative.requesters.error_handlers.default_error_handler import DefaultErrorHandler
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ResponseAction


CONNECTOR_DIR = Path(__file__).resolve().parents[1]
MANIFEST_PATH = CONNECTOR_DIR / "manifest.yaml"
STREAM_NAMES = list(yaml.safe_load(MANIFEST_PATH.read_text())["definitions"]["streams"])


def _walk_dicts(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _walk_dicts(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_dicts(child)


@pytest.mark.parametrize(
    "region, host",
    [
        pytest.param("nl", "data.castoredc.com", id="netherlands"),
        pytest.param("uk", "uk.castoredc.com", id="united-kingdom"),
        pytest.param("us", "us.castoredc.com", id="united-states"),
    ],
)
def test_regional_api_and_oauth_hosts(region: str, host: str) -> None:
    manifest = yaml.safe_load((CONNECTOR_DIR / "manifest.yaml").read_text())
    metadata = yaml.safe_load((CONNECTOR_DIR / "metadata.yaml").read_text())
    requester = ModelToComponentFactory().create_component(
        model_type=HttpRequester,
        component_definition=manifest["definitions"]["base_requester"],
        config={"url_region": region, "client_id": "test-client", "client_secret": "test-secret"},
        name="test_stream",
    )

    api_url = requester.get_url_base()
    token_url = requester.authenticator.get_token_refresh_endpoint()
    assert api_url == f"https://{host}/api/"
    assert token_url == f"https://{host}/oauth/token"
    assert requester.authenticator.get_grant_type() == "client_credentials"
    for url in (api_url, token_url):
        assert urlparse(url).hostname in metadata["data"]["allowedHosts"]["hosts"]


def test_region_configuration_remains_compatible() -> None:
    manifest = yaml.safe_load((CONNECTOR_DIR / "manifest.yaml").read_text())
    region = manifest["spec"]["connection_specification"]["properties"]["url_region"]

    assert region["enum"] == ["uk", "nl", "us"]
    assert region["default"] == "uk"


def test_manifest_has_no_composite_error_handler() -> None:
    manifest = yaml.safe_load(MANIFEST_PATH.read_text())

    assert not any(node.get("type") == "CompositeErrorHandler" for node in _walk_dicts(manifest))


@pytest.mark.parametrize("stream_name", STREAM_NAMES)
def test_stream_error_handlers_retry_rate_limits(stream_name: str) -> None:
    manifest = yaml.safe_load(MANIFEST_PATH.read_text())
    error_handler_definition = manifest["definitions"]["streams"][stream_name]["retriever"]["requester"]["error_handler"]

    assert error_handler_definition["type"] == "DefaultErrorHandler"

    error_handler = ModelToComponentFactory().create_component(
        model_type=DefaultErrorHandlerModel,
        component_definition=error_handler_definition,
        config={},
    )
    assert isinstance(error_handler, DefaultErrorHandler)
    assert error_handler.max_retries == 5

    response = requests.Response()
    response.status_code = 429
    assert error_handler.interpret_response(response).response_action == ResponseAction.RATE_LIMITED
    assert error_handler.backoff_strategies[0].backoff_time(response_or_exception=response, attempt_count=1) == 5
