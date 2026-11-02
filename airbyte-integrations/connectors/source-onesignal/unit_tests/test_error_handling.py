import json

import pytest
import requests
import yaml
from conftest import _YAML_FILE_PATH, get_source

from airbyte_cdk.models import AirbyteStreamStatus, SyncMode
from airbyte_cdk.sources.declarative.models.declarative_component_schema import DefaultErrorHandler as DefaultErrorHandlerModel
from airbyte_cdk.sources.declarative.parsers.manifest_reference_resolver import ManifestReferenceResolver
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory
from airbyte_cdk.sources.declarative.requesters.error_handlers.default_error_handler import DefaultErrorHandler
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ResponseAction
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder


CONFIG = {
    "user_auth_key": "test-user-auth-key",
    "applications": [{"app_id": "test-app-id", "app_api_key": "test-app-api-key", "app_name": "Test App"}],
    "start_date": "2024-01-01T00:00:00Z",
    "outcome_names": "os__session_duration.count",
}
BASE_URL = "https://onesignal.com/api/v1"
OUTCOMES_REQUEST = HttpRequest(
    url=f"{BASE_URL}/apps/test-app-id/outcomes",
    query_params={
        "app_id": "test-app-id",
        "outcome_names": "os__session_duration.count",
        "limit": "5",
    },
)


def _resolved_manifest() -> dict:
    return ManifestReferenceResolver().preprocess_manifest(yaml.safe_load(_YAML_FILE_PATH.read_text()))


def _handler(stream_name: str) -> DefaultErrorHandler:
    manifest = _resolved_manifest()
    definition = manifest["definitions"]["streams"][stream_name]["retriever"]["requester"]["error_handler"]
    return ModelToComponentFactory().create_component(DefaultErrorHandlerModel, definition, config=CONFIG)


def _response(status_code: int) -> requests.Response:
    response = requests.Response()
    response.status_code = status_code
    response.headers["Content-Type"] = "application/json"
    response._content = b'{"errors":["test error"]}'
    response.request = requests.Request("GET", f"{BASE_URL}/example").prepare()
    response.url = response.request.url
    return response


def _read_stream(stream_name: str) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    state = StateBuilder().build()
    return read(get_source(CONFIG, state), CONFIG, catalog, state=state)


def test_manifest_has_no_composite_error_handler() -> None:
    composite_handlers = []

    def walk(node):
        if isinstance(node, dict):
            handler_type = node.get("type", "")
            if isinstance(handler_type, str) and handler_type.startswith("Composite") and handler_type.endswith("ErrorHandler"):
                composite_handlers.append(node)
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(_resolved_manifest())

    assert not composite_handlers


@pytest.mark.parametrize(
    "stream_name",
    [
        pytest.param("apps", id="apps"),
        pytest.param("devices", id="devices"),
        pytest.param("notifications", id="notifications"),
        pytest.param("outcomes", id="outcomes"),
    ],
)
def test_handlers_classify_responses(stream_name: str) -> None:
    handler = _handler(stream_name)

    assert type(handler) is DefaultErrorHandler
    assert handler.max_retries == 3

    rate_limited = handler.interpret_response(_response(429))
    assert rate_limited.response_action == ResponseAction.RATE_LIMITED
    assert rate_limited.error_message == "Rate limits hit"
    assert handler.interpret_response(_response(500)).response_action == ResponseAction.RETRY
    assert handler.interpret_response(_response(401)).response_action == ResponseAction.FAIL
    assert handler.backoff_time(_response(500), attempt_count=2) == 8.0


@pytest.mark.parametrize(
    "stream_name,expected_action",
    [
        pytest.param("outcomes", ResponseAction.SUCCESS, id="outcomes-400-is-success"),
        pytest.param("apps", ResponseAction.FAIL, id="apps-400-fails"),
        pytest.param("devices", ResponseAction.FAIL, id="devices-400-fails"),
        pytest.param("notifications", ResponseAction.FAIL, id="notifications-400-fails"),
    ],
)
def test_400_filter_is_scoped_to_outcomes(stream_name: str, expected_action: ResponseAction) -> None:
    assert _handler(stream_name).interpret_response(_response(400)).response_action == expected_action


def test_outcomes_400_completes_without_records_or_error_traces() -> None:
    with HttpMocker() as http_mocker:
        http_mocker.get(
            OUTCOMES_REQUEST,
            HttpResponse(
                body='{"errors":["Add .sum or .count to every requested outcome id"]}',
                status_code=400,
            ),
        )

        output = _read_stream("outcomes")

    assert output.records == []
    assert output.errors == []
    assert output.get_stream_statuses("outcomes")[-1] == AirbyteStreamStatus.COMPLETE
    http_mocker.assert_number_of_calls(OUTCOMES_REQUEST, 1)


def test_outcomes_429_retries_and_emits_record() -> None:
    with HttpMocker() as http_mocker:
        http_mocker.get(
            OUTCOMES_REQUEST,
            [
                HttpResponse(body='{"errors":["rate limited"]}', status_code=429),
                HttpResponse(body=json.dumps({"outcomes": [{"id": "outcome-1", "value": 1, "aggregation": "count"}]})),
            ],
        )

        output = _read_stream("outcomes")

    assert output.errors == []
    assert [record.record.data["id"] for record in output.records] == ["outcome-1"]
    http_mocker.assert_number_of_calls(OUTCOMES_REQUEST, 2)


def test_apps_429_retries_and_emits_record() -> None:
    apps_request = HttpRequest(url=f"{BASE_URL}/apps")
    with HttpMocker() as http_mocker:
        http_mocker.get(
            apps_request,
            [
                HttpResponse(body='{"errors":["rate limited"]}', status_code=429),
                HttpResponse(body=json.dumps([{"id": "app-1", "name": "Test App"}])),
            ],
        )

        output = _read_stream("apps")

    assert output.errors == []
    assert [record.record.data["id"] for record in output.records] == ["app-1"]
    http_mocker.assert_number_of_calls(apps_request, 2)
