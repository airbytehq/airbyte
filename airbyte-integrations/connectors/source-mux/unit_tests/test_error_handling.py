# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from pathlib import Path

import pytest
import requests
import yaml

from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.declarative.models import declarative_component_schema
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory
from airbyte_cdk.sources.declarative.requesters.error_handlers import DefaultErrorHandler
from airbyte_cdk.sources.declarative.requesters.error_handlers.backoff_strategies import ExponentialBackoffStrategy
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ResponseAction


@pytest.fixture(
    params=[
        "video_assets",
        "video_live-streams",
        "video_playbacks",
        "system_signin-keys",
        "video_playback-restrictions",
        "video_transcription-vocabularies",
        "video_uploads",
        "video_signing-keys",
    ]
)
def error_handler(request: pytest.FixtureRequest) -> DefaultErrorHandler:
    manifest = yaml.safe_load((Path(__file__).parents[1] / "manifest.yaml").read_text())
    definition = manifest["definitions"]["streams"][request.param]["retriever"]["requester"]["error_handler"]
    model = getattr(declarative_component_schema, definition["type"])
    return ModelToComponentFactory().create_component(model, definition, config={})


def test_single_error_handler_preserves_retry_policy(error_handler: DefaultErrorHandler) -> None:
    assert isinstance(error_handler, DefaultErrorHandler)
    assert error_handler.max_retries == 3
    assert error_handler.max_time == 600
    assert error_handler.backoff_strategies is not None
    assert len(error_handler.backoff_strategies) == 1
    strategy = error_handler.backoff_strategies[0]
    assert isinstance(strategy, ExponentialBackoffStrategy)
    assert [strategy.backoff_time(None, attempt_count=attempt) for attempt in range(3)] == [2, 4, 8]


@pytest.mark.parametrize(
    "status_code,action,failure_type",
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
def test_error_handler_classifies_responses(
    error_handler: DefaultErrorHandler, status_code: int, action: ResponseAction, failure_type: FailureType | None
) -> None:
    response = requests.Response()
    response.status_code = status_code
    response.url = "https://api.mux.com/test"
    response.request = requests.Request("GET", response.url).prepare()
    response._content = b"{}"

    resolution = error_handler.interpret_response(response)

    assert resolution.response_action == action
    assert resolution.failure_type == failure_type
    if status_code == 429:
        assert resolution.error_message == "Rate limits hit"
