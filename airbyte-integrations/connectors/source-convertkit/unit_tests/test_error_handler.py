# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from pathlib import Path

import pytest
import requests
import yaml

from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.declarative.models.declarative_component_schema import DefaultErrorHandler as DefaultErrorHandlerModel
from airbyte_cdk.sources.declarative.parsers.manifest_reference_resolver import ManifestReferenceResolver
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory
from airbyte_cdk.sources.declarative.requesters.error_handlers.default_error_handler import DefaultErrorHandler
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ResponseAction


OAUTH_REQUIRED_MESSAGE = (
    "The purchases endpoint requires the use of OAuth authentication and isn't available when using API Key auth. "
    "Please switch to OAuth or disable this stream."
)


@pytest.fixture
def purchases_error_handler() -> DefaultErrorHandler:
    manifest_path = Path(__file__).parent.parent / "manifest.yaml"
    manifest = ManifestReferenceResolver().preprocess_manifest(yaml.safe_load(manifest_path.read_text()))
    definition = manifest["definitions"]["streams"]["purchases"]["retriever"]["requester"]["error_handler"]
    return ModelToComponentFactory().create_component(DefaultErrorHandlerModel, definition, config={})


def test_purchases_uses_single_default_handler(purchases_error_handler: DefaultErrorHandler) -> None:
    assert isinstance(purchases_error_handler, DefaultErrorHandler)
    assert purchases_error_handler.max_retries == 5
    assert purchases_error_handler.max_time == 600
    assert not purchases_error_handler.backoff_strategies


@pytest.mark.parametrize(
    "status_code, message, action, failure_type, custom_message",
    [
        (401, "OAuth authentication required", ResponseAction.FAIL, FailureType.config_error, True),
        (401, "Invalid API key", ResponseAction.FAIL, FailureType.config_error, True),
        (403, "OAuth authentication required", ResponseAction.FAIL, FailureType.config_error, True),
        (403, "Forbidden", ResponseAction.FAIL, FailureType.config_error, False),
        (429, "Rate limit exceeded", ResponseAction.RATE_LIMITED, FailureType.transient_error, False),
        (500, "Internal server error", ResponseAction.RETRY, FailureType.transient_error, False),
        (200, "", ResponseAction.SUCCESS, None, False),
    ],
)
def test_purchases_response_classification(
    purchases_error_handler: DefaultErrorHandler,
    status_code: int,
    message: str,
    action: ResponseAction,
    failure_type: FailureType | None,
    custom_message: bool,
) -> None:
    response = requests.Response()
    response.status_code = status_code
    response._content = json.dumps({"error": message}).encode()
    response.headers["Content-Type"] = "application/json"

    resolution = purchases_error_handler.interpret_response(response)

    assert resolution.response_action == action
    assert resolution.failure_type == failure_type
    if custom_message:
        assert resolution.error_message == OAUTH_REQUIRED_MESSAGE
    else:
        assert resolution.error_message != OAUTH_REQUIRED_MESSAGE
