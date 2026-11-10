# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import logging
from urllib.parse import parse_qs, urlparse

import jsonschema
import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.entrypoint_wrapper import discover
from airbyte_cdk.utils.traced_exception import AirbyteTracedException

from .conftest import find_stream, get_source, read_from_stream


URL = "https://api.hubapi.com/scheduler/2026-09/meetings/meeting-links"
SCHEMAS_URL = "https://api.hubapi.com/crm/v3/schemas"


@pytest.fixture(autouse=True)
def mock_schemas(requests_mock):
    requests_mock.get(SCHEMAS_URL, json={"results": []})


@pytest.fixture
def enabled_config(config):
    return {**config, "enable_meeting_links": True}


def link(link_id="1", link_type="PERSONAL_LINK"):
    return {
        "id": link_id,
        "type": link_type,
        "name": None,
        "slug": "example",
        "link": "https://meetings.hubspot.com/example",
        "organizerUserId": "12",
        "userIdsOfLinkMembers": ["12", "34"],
        "defaultLink": False,
        "paymentLinkId": None,
        "createdAt": "2026-01-01T00:00:00Z",
        "updatedAt": None,
    }


@pytest.mark.parametrize("auth", ["config", "oauth_config"])
def test_catalog_is_opt_in(auth, request, requests_mock, mock_dynamic_schema_requests):
    config = request.getfixturevalue(auth)
    requests_mock.post("https://api.hubapi.com/oauth/v1/token", json={"access_token": "token", "expires_in": 1800})
    default = discover(get_source(config), config).catalog.catalog.streams
    enabled = {**config, "enable_meeting_links": True}
    expanded = discover(get_source(enabled), enabled).catalog.catalog.streams
    assert len(default) == 38
    assert {s.name for s in expanded} == {s.name for s in default} | {"meeting_links"}
    old = {s.name: s for s in default}
    assert all(s == old[s.name] for s in expanded if s.name != "meeting_links")
    stream = next(s for s in expanded if s.name == "meeting_links")
    assert stream.supported_sync_modes == [SyncMode.full_refresh]
    assert stream.source_defined_primary_key == [["id"]]
    assert not any(r.path.startswith("/scheduler/") for r in requests_mock.request_history)


def test_short_page_continues_with_exact_opaque_cursor(enabled_config, requests_mock):
    endpoint = requests_mock.get(
        URL,
        [
            {"json": {"results": [link()], "paging": {"next": {"after": "AbC+/="}}}},
            {"json": {"results": [link("2", "GROUP_CALENDAR"), link("3", "ROUND_ROBIN_CALENDAR")]}},
        ],
    )
    output = read_from_stream(enabled_config, "meeting_links", SyncMode.full_refresh)
    assert [r.record.data["id"] for r in output.records] == ["1", "2", "3"]
    assert endpoint.call_count == 2
    assert endpoint.request_history[0].qs == {"limit": ["100"]}
    assert parse_qs(urlparse(endpoint.last_request.url).query) == {"limit": ["100"], "after": ["AbC+/="]}
    schema = find_stream("meeting_links", enabled_config).get_json_schema()
    for record in output.records:
        assert set(record.record.data) <= set(schema["properties"])
        jsonschema.validate(record.record.data, schema, format_checker=jsonschema.FormatChecker())


@pytest.mark.parametrize("paging", [{}, {"paging": None}, {"paging": {}}, {"paging": {"next": None}}, {"paging": {"next": {}}}])
def test_empty_terminal_page(enabled_config, requests_mock, paging):
    endpoint = requests_mock.get(URL, json={"results": [], **paging})
    output = read_from_stream(enabled_config, "meeting_links", SyncMode.full_refresh)
    assert not output.records
    assert not output.errors
    assert endpoint.call_count == 1


@pytest.mark.parametrize("status,headers", [(429, {}), (429, {"Retry-After": "0"}), (500, {}), (502, {}), (503, {})])
def test_transient_errors_retry(enabled_config, requests_mock, status, headers):
    endpoint = requests_mock.get(
        URL,
        [
            {"status_code": status, "json": {"message": "temporary"}, "headers": headers},
            {"json": {"results": [link()]}},
        ],
    )
    output = read_from_stream(enabled_config, "meeting_links", SyncMode.full_refresh)
    assert len(output.records) == 1
    assert endpoint.call_count == 2


def test_missing_scope_fails_actionably(enabled_config, requests_mock):
    endpoint = requests_mock.get(URL, status_code=403, json={"message": "Missing scope"})
    output = read_from_stream(enabled_config, "meeting_links", SyncMode.full_refresh, expecting_exception=True)
    assert output.errors
    assert "scheduler.meetings.meeting-link.read" in output.errors[0].trace.error.message
    assert endpoint.call_count == 1


def test_retry_is_bounded(enabled_config, requests_mock):
    endpoint = requests_mock.get(URL, status_code=503, json={"message": "temporary"})
    output = read_from_stream(enabled_config, "meeting_links", SyncMode.full_refresh, expecting_exception=True)
    assert output.errors
    assert endpoint.call_count == 6


def test_oauth_expiration_refreshes_and_retries(oauth_config, requests_mock):
    config = {**oauth_config, "enable_meeting_links": True}
    refresh = requests_mock.post(
        "https://api.hubapi.com/oauth/v1/token",
        [
            {"json": {"access_token": "schemas", "expires_in": 1800}},
            {"json": {"access_token": "old", "expires_in": 1800}},
            {"json": {"access_token": "new", "expires_in": 1800}},
        ],
    )
    endpoint = requests_mock.get(
        URL,
        [
            {"status_code": 401, "json": {"message": "expired"}},
            {"json": {"results": [link()]}},
        ],
    )
    output = read_from_stream(config, "meeting_links", SyncMode.full_refresh)
    assert len(output.records) == 1
    assert refresh.call_count == 3  # Schema resolver and stream have separate authenticators.
    assert endpoint.call_count == 2
    assert endpoint.last_request.headers["Authorization"] == "Bearer new"


@pytest.mark.parametrize(
    "enabled,prefix,expected",
    [(False, False, "meeting_links"), (False, True, "meeting_links"), (True, True, "custom_object_meeting_links")],
)
def test_custom_object_collision_is_opt_in(config, requests_mock, enabled, prefix, expected):
    config.update(enable_meeting_links=enabled, prefix_colliding_custom_objects=prefix)
    requests_mock.get(
        SCHEMAS_URL, json={"results": [{"name": "meeting_links", "fullyQualifiedName": "p123_meeting_links", "properties": []}]}
    )
    names = [s.name for s in get_source(config).streams(config)]
    assert names.count(expected) == 1
    assert len(names) == len(set(names))
    if enabled:
        assert names.count("meeting_links") == 1


def test_collision_without_prefix_fails_actionably(enabled_config, requests_mock):
    requests_mock.get(
        SCHEMAS_URL, json={"results": [{"name": "meeting_links", "fullyQualifiedName": "p123_meeting_links", "properties": []}]}
    )
    with pytest.raises(AirbyteTracedException, match="prefix_colliding_custom_objects"):
        get_source(enabled_config).streams(enabled_config)


def test_prefix_target_collision_fails_actionably(enabled_config, requests_mock):
    enabled_config["prefix_colliding_custom_objects"] = True
    requests_mock.get(
        SCHEMAS_URL,
        json={
            "results": [
                {"name": name, "fullyQualifiedName": "p123_" + name, "properties": []}
                for name in ["meeting_links", "custom_object_meeting_links"]
            ]
        },
    )
    with pytest.raises(AirbyteTracedException, match="Rename one of these custom objects"):
        get_source(enabled_config).streams(enabled_config)


def test_private_app_expiration_is_not_retried(enabled_config, requests_mock):
    endpoint = requests_mock.get(URL, status_code=401, json={"message": "expired"})
    output = read_from_stream(enabled_config, "meeting_links", SyncMode.full_refresh, expecting_exception=True)
    assert output.errors
    assert endpoint.call_count == 1


def test_old_selected_stream_needs_no_scheduler_scope(config, requests_mock):
    endpoint = requests_mock.get("https://api.hubapi.com/account-info/v3/details", json={"portalId": 123})
    output = read_from_stream(config, "account_details", SyncMode.full_refresh)
    assert len(output.records) == 1
    assert endpoint.call_count == 1
    assert not any(r.path.startswith("/scheduler/") for r in requests_mock.request_history)


def test_connection_check_still_uses_contacts(enabled_config, requests_mock, mock_dynamic_schema_requests):
    requests_mock.post("https://api.hubapi.com/crm/v3/objects/contact/search", json={"results": []})
    status = get_source(enabled_config).check(logging.getLogger("test"), config=enabled_config)
    assert status.status.value == "SUCCEEDED"
    assert not any(r.path.startswith("/scheduler/") for r in requests_mock.request_history)
