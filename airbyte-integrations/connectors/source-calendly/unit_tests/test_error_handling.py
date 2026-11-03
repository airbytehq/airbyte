# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest
import requests
import yaml
from _helpers import CONFIG, collection, event, invitees_request, list_request, mock_user, read_stream, request
from conftest import _YAML_FILE_PATH

from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.declarative.models.declarative_component_schema import DefaultErrorHandler as DefaultErrorHandlerModel
from airbyte_cdk.sources.declarative.parsers.manifest_reference_resolver import ManifestReferenceResolver
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory
from airbyte_cdk.sources.declarative.requesters.error_handlers.default_error_handler import DefaultErrorHandler
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ResponseAction
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse


def resolved_manifest() -> dict:
    return ManifestReferenceResolver().preprocess_manifest(yaml.safe_load(_YAML_FILE_PATH.read_text()))


def test_no_composite_error_handler() -> None:
    def walk(node):
        if isinstance(node, dict):
            assert node.get("type") != "CompositeErrorHandler"
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(resolved_manifest())


@pytest.mark.parametrize("stream", ["api_user", "event_types", "groups", "organization_memberships", "scheduled_events", "event_invitees"])
@pytest.mark.parametrize(
    "status,action,failure_type",
    [
        (401, ResponseAction.FAIL, FailureType.config_error),
        (403, ResponseAction.FAIL, FailureType.config_error),
        (404, ResponseAction.FAIL, FailureType.system_error),
        (429, ResponseAction.RATE_LIMITED, FailureType.transient_error),
        *[(status, ResponseAction.RETRY, FailureType.transient_error) for status in [500, 502, 503, 504]],
    ],
)
def test_each_requester_classifies_errors(stream: str, status: int, action: ResponseAction, failure_type: FailureType) -> None:
    definition = next(s for s in resolved_manifest()["streams"] if s["name"] == stream)["retriever"]["requester"]["error_handler"]
    assert definition["type"] == "DefaultErrorHandler"
    handler = ModelToComponentFactory().create_component(DefaultErrorHandlerModel, definition, config=CONFIG)
    assert isinstance(handler, DefaultErrorHandler)
    response = requests.Response()
    response.status_code = status
    response._content = json.dumps({"title": "API error", "message": "Calendly response detail"}).encode()
    response.headers["X-RateLimit-Reset"] = "60"
    resolution = handler.interpret_response(response)
    if stream == "event_invitees" and status == 404:
        assert resolution.response_action == ResponseAction.IGNORE
        assert resolution.failure_type == FailureType.system_error
    else:
        assert resolution.response_action == action
        assert resolution.failure_type == failure_type
    if status == 429:
        assert handler.backoff_time(response, attempt_count=1) == 60


@pytest.mark.parametrize(
    "status,remediation",
    [
        (401, "Create a new personal access token"),
        (403, "users:read, event_types:read, groups:read, organizations:read, and scheduled_events:read"),
    ],
)
def test_authentication_error_read_includes_response_and_remediation(status: int, remediation: str) -> None:
    with HttpMocker() as http:
        target = request("users/me")
        http.get(
            target, HttpResponse(body=json.dumps({"title": "Authentication error", "message": "Token access denied"}), status_code=status)
        )
        output = read_stream("api_user")
        assert output.errors
        error = output.errors[0].trace.error
        assert error.failure_type == FailureType.config_error
        assert "Token access denied" in error.message
        assert remediation in error.message
        http.assert_number_of_calls(target, 1)


def test_deleted_parent_event_skips_invitees_and_continues() -> None:
    with HttpMocker() as http:
        mock_user(http)
        http.get(list_request("scheduled_events"), collection([event("deleted"), event("present")]))
        deleted = invitees_request("deleted")
        present = invitees_request("present")
        http.get(deleted, HttpResponse(body='{"title":"Not Found","message":"Event deleted"}', status_code=404))
        invitee = {"uri": "https://api.calendly.com/invitees/one", "created_at": "2024-01-15T00:00:00.000000Z"}
        http.get(present, collection([invitee]))
        output = read_stream("event_invitees")
        assert not output.errors
        assert len(output.records) == 1
        assert output.records[0].record.data["scheduled_event_id"] == "present"
        http.assert_number_of_calls(deleted, 1)
        http.assert_number_of_calls(present, 1)
