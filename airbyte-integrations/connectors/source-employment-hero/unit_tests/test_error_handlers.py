# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from pathlib import Path

import pytest
import yaml
from requests import Response

from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.declarative.models.declarative_component_schema import DefaultErrorHandler as DefaultErrorHandlerModel
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory
from airbyte_cdk.sources.declarative.requesters.error_handlers.default_error_handler import DefaultErrorHandler
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ResponseAction


STREAMS = yaml.safe_load((Path(__file__).parents[1] / "manifest.yaml").read_text())["definitions"]["streams"]


@pytest.fixture(params=STREAMS, ids=STREAMS)
def error_handler(request: pytest.FixtureRequest) -> DefaultErrorHandler:
    definition = STREAMS[request.param]["retriever"]["requester"]["error_handler"]
    assert definition["type"] == "DefaultErrorHandler"
    return ModelToComponentFactory().create_component(DefaultErrorHandlerModel, definition, config={})


@pytest.mark.parametrize(
    "status_code, action, failure_type, message",
    [
        (200, ResponseAction.SUCCESS, None, None),
        (
            400,
            ResponseAction.FAIL,
            FailureType.system_error,
            "HTTP Status Code: 400. Error: Bad request. Please check your request parameters.",
        ),
        (
            401,
            ResponseAction.FAIL,
            FailureType.config_error,
            "HTTP Status Code: 401. Error: Unauthorized. Please ensure you are authenticated correctly.",
        ),
        (
            403,
            ResponseAction.FAIL,
            FailureType.config_error,
            "HTTP Status Code: 403. Error: Forbidden. You don't have permission to access this resource.",
        ),
        (
            404,
            ResponseAction.FAIL,
            FailureType.system_error,
            "HTTP Status Code: 404. Error: Not found. The requested resource was not found on the server.",
        ),
        (429, ResponseAction.RATE_LIMITED, FailureType.transient_error, "Rate limits hit"),
        (500, ResponseAction.RETRY, FailureType.transient_error, "HTTP Status Code: 500. Error: Internal server error."),
        (502, ResponseAction.RETRY, FailureType.transient_error, "HTTP Status Code: 502. Error: Bad gateway."),
        (503, ResponseAction.RETRY, FailureType.transient_error, "HTTP Status Code: 503. Error: Service unavailable."),
    ],
)
def test_response_classification(
    error_handler: DefaultErrorHandler,
    status_code: int,
    action: ResponseAction,
    failure_type: FailureType | None,
    message: str | None,
) -> None:
    response = Response()
    response.status_code = status_code
    response._content = b"{}"

    resolution = error_handler.interpret_response(response)

    assert resolution.response_action == action
    assert resolution.failure_type == failure_type
    assert resolution.error_message == message


def test_retry_limits_and_backoff(error_handler: DefaultErrorHandler) -> None:
    assert error_handler.max_retries == 3
    assert error_handler.max_time == 600
    assert error_handler.backoff_strategies is not None
    assert len(error_handler.backoff_strategies) == 1
    assert [error_handler.backoff_strategies[0].backoff_time(None, attempt) for attempt in (1, 2, 3)] == [4, 8, 16]
