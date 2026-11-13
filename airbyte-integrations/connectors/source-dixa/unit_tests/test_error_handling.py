# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from pathlib import Path

import pytest
import requests
import yaml

from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.declarative.models.declarative_component_schema import HttpRequester as HttpRequesterModel
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory
from airbyte_cdk.sources.declarative.requesters.error_handlers.default_error_handler import DefaultErrorHandler
from airbyte_cdk.sources.streams.http.error_handlers import ErrorHandler
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ResponseAction


@pytest.fixture
def error_handler() -> ErrorHandler:
    manifest_dir = Path("/airbyte/integration_code/source_declarative_manifest")
    if not manifest_dir.exists():
        manifest_dir = Path(__file__).parent.parent
    manifest = yaml.safe_load((manifest_dir / "manifest.yaml").read_text())
    requester = ModelToComponentFactory().create_component(
        model_type=HttpRequesterModel,
        component_definition=manifest["streams"][0]["retriever"]["requester"],
        config={"api_token": "test-token"},
        name="conversation_export",
    )
    return requester.error_handler


def test_conversation_export_uses_default_handler_directly(error_handler: ErrorHandler) -> None:
    assert isinstance(error_handler, DefaultErrorHandler)


@pytest.mark.parametrize(
    "status_code, expected_action, expected_failure_type",
    [
        (200, ResponseAction.SUCCESS, None),
        (204, ResponseAction.SUCCESS, None),
        (400, ResponseAction.FAIL, FailureType.system_error),
        (401, ResponseAction.FAIL, FailureType.config_error),
        (403, ResponseAction.FAIL, FailureType.config_error),
        (404, ResponseAction.FAIL, FailureType.system_error),
        (408, ResponseAction.RETRY, FailureType.transient_error),
        (429, ResponseAction.RATE_LIMITED, FailureType.transient_error),
        (500, ResponseAction.RETRY, FailureType.transient_error),
        (502, ResponseAction.RETRY, FailureType.transient_error),
        (503, ResponseAction.RETRY, FailureType.transient_error),
        (504, ResponseAction.RETRY, FailureType.transient_error),
    ],
)
def test_conversation_export_response_classification(
    error_handler: ErrorHandler, status_code: int, expected_action: ResponseAction, expected_failure_type: FailureType | None
) -> None:
    response = requests.Response()
    response.status_code = status_code

    resolution = error_handler.interpret_response(response)

    assert resolution.response_action == expected_action
    assert resolution.failure_type == expected_failure_type


def test_conversation_export_connection_timeout_is_retried(error_handler: ErrorHandler) -> None:
    resolution = error_handler.interpret_response(requests.exceptions.Timeout())

    assert resolution.response_action == ResponseAction.RETRY
    assert resolution.failure_type == FailureType.system_error


@pytest.mark.parametrize("attempt_count", [1, 2, 5])
def test_conversation_export_retry_policy(error_handler: ErrorHandler, attempt_count: int) -> None:
    response = requests.Response()
    response.status_code = 429

    assert error_handler.max_retries == 5
    assert error_handler.max_time == 600
    assert isinstance(error_handler, DefaultErrorHandler)
    assert error_handler.backoff_strategies is not None
    assert len(error_handler.backoff_strategies) == 1
    assert error_handler.backoff_strategies[0].backoff_time(response, attempt_count) == 60
