# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from pathlib import Path

import pytest
import requests
import yaml

from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.declarative.models import DefaultErrorHandler as DefaultErrorHandlerModel
from airbyte_cdk.sources.declarative.parsers.manifest_reference_resolver import ManifestReferenceResolver
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory
from airbyte_cdk.sources.declarative.requesters.error_handlers.default_error_handler import DefaultErrorHandler
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ResponseAction


MANIFEST_PATH = Path(__file__).resolve().parents[1] / "manifest.yaml"
STREAM_NAMES = ("accounts", "customers", "worklogs", "workload-schemes")


@pytest.fixture(params=STREAM_NAMES)
def stream_name(request: pytest.FixtureRequest) -> str:
    return request.param


@pytest.fixture(params=("definitions", "streams"))
def handler_definition(request: pytest.FixtureRequest, stream_name: str) -> dict:
    manifest = yaml.safe_load(MANIFEST_PATH.read_text())
    if request.param == "definitions":
        stream = manifest["definitions"]["streams"][stream_name]
    else:
        stream = next(stream for stream in manifest["streams"] if stream["name"] == stream_name)
    definition = stream["retriever"]["requester"]["error_handler"]
    assert definition == {"$ref": "#/definitions/error_handler"}
    return ManifestReferenceResolver().preprocess_manifest(manifest)["definitions"]["error_handler"]


@pytest.fixture
def handler(handler_definition: dict) -> DefaultErrorHandler:
    assert handler_definition["type"] == "DefaultErrorHandler"
    return ModelToComponentFactory().create_component(
        model_type=DefaultErrorHandlerModel, component_definition=handler_definition, config={}
    )


def response(status_code: int) -> requests.Response:
    result = requests.Response()
    result.status_code = status_code
    result._content = b'{"error": "test response"}'
    result.request = requests.Request("GET", "https://api.tempo.io/4/accounts").prepare()
    return result


def test_forbidden_is_ignored(handler: DefaultErrorHandler) -> None:
    resolution = handler.interpret_response(response(403))
    assert resolution.response_action == ResponseAction.IGNORE
    assert resolution.failure_type == FailureType.config_error


@pytest.mark.parametrize(
    "status_code, action, failure_type",
    [
        (200, ResponseAction.SUCCESS, None),
        (400, ResponseAction.FAIL, FailureType.system_error),
        (401, ResponseAction.FAIL, FailureType.config_error),
        (402, ResponseAction.RETRY, FailureType.system_error),
        (404, ResponseAction.FAIL, FailureType.system_error),
        (408, ResponseAction.RETRY, FailureType.transient_error),
        (410, ResponseAction.RETRY, FailureType.system_error),
        (415, ResponseAction.RETRY, FailureType.system_error),
        (429, ResponseAction.RATE_LIMITED, FailureType.transient_error),
        (500, ResponseAction.RETRY, FailureType.transient_error),
        (501, ResponseAction.RETRY, FailureType.system_error),
        (502, ResponseAction.RETRY, FailureType.transient_error),
        (503, ResponseAction.RETRY, FailureType.transient_error),
        (504, ResponseAction.RETRY, FailureType.transient_error),
    ],
)
def test_default_status_handling(
    handler: DefaultErrorHandler, status_code: int, action: ResponseAction, failure_type: FailureType | None
) -> None:
    resolution = handler.interpret_response(response(status_code))
    assert resolution.response_action == action
    assert resolution.failure_type == failure_type


def test_default_retry_settings(handler: DefaultErrorHandler) -> None:
    assert handler.max_retries == 5
    assert handler.max_time == 600
    assert handler.backoff_strategies == []
