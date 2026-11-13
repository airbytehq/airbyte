# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from typing import Any

import pytest
import requests
import requests_mock as requests_mock_lib
import yaml
from conftest import _YAML_FILE_PATH, get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.models.declarative_component_schema import DefaultErrorHandler as DefaultErrorHandlerModel
from airbyte_cdk.sources.declarative.parsers.manifest_component_transformer import ManifestComponentTransformer
from airbyte_cdk.sources.declarative.parsers.manifest_reference_resolver import ManifestReferenceResolver
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory
from airbyte_cdk.sources.declarative.requesters.error_handlers.backoff_strategies import WaitTimeFromHeaderBackoffStrategy
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ResponseAction
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read


_HANDLER_LOCATIONS = [
    pytest.param("page_components", "retriever.requester.error_handler", 3, id="page_components"),
    pytest.param("incidents", "retriever.requester.error_handler", 3, id="incidents"),
    pytest.param("incident_updates", "retriever.requester.error_handler", 3, id="incident_updates"),
    pytest.param(
        "incident_updates",
        "retriever.partition_router.parent_stream_configs.0.stream.retriever.requester.error_handler",
        5,
        id="incident_updates_parent",
    ),
    pytest.param("maintenances", "retriever.requester.error_handler", 3, id="maintenances"),
    pytest.param("maintenance_updates", "retriever.requester.error_handler", 3, id="maintenance_updates"),
    pytest.param(
        "maintenance_updates",
        "retriever.partition_router.parent_stream_configs.0.stream.retriever.requester.error_handler",
        5,
        id="maintenance_updates_parent",
    ),
    pytest.param("templates", "retriever.requester.error_handler", 3, id="templates"),
    pytest.param("team", "retriever.requester.error_handler", 3, id="team"),
    pytest.param("subscribers", "retriever.requester.error_handler", 3, id="subscribers"),
    pytest.param("metrics", "retriever.requester.error_handler", 3, id="metrics"),
    pytest.param("public_data", "retriever.requester.error_handler", 5, id="public_data"),
]


def _read_manifest() -> dict[str, Any]:
    return ManifestReferenceResolver().preprocess_manifest(yaml.safe_load(_YAML_FILE_PATH.read_text()))


def _at_path(component: dict[str, Any], path: str) -> dict[str, Any]:
    for part in path.split("."):
        component = component[int(part)] if part.isdigit() else component[part]
    return component


def _response(status_code: int, headers: dict[str, str] | None = None) -> requests.Response:
    response = requests.Response()
    response.status_code = status_code
    response.headers.update(headers or {})
    response.request = requests.Request("GET", "https://api.instatus.com/example").prepare()
    response.url = response.request.url
    return response


@pytest.mark.parametrize("stream_name,path,expected_max_retries", _HANDLER_LOCATIONS)
def test_shared_error_handlers_preserve_response_behavior(stream_name: str, path: str, expected_max_retries: int) -> None:
    manifest = _read_manifest()
    handler_definition = _at_path(manifest["definitions"]["streams"][stream_name], path)
    handler_definition = ManifestComponentTransformer().propagate_types_and_parameters(
        "HttpRequester.error_handler", handler_definition, {}
    )
    assert handler_definition["type"] == "DefaultErrorHandler"
    handler = ModelToComponentFactory().create_component(DefaultErrorHandlerModel, handler_definition, config={"api_key": "k"})

    assert handler.max_retries == expected_max_retries
    assert handler.interpret_response(_response(401)).response_action == ResponseAction.IGNORE
    rate_limit_response = _response(429, {"Retry-After": "7"})
    assert handler.interpret_response(rate_limit_response).response_action == ResponseAction.RETRY
    assert isinstance(handler.backoff_strategies[0], WaitTimeFromHeaderBackoffStrategy)
    assert handler.backoff_strategies[0].backoff_time(rate_limit_response, 1) == 7
    assert handler.interpret_response(_response(500)).response_action == ResponseAction.RETRY
    assert handler.interpret_response(_response(403)).response_action == ResponseAction.FAIL


def test_manifest_has_no_composite_error_handlers() -> None:
    assert "CompositeErrorHandler" not in _YAML_FILE_PATH.read_text()


def _read_page_components() -> EntrypointOutput:
    config = {"api_key": "test-api-key"}
    catalog = CatalogBuilder().with_stream("page_components", SyncMode.full_refresh).build()
    return read(get_source(config, catalog), config, catalog)


def test_page_components_ignores_401(requests_mock: requests_mock_lib.Mocker) -> None:
    requests_mock.get("https://api.instatus.com/v2/pages", json=[{"id": "p1", "subdomain": "s"}])
    component_url = "https://api.instatus.com/v1/p1/components"
    requests_mock.get(component_url, status_code=401)

    output = _read_page_components()

    assert output.records == []
    assert output.errors == []
    assert sum(request.url == component_url for request in requests_mock.request_history) == 1


def test_page_components_retries_429_with_retry_after(requests_mock: requests_mock_lib.Mocker, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("time.sleep", lambda *_args, **_kwargs: None)
    requests_mock.get("https://api.instatus.com/v2/pages", json=[{"id": "p1", "subdomain": "s"}])
    component_url = "https://api.instatus.com/v1/p1/components"
    requests_mock.get(
        component_url,
        response_list=[
            {"status_code": 429, "headers": {"Retry-After": "1"}},
            {"status_code": 200, "json": [{"id": "c1"}]},
        ],
    )

    output = _read_page_components()

    assert output.errors == []
    assert [message.record.data["id"] for message in output.records] == ["c1"]
    assert sum(request.url == component_url for request in requests_mock.request_history) == 2
