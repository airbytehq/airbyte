import json
from pathlib import Path

import pytest
import requests
import yaml
from _helpers import CONFIG, json_response, read_stream, request
from conftest import _YAML_FILE_PATH

from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.declarative.models.declarative_component_schema import (
    DefaultErrorHandler as DefaultErrorHandlerModel,
)
from airbyte_cdk.sources.declarative.parsers.manifest_reference_resolver import ManifestReferenceResolver
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ResponseAction
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse


STREAMS = (
    "teams",
    "groups",
    "group_collection_access",
    "group_members",
    "members",
    "collections",
    "folders",
    "folder_items",
    "folders_parent",
    "search_cardmgr",
    "team_analytics",
    "tag_categories",
)
RATE_LIMIT_FILTER = {
    "type": "HttpResponseFilter",
    "action": "RETRY",
    "http_codes": [429],
    "error_message": "Rate limits hit...Retrying",
}
IGNORE_BAD_REQUEST_FILTERS = [
    {
        "type": "HttpResponseFilter",
        "action": "RATE_LIMITED",
        "http_codes": [429],
        "error_message": "Rate limits hit...Retrying",
    },
    {
        "type": "HttpResponseFilter",
        "action": "IGNORE",
        "http_codes": [400],
    },
]
RATE_LIMIT_BACKOFF = [{"type": "ExponentialBackoffStrategy", "factor": 2}]


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    monkeypatch.setattr("time.sleep", lambda *_args, **_kwargs: None)


@pytest.fixture
def resolved_manifest():
    return ManifestReferenceResolver().preprocess_manifest(yaml.safe_load(Path(_YAML_FILE_PATH).read_text()))


def _stream_definition(manifest, stream_name):
    return next(stream for stream in manifest["streams"] if stream["name"] == stream_name)


def _stream_error_handler(manifest, stream_name):
    return _stream_definition(manifest, stream_name)["retriever"]["requester"]["error_handler"]


def _build_handler(definition):
    return ModelToComponentFactory().create_component(DefaultErrorHandlerModel, definition, config=CONFIG)


def _response(status_code):
    response = requests.Response()
    response.status_code = status_code
    response.url = "https://api.getguru.com/api/v1/teams"
    response.request = requests.Request("GET", response.url).prepare()
    response.headers["Content-Type"] = "application/json"
    response._content = json.dumps({"error": "Guru API error"}).encode()
    return response


def test_manifest_has_no_composite_error_handler(resolved_manifest):
    composite_handlers = []

    def walk(node):
        if isinstance(node, dict):
            if node.get("type") == "Composite" + "ErrorHandler":
                composite_handlers.append(node)
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(resolved_manifest)

    assert not composite_handlers


@pytest.mark.parametrize(
    "stream_name, expected_filters",
    [pytest.param(stream, [RATE_LIMIT_FILTER], id=stream) for stream in STREAMS if stream not in {"team_analytics", "tag_categories"}]
    + [pytest.param(stream, IGNORE_BAD_REQUEST_FILTERS, id=stream) for stream in ("team_analytics", "tag_categories")],
)
def test_streams_use_expected_default_error_handler(resolved_manifest, stream_name, expected_filters):
    handler = _stream_error_handler(resolved_manifest, stream_name)

    assert handler["type"] == "DefaultErrorHandler"
    assert handler["max_retries"] == 3
    assert handler["backoff_strategies"] == RATE_LIMIT_BACKOFF
    assert handler["response_filters"] == expected_filters


@pytest.mark.parametrize(
    "handler_stream, status_code, expected_action, expected_failure_type, expected_message",
    [
        pytest.param("teams", 200, ResponseAction.SUCCESS, None, None, id="retry-handler-success"),
        pytest.param("teams", 400, ResponseAction.FAIL, FailureType.system_error, None, id="retry-handler-400"),
        pytest.param("teams", 401, ResponseAction.FAIL, FailureType.config_error, None, id="retry-handler-401"),
        pytest.param("teams", 403, ResponseAction.FAIL, FailureType.config_error, None, id="retry-handler-403"),
        pytest.param("teams", 404, ResponseAction.FAIL, None, None, id="retry-handler-404"),
        pytest.param(
            "teams",
            429,
            ResponseAction.RETRY,
            None,
            "Rate limits hit...Retrying",
            id="retry-handler-429",
        ),
        pytest.param("teams", 500, ResponseAction.RETRY, None, None, id="retry-handler-500"),
        pytest.param("teams", 503, ResponseAction.RETRY, None, None, id="retry-handler-503"),
        pytest.param(
            "team_analytics",
            200,
            ResponseAction.SUCCESS,
            None,
            None,
            id="ignore-handler-success",
        ),
        pytest.param(
            "team_analytics",
            400,
            ResponseAction.IGNORE,
            None,
            None,
            id="ignore-handler-400",
        ),
        pytest.param(
            "team_analytics",
            401,
            ResponseAction.FAIL,
            FailureType.config_error,
            None,
            id="ignore-handler-401",
        ),
        pytest.param(
            "team_analytics",
            403,
            ResponseAction.FAIL,
            FailureType.config_error,
            None,
            id="ignore-handler-403",
        ),
        pytest.param(
            "team_analytics",
            404,
            ResponseAction.FAIL,
            None,
            None,
            id="ignore-handler-404",
        ),
        pytest.param(
            "team_analytics",
            429,
            ResponseAction.RATE_LIMITED,
            None,
            "Rate limits hit...Retrying",
            id="ignore-handler-429",
        ),
        pytest.param(
            "team_analytics",
            500,
            ResponseAction.RETRY,
            None,
            None,
            id="ignore-handler-500",
        ),
        pytest.param(
            "team_analytics",
            503,
            ResponseAction.RETRY,
            None,
            None,
            id="ignore-handler-503",
        ),
    ],
)
def test_handler_classifies_responses(
    resolved_manifest, handler_stream, status_code, expected_action, expected_failure_type, expected_message
):
    resolution = _build_handler(_stream_error_handler(resolved_manifest, handler_stream)).interpret_response(_response(status_code))

    assert resolution.response_action == expected_action
    if expected_failure_type:
        assert resolution.failure_type == expected_failure_type
    if expected_message:
        assert resolution.error_message == expected_message


def test_teams_retries_429_then_emits_record():
    teams_request = request("teams")
    with HttpMocker() as http_mocker:
        http_mocker.get(
            teams_request,
            [
                HttpResponse(body='{"error":"rate limited"}', status_code=429),
                json_response([{"id": "team-1", "dateCreated": "2024-01-02T00:00:00Z"}]),
            ],
        )

        output = read_stream("teams")

        assert not output.errors
        assert [record.record.data["id"] for record in output.records] == ["team-1"]
        http_mocker.assert_number_of_calls(teams_request, 2)


def test_tag_categories_ignores_bad_request():
    teams_request = request("teams")
    tag_categories_request = request("teams/team-1/tagcategories")
    with HttpMocker() as http_mocker:
        http_mocker.get(teams_request, json_response([{"id": "team-1", "dateCreated": "2024-01-02T00:00:00Z"}]))
        http_mocker.get(tag_categories_request, HttpResponse(body='{"error":"bad request"}', status_code=400))

        output = read_stream("tag_categories")

        assert not output.errors
        assert not [record for record in output.records if record.stream.name == "tag_categories"]
        http_mocker.assert_number_of_calls(teams_request, 1)
        http_mocker.assert_number_of_calls(tag_categories_request, 1)


def test_teams_401_is_config_error():
    teams_request = request("teams")
    with HttpMocker() as http_mocker:
        http_mocker.get(teams_request, HttpResponse(body='{"error":"unauthorized"}', status_code=401))

        output = read_stream("teams", expecting_exception=True)

        assert output.errors
        assert output.errors[0].trace.error.failure_type == FailureType.config_error
        http_mocker.assert_number_of_calls(teams_request, 1)
