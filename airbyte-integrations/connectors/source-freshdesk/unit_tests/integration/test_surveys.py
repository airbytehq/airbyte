# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
import sys
from pathlib import Path
from typing import Any, Dict

import pytest
from config_builder import ConfigBuilder

from airbyte_cdk import ConfiguredAirbyteCatalog, SyncMode, YamlDeclarativeSource
from airbyte_cdk.models import FailureType
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput
from airbyte_cdk.test.entrypoint_wrapper import read as entrypoint_read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.request import ANY_QUERY_PARAMS
from airbyte_cdk.test.state_builder import StateBuilder


_DOMAIN = "a-domain.freshdesk.com"
_STREAM_ENDPOINTS = {
    "satisfaction_ratings": "surveys/satisfaction_ratings",
    "surveys": "surveys",
}
_SURVEYS_PLAN_MESSAGE = "The Surveys feature(s) is/are not supported in your plan. Please upgrade your account to use it."
_EXPECTED_PLAN_ERROR = (
    "The <stream> stream requires the Freshdesk Surveys (CSAT) feature, which is not available on your Freshdesk "
    "plan. Deselect the satisfaction_ratings and surveys streams, or upgrade your Freshdesk plan."
)
_GENERIC_403_MESSAGE = "You are not authorized to perform this action."

_SOURCE_FOLDER_PATH = Path(__file__).parent.parent.parent
_YAML_FILE_PATH = _SOURCE_FOLDER_PATH / "manifest.yaml"

sys.path.append(str(_SOURCE_FOLDER_PATH))


def _catalog(stream_name: str) -> ConfiguredAirbyteCatalog:
    return CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()


def _read(stream_name: str, expecting_exception: bool = False) -> EntrypointOutput:
    catalog = _catalog(stream_name)
    config = ConfigBuilder().domain(_DOMAIN).build()
    state = StateBuilder().build()
    source = YamlDeclarativeSource(path_to_yaml=str(_YAML_FILE_PATH), catalog=catalog, config=config, state=state)
    return entrypoint_read(source, config, catalog, state, expecting_exception)


def _request(stream_name: str) -> HttpRequest:
    endpoint = _STREAM_ENDPOINTS[stream_name]
    return HttpRequest(f"https://{_DOMAIN}/api/v2/{endpoint}", query_params=ANY_QUERY_PARAMS)


def _assert_error(output: EntrypointOutput, expected_message: str) -> None:
    assert any(
        error.trace.error.failure_type == FailureType.config_error and error.trace.error.message == expected_message
        for error in output.errors
    ), [error.trace.error for error in output.errors]


@pytest.mark.parametrize("stream_name", ("satisfaction_ratings", "surveys"))
@pytest.mark.parametrize(
    "status_code, body, expected_message",
    (
        (
            403,
            {"code": "access_denied", "message": _SURVEYS_PLAN_MESSAGE},
            _EXPECTED_PLAN_ERROR,
        ),
        (
            403,
            {"code": "access_denied", "message": _GENERIC_403_MESSAGE},
            "Freshdesk denied access to the <stream> stream. Confirm the API key belongs to a user with permission "
            "to view surveys, or deselect the <stream> stream.",
        ),
        (
            401,
            {"code": "access_denied", "message": "Unauthorized"},
            "The endpoint to access stream <stream> returned 401: Unauthorized. This is most likely due to wrong " "credentials.",
        ),
    ),
)
def test_survey_error_messages(
    stream_name: str,
    status_code: int,
    body: Dict[str, Any],
    expected_message: str,
) -> None:
    request = _request(stream_name)
    with HttpMocker() as http_mocker:
        http_mocker.get(request, HttpResponse(json.dumps(body), status_code))

        output = _read(stream_name, expecting_exception=True)
        http_mocker.assert_number_of_calls(request, 1)

    _assert_error(output, expected_message.replace("<stream>", stream_name))


@pytest.mark.parametrize("stream_name", ("satisfaction_ratings", "surveys"))
def test_rate_limit_retries_using_retry_after(stream_name: str) -> None:
    request = _request(stream_name)
    with HttpMocker() as http_mocker:
        http_mocker.get(
            request,
            [
                HttpResponse("[]", 429, headers={"Retry-After": "0"}),
                HttpResponse("[]", 200),
            ],
        )

        output = _read(stream_name)
        http_mocker.assert_number_of_calls(request, 2)

    assert not output.errors
    assert not output.records
