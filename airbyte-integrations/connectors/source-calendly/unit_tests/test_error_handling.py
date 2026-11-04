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


URL = "https://api.calendly.com/scheduled_events/ABC/invitees"
FAN_OUT_STREAMS = {"event_type_memberships", "user_availability_schedules", "locations"}


@pytest.mark.parametrize(
    "stream",
    [
        "api_user",
        "event_types",
        "groups",
        "organization_memberships",
        "scheduled_events",
        "event_invitees",
        "teams",
        "event_type_memberships",
        "group_relationships",
        "user_availability_schedules",
        "locations",
        "organization_invitations",
        "webhook_subscriptions",
    ],
)
@pytest.mark.parametrize(
    "status,action,failure_type,message",
    [
        (401, ResponseAction.FAIL, FailureType.config_error, "Calendly rejected the personal access token"),
        (403, ResponseAction.FAIL, FailureType.config_error, "owner or admin of the Calendly organization"),
        (404, ResponseAction.FAIL, FailureType.system_error, f"Calendly returned 404 for {URL}: Calendly response detail"),
        (429, ResponseAction.RATE_LIMITED, FailureType.transient_error, None),
        *[
            (status, ResponseAction.RETRY, FailureType.transient_error, "Calendly API is temporarily unavailable.")
            for status in [500, 502, 503, 504]
        ],
    ],
)
def test_each_requester_classifies_errors(stream: str, status: int, action: ResponseAction, failure_type: FailureType, message) -> None:
    definition = next(s for s in resolved_manifest()["streams"] if s["name"] == stream)["retriever"]["requester"]["error_handler"]
    assert definition["type"] == "DefaultErrorHandler"
    handler = ModelToComponentFactory().create_component(DefaultErrorHandlerModel, definition, config=CONFIG)
    assert isinstance(handler, DefaultErrorHandler)
    response = requests.Response()
    response.status_code = status
    response.url = f"{URL}?count=100"
    response._content = json.dumps({"title": "API error", "message": "Calendly response detail"}).encode()
    response.headers["X-RateLimit-Reset"] = "60"
    resolution = handler.interpret_response(response)
    if stream == "event_invitees" and status == 404:
        assert resolution.response_action == ResponseAction.IGNORE
        assert resolution.error_message == f"Skipping invitees of a scheduled event that Calendly no longer returns (404): {URL}"
    elif stream in FAN_OUT_STREAMS and status == 404:
        assert resolution.response_action == ResponseAction.IGNORE
        assert resolution.error_message == f"Skipping a member or event type that Calendly no longer returns (404): {URL}"
    else:
        assert resolution.response_action == action
        assert resolution.failure_type == failure_type
        if message:
            assert message in resolution.error_message
    if status == 429:
        assert handler.backoff_time(response, attempt_count=1) == 60


@pytest.mark.parametrize(
    "status,body,expected",
    [
        (401, {"title": "Unauthenticated", "message": "The access token is invalid"}, ["open the Profile menu, select Developer"]),
        (
            403,
            {"title": "Permission Denied", "message": "You do not have permission to access this resource."},
            [
                "owner or admin of the Calendly organization",
                "read scope of every selected stream",
                "scheduled events and webhook subscriptions",
            ],
        ),
        (
            403,
            {
                "title": "Insufficient scope",
                "message": "This operation requires the scopes listed in the 'required_scopes' array.",
                "required_scopes": ["users:read"],
            },
            ["Missing scopes: users:read"],
        ),
    ],
)
def test_authentication_error_read_includes_response_and_remediation(status: int, body: dict, expected: list) -> None:
    with HttpMocker() as http:
        target = request("users/me")
        http.get(target, HttpResponse(body=json.dumps(body), status_code=status))
        output = read_stream("api_user")
        assert output.errors
        error = output.errors[0].trace.error
        assert error.failure_type == FailureType.config_error
        assert f"Calendly response ({status}): {body['message']}" in error.message
        assert "update it in the Airbyte source settings" in error.message
        for text in expected:
            assert text in error.message
        if body["title"] == "Permission Denied":
            assert "users:read, event_types:read" not in error.message
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
