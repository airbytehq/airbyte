# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Per-filter tests for the merged Zoom error handlers in `manifest.yaml`.

Each requester uses one `DefaultErrorHandler`. Stream-specific filters come first, followed by the
shared `zoom_token_refresh_filter` (HTTP 401, code 124) and, where no stream-specific filter answers
it first, the shared `zoom_missing_scope_filter` (HTTP 400, code 4711). Zoom error bodies carry
`code` and `message`, with the HTTP statuses used below (see `integration/zoom_mocks.py`).
"""

import json
from pathlib import Path
from typing import Any, Dict, Iterator, Optional, Tuple

import pytest
import requests
import yaml

from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.declarative.models.declarative_component_schema import DefaultErrorHandler as DefaultErrorHandlerModel
from airbyte_cdk.sources.declarative.parsers.manifest_component_transformer import ManifestComponentTransformer
from airbyte_cdk.sources.declarative.parsers.manifest_reference_resolver import ManifestReferenceResolver
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ResponseAction


_CI_MANIFEST_DIR = Path("/airbyte/integration_code/source_declarative_manifest")
_MANIFEST_DIR = _CI_MANIFEST_DIR if _CI_MANIFEST_DIR.exists() else Path(__file__).parent.parent
_MANIFEST_PATH = _MANIFEST_DIR / "manifest.yaml"

_REPORT_USER_MEETINGS_PATH = "/report/users/{{ stream_partition.parent_id }}/meetings"
_REPORT_DAILY_PATH = "/report/daily"
_CHAT_CHANNELS_PATH = "/chat/users/{{ stream_partition.parent_id }}/channels"
_ZOOM_EVENTS_PATH = "/zoom_events/events"

_GENERIC_MISSING_SCOPE_MESSAGE = "Zoom access token lacks a required scope ('no scope')."


def _resolved_manifest() -> Dict[str, Any]:
    manifest = yaml.safe_load(_MANIFEST_PATH.read_text())
    manifest["type"] = "DeclarativeSource"
    manifest = ManifestReferenceResolver().preprocess_manifest(manifest)
    return ManifestComponentTransformer().propagate_types_and_parameters("", manifest, {})


_MANIFEST = _resolved_manifest()


def _requester_error_handlers(node: Any, location: str = "") -> Iterator[Tuple[str, str, Dict[str, Any]]]:
    if isinstance(node, dict):
        if isinstance(node.get("requester"), dict) and "error_handler" in node["requester"]:
            yield location, node["requester"].get("path", ""), node["requester"]["error_handler"]
        for key, value in node.items():
            yield from _requester_error_handlers(value, f"{location}.{key}")
    elif isinstance(node, list):
        for index, value in enumerate(node):
            yield from _requester_error_handlers(value, f"{location}[{index}]")


_ALL_ERROR_HANDLERS = {location: handler for location, _, handler in _requester_error_handlers(_MANIFEST)}


def _handler_for_path(path: str) -> Dict[str, Any]:
    return next(handler for _, handler_path, handler in _requester_error_handlers(_MANIFEST["streams"]) if handler_path == path)


def _build(handler_definition: Dict[str, Any]):
    return ModelToComponentFactory().create_component(DefaultErrorHandlerModel, handler_definition, config={})


def _named(name: str):
    return _build(_MANIFEST["definitions"][name])


def _response(status_code: int, body: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> requests.Response:
    response = requests.Response()
    response.status_code = status_code
    response._content = json.dumps(body).encode()
    response.headers["Content-Type"] = "application/json"
    response.headers.update(headers or {})
    response.url = "https://api.zoom.us/v2/test"
    return response


def _zoom_error(code: int, message: str, status_code: int) -> requests.Response:
    return _response(status_code, {"code": code, "message": message})


@pytest.mark.parametrize("location", sorted(_ALL_ERROR_HANDLERS))
def test_every_error_handler_refreshes_the_token_on_code_124(location):
    resolution = _build(_ALL_ERROR_HANDLERS[location]).interpret_response(_zoom_error(124, "Access token is expired.", 401))

    assert resolution.response_action == ResponseAction.REFRESH_TOKEN_THEN_RETRY


@pytest.mark.parametrize("location", sorted(_ALL_ERROR_HANDLERS))
def test_every_error_handler_waits_for_the_retry_after_header(location):
    handler = _build(_ALL_ERROR_HANDLERS[location])

    assert handler.backoff_time(_response(429, {}, {"Retry-After": "7"}), attempt_count=1) == 7


@pytest.mark.parametrize(
    "handler_name",
    [
        "zoom_error_handler",
        "zoom_skip_meetings_disabled_user_error_handler",
        "zoom_skip_missing_resource_error_handler",
        "zoom_meeting_registrants_error_handler",
    ],
)
def test_missing_scope_4711_is_a_config_error(handler_name):
    resolution = _named(handler_name).interpret_response(_zoom_error(4711, "no scope", 400))

    assert resolution.response_action == ResponseAction.FAIL
    assert resolution.failure_type == FailureType.config_error
    assert resolution.error_message.startswith(_GENERIC_MISSING_SCOPE_MESSAGE)


# These handlers skip every HTTP 400 before the shared filters run, so a 4711 is skipped as well.
@pytest.mark.parametrize(
    "handler_name",
    [
        "zoom_skip_missing_resource_or_bad_request_error_handler",
        "zoom_skip_bad_request_or_not_found_error_handler",
        "zoom_skip_bad_request_error_handler",
    ],
)
def test_bad_request_is_skipped_before_the_missing_scope_filter(handler_name):
    handler = _named(handler_name)

    assert handler.interpret_response(_response(400, {})).response_action == ResponseAction.IGNORE
    assert handler.interpret_response(_zoom_error(4711, "no scope", 400)).response_action == ResponseAction.IGNORE


def test_not_found_without_a_skip_filter_fails():
    assert _named("zoom_error_handler").interpret_response(_response(404, {})).response_action == ResponseAction.FAIL


@pytest.mark.parametrize("handler_name", ["zoom_skip_bad_request_or_not_found_error_handler", "zoom_skip_not_found_error_handler"])
def test_not_found_is_skipped(handler_name):
    assert _named(handler_name).interpret_response(_response(404, {})).response_action == ResponseAction.IGNORE


def test_meetings_disabled_user_3161_is_skipped():
    handler = _named("zoom_skip_meetings_disabled_user_error_handler")

    resolution = handler.interpret_response(_zoom_error(3161, "User is not allowed to host meetings.", 400))

    assert resolution.response_action == ResponseAction.IGNORE
    assert resolution.error_message.startswith("Zoom returned code 3161 ('User is not allowed to host meetings.')")


@pytest.mark.parametrize(
    "handler_name",
    [
        "zoom_skip_missing_resource_error_handler",
        "zoom_meeting_registrants_error_handler",
        "zoom_skip_missing_resource_or_bad_request_error_handler",
    ],
)
def test_missing_resource_3001_is_skipped(handler_name):
    resolution = _named(handler_name).interpret_response(_zoom_error(3001, "Meeting does not exist.", 404))

    assert resolution.response_action == ResponseAction.IGNORE
    assert resolution.error_message.startswith("Zoom returned code 3001 ('Meeting does not exist.')")


def test_meeting_registrants_skips_code_300():
    resolution = _named("zoom_meeting_registrants_error_handler").interpret_response(
        _zoom_error(300, "Registration has not been enabled for this meeting.", 404)
    )

    assert resolution.response_action == ResponseAction.IGNORE


@pytest.mark.parametrize(
    "path, scope",
    [
        (_REPORT_USER_MEETINGS_PATH, "report:read:user:admin"),
        (_REPORT_DAILY_PATH, "report:read:daily_usage:admin"),
        (_CHAT_CHANNELS_PATH, "team_chat:read:list_user_channels:admin"),
        (_ZOOM_EVENTS_PATH, "zoom_events:read:list_events:admin"),
    ],
)
def test_stream_specific_missing_scope_message_names_the_scope(path, scope):
    resolution = _build(_handler_for_path(path)).interpret_response(_zoom_error(4711, "no scope", 400))

    assert resolution.response_action == ResponseAction.FAIL
    assert resolution.failure_type == FailureType.config_error
    assert resolution.error_message.startswith("Zoom returned code 4711 ('no scope')")
    assert scope in resolution.error_message


@pytest.mark.parametrize("path", [_REPORT_USER_MEETINGS_PATH, _CHAT_CHANNELS_PATH])
def test_user_removed_after_discovery_1001_is_skipped(path):
    resolution = _build(_handler_for_path(path)).interpret_response(_zoom_error(1001, "User does not exist.", 404))

    assert resolution.response_action == ResponseAction.IGNORE


@pytest.mark.parametrize("path", [_REPORT_USER_MEETINGS_PATH, _REPORT_DAILY_PATH])
def test_report_window_older_than_six_months_is_skipped(path):
    handler = _build(_handler_for_path(path))

    assert (
        handler.interpret_response(_zoom_error(300, "The request is outside the last six months.", 400)).response_action
        == ResponseAction.IGNORE
    )
    assert handler.interpret_response(_zoom_error(300, "Invalid parameter.", 400)).response_action == ResponseAction.FAIL


@pytest.mark.parametrize(
    "path, scope",
    [(_REPORT_USER_MEETINGS_PATH, "report:read:user:admin"), (_REPORT_DAILY_PATH, "report:read:daily_usage:admin")],
)
def test_reports_without_a_paid_plan_200_is_a_config_error(path, scope):
    resolution = _build(_handler_for_path(path)).interpret_response(_zoom_error(200, "Reports require a paid account.", 400))

    assert resolution.response_action == ResponseAction.FAIL
    assert resolution.failure_type == FailureType.config_error
    assert scope in resolution.error_message
