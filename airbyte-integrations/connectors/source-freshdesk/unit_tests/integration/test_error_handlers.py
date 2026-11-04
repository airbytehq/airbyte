# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
import sys
import time
from pathlib import Path

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
_SOURCE_FOLDER_PATH = Path(__file__).parent.parent.parent
_YAML_FILE_PATH = _SOURCE_FOLDER_PATH / "manifest.yaml"

sys.path.append(str(_SOURCE_FOLDER_PATH))

_CONVERTED_STREAMS = {
    "agents",
    "business_hours",
    "canned_response_folders",
    "canned_responses",
    "companies",
    "conversations",
    "contacts",
    "discussion_categories",
    "discussion_comments",
    "discussion_forums",
    "discussion_topics",
    "email_configs",
    "email_mailboxes",
    "groups",
    "products",
    "roles",
    "scenario_automations",
    "settings",
    "skills",
    "sla_policies",
    "solution_articles",
    "solution_categories",
    "solution_folders",
    "ticket_fields",
    "tickets",
    "time_entries",
}
_TOP_LEVEL_STREAM_ENDPOINTS = {
    "agents": "agents",
    "business_hours": "business_hours",
    "canned_response_folders": "canned_response_folders",
    "companies": "companies",
    "contacts": "contacts",
    "discussion_categories": "discussions/categories",
    "email_configs": "email_configs",
    "email_mailboxes": "email/mailboxes",
    "groups": "groups",
    "products": "products",
    "roles": "roles",
    "scenario_automations": "scenario_automations",
    "settings": "settings/helpdesk",
    "skills": "skills",
    "sla_policies": "sla_policies",
    "solution_categories": "solutions/categories",
    "ticket_fields": "ticket_fields",
    "tickets": "tickets",
    "time_entries": "time_entries",
}
_RETRY_AFTER_SECONDS = 7
_EXPECTED_UNAUTHORIZED_MESSAGE = (
    "The endpoint to access stream {stream_name} returned 401: Unauthorized. " "This is most likely due to wrong credentials."
)


def _catalog(stream_name: str) -> ConfiguredAirbyteCatalog:
    return CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()


def _read(stream_name: str, expecting_exception: bool = False) -> EntrypointOutput:
    catalog = _catalog(stream_name)
    config = ConfigBuilder().domain(_DOMAIN).build()
    state = StateBuilder().build()
    source = YamlDeclarativeSource(path_to_yaml=str(_YAML_FILE_PATH), catalog=catalog, config=config, state=state)
    return entrypoint_read(source, config, catalog, state, expecting_exception)


def _request(stream_name: str) -> HttpRequest:
    endpoint = _TOP_LEVEL_STREAM_ENDPOINTS[stream_name]
    return HttpRequest(f"https://{_DOMAIN}/api/v2/{endpoint}", query_params=ANY_QUERY_PARAMS)


def test_every_stream_error_handler_names_its_stream() -> None:
    config = ConfigBuilder().domain(_DOMAIN).build()
    source = YamlDeclarativeSource(path_to_yaml=str(_YAML_FILE_PATH), config=config)
    streams = source.resolved_manifest["streams"]
    stream_names = {}
    for stream in streams:
        error_handler = stream.get("retriever", {}).get("requester", {}).get("error_handler", {})
        parameters = error_handler.get("$parameters", {})
        if "stream_name" in parameters:
            stream_names[stream["name"]] = parameters["stream_name"]

    assert set(stream_names) == _CONVERTED_STREAMS
    assert all(stream_name == parameter_name for stream_name, parameter_name in stream_names.items())


@pytest.mark.parametrize("stream_name", _TOP_LEVEL_STREAM_ENDPOINTS)
def test_unauthorized_surfaces_stream_specific_message(stream_name: str) -> None:
    request = _request(stream_name)
    with HttpMocker() as http_mocker:
        http_mocker.get(request, HttpResponse(json.dumps({"code": "access_denied", "message": "Unauthorized"}), 401))

        output = _read(stream_name, expecting_exception=True)

        http_mocker.assert_number_of_calls(request, 1)

    assert any(
        error.trace.error.failure_type == FailureType.config_error
        and error.trace.error.message == _EXPECTED_UNAUTHORIZED_MESSAGE.format(stream_name=stream_name)
        for error in output.errors
    ), [error.trace.error for error in output.errors]


@pytest.mark.parametrize("stream_name", ("agents", "tickets"))
def test_rate_limit_waits_retry_after_header(stream_name: str, monkeypatch: pytest.MonkeyPatch) -> None:
    request = _request(stream_name)
    waits = []
    monkeypatch.setattr(time, "sleep", waits.append)

    with HttpMocker() as http_mocker:
        http_mocker.get(
            request,
            [
                HttpResponse("[]", 429, headers={"Retry-After": str(_RETRY_AFTER_SECONDS)}),
                HttpResponse("[]", 200),
            ],
        )

        output = _read(stream_name)

        http_mocker.assert_number_of_calls(request, 2)

    assert not output.errors
    # The CDK rate-limit handler sleeps one extra second on top of the backoff time.
    assert _RETRY_AFTER_SECONDS + 1 in waits
