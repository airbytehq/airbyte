# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest
import yaml
from conftest import _YAML_FILE_PATH, get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.models.declarative_component_schema import DefaultErrorHandler as DefaultErrorHandlerModel
from airbyte_cdk.sources.declarative.parsers.manifest_reference_resolver import ManifestReferenceResolver
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory
from airbyte_cdk.sources.declarative.requesters.error_handlers.backoff_strategies.wait_time_from_header_backoff_strategy import (
    WaitTimeFromHeaderBackoffStrategy,
)
from airbyte_cdk.sources.declarative.requesters.error_handlers.default_error_handler import DefaultErrorHandler
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


STREAM_NAMES = [
    "organizations",
    "projects",
    "saved_searches",
    "saved_searches_usage_summary",
    "errors",
    "events",
    "pivots",
    "supported_integrations",
    "collaborators",
    "teams",
    "event_fields",
    "releases",
    "trace_fields",
]
COMPOSITE_HANDLER_TYPE = "".join(("Composite", "ErrorHandler"))
CONFIG = {"auth_token": "test-token", "start_date": "2024-01-01T00:00:00Z"}
ORGANIZATIONS_REQUEST = HttpRequest(
    "https://api.bugsnag.com/user/organizations",
    query_params={"per_page": "50"},
    headers={"Authorization": "token test-token", "X-Version": "2"},
)


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    slept = []
    monkeypatch.setattr("time.sleep", lambda seconds=0, *_args, **_kwargs: slept.append(seconds))
    return slept


def _resolved_manifest():
    return ManifestReferenceResolver().preprocess_manifest(yaml.safe_load(_YAML_FILE_PATH.read_text()))


def test_manifest_has_no_composite_error_handler() -> None:
    composite_handlers = []

    def walk(node):
        if isinstance(node, dict):
            if node.get("type") == COMPOSITE_HANDLER_TYPE:
                composite_handlers.append(node)
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(_resolved_manifest())

    assert not composite_handlers


@pytest.mark.parametrize("stream", STREAM_NAMES)
def test_stream_error_handler_waits_for_retry_after_header(stream: str) -> None:
    manifest = _resolved_manifest()
    stream_definition = next(stream_definition for stream_definition in manifest["streams"] if stream_definition["name"] == stream)
    handler_definition = stream_definition["retriever"]["requester"]["error_handler"]
    error_handler = ModelToComponentFactory().create_component(DefaultErrorHandlerModel, handler_definition, config={})

    assert isinstance(error_handler, DefaultErrorHandler)
    assert len(error_handler.backoff_strategies) == 1
    strategy = error_handler.backoff_strategies[0]
    assert isinstance(strategy, WaitTimeFromHeaderBackoffStrategy)
    assert strategy.header.string == "Retry-After"


def test_organizations_retries_after_retry_after_header(no_sleep) -> None:
    with HttpMocker() as http_mocker:
        http_mocker.get(
            ORGANIZATIONS_REQUEST,
            [
                HttpResponse(body="{}", status_code=429, headers={"Retry-After": "7"}),
                HttpResponse(body=json.dumps([{"id": "org1"}]), status_code=200),
            ],
        )

        catalog = CatalogBuilder().with_stream("organizations", SyncMode.full_refresh).build()
        output = read(get_source(CONFIG), CONFIG, catalog)

        http_mocker.assert_number_of_calls(ORGANIZATIONS_REQUEST, 2)

    assert len(output.records) == 1
    assert output.records[0].record.data["id"] == "org1"
    assert 8 in no_sleep
