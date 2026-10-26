# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import discover, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder


_CONFIG = {
    "client_id": "test-client",
    "client_secret": "test-secret",
    "tenant_id": "test-tenant",
    "user_id": "test-user",
}
_GRAPH_BASE = "https://graph.microsoft.com/v1.0"
_USERS_DELTA = f"{_GRAPH_BASE}/users/delta"
_GROUPS_DELTA = f"{_GRAPH_BASE}/groups/delta"
_TOKEN_URL = "https://login.microsoftonline.com/test-tenant/oauth2/v2.0/token"
_TOKEN_REQUEST_BODY = (
    "grant_type=client_credentials"
    "&client_id=test-client"
    "&client_secret=test-secret"
    "&scope=https%3A%2F%2Fgraph.microsoft.com%2F.default"
)
_GROUP_SELECT = (
    "id,deletedDateTime,classification,createdDateTime,creationOptions,description,displayName,"
    "expirationDateTime,groupTypes,isAssignableToRole,mail,mailEnabled,mailNickname,membershipRule,"
    "membershipRuleProcessingState,onPremisesDomainName,onPremisesLastSyncDateTime,"
    "onPremisesNetBiosName,onPremisesProvisioningErrors,onPremisesSamAccountName,"
    "onPremisesSecurityIdentifier,onPremisesSyncEnabled,preferredDataLocation,preferredLanguage,"
    "proxyAddresses,renewedDateTime,resourceBehaviorOptions,resourceProvisioningOptions,"
    "securityEnabled,securityIdentifier,serviceProvisioningErrors,theme,visibility"
)
_GROUPS_INITIAL = f"{_GROUPS_DELTA}?$select={_GROUP_SELECT}"


def _mock_oauth(http_mocker: HttpMocker) -> None:
    http_mocker.post(
        HttpRequest(_TOKEN_URL, body=_TOKEN_REQUEST_BODY),
        HttpResponse(
            body=json.dumps({"access_token": "test-access-token", "expires_in": 3600}),
        ),
    )


def _read(
    http_mocker: HttpMocker,
    streams: list[str],
    state=None,
    sync_mode: SyncMode = SyncMode.incremental,
):
    _mock_oauth(http_mocker)
    catalog_builder = CatalogBuilder()
    for stream_name in streams:
        catalog_builder.with_stream(stream_name, sync_mode)
    catalog = catalog_builder.build()
    return read(
        get_source(_CONFIG, catalog=catalog, state=state),
        config=_CONFIG,
        catalog=catalog,
        state=state,
    )


def _mock_delta_page(http_mocker: HttpMocker, url: str, body: dict, status_code: int = 200) -> None:
    http_mocker.get(
        HttpRequest(url),
        HttpResponse(body=json.dumps(body), status_code=status_code),
    )


def _graph_request_urls(http_mocker: HttpMocker) -> list[str]:
    return [request.url for request in http_mocker._mocker.request_history if request.url.startswith(_GRAPH_BASE)]


def _state_for(stream_name: str, token: str):
    return (
        StateBuilder()
        .with_stream_state(
            stream_name,
            {"state_type": "sync_token", "token": token},
        )
        .build()
    )


def _token_from_state(output, stream_name: str) -> str:
    state = next(
        message.state.stream.stream_state for message in output.state_messages if message.state.stream.stream_descriptor.name == stream_name
    )
    return state.token


def test_discover_users_and_groups_support_incremental_only():
    output = discover(get_source(_CONFIG), config=_CONFIG)

    assert output.errors == []
    streams = {stream.name: stream for stream in output.catalog.catalog.streams}
    for stream_name in ("users", "groups"):
        stream = streams[stream_name]
        assert stream.supported_sync_modes == [SyncMode.full_refresh, SyncMode.incremental]
        assert stream.source_defined_cursor is True
        assert not stream.default_cursor_field
    for stream_name, stream in streams.items():
        if stream_name not in ("users", "groups"):
            assert stream.supported_sync_modes == [SyncMode.full_refresh]


def test_users_initial_incremental_sync_follows_next_link_filters_removed_and_stores_delta_link():
    next_link = f"{_USERS_DELTA}?$skiptoken=next-page"
    delta_link = f"{_USERS_DELTA}?$deltatoken=finished"
    first_user = {"id": "user-1", "displayName": "First user"}
    second_user = {"id": "user-2", "displayName": "Second user"}
    with HttpMocker() as http_mocker:
        _mock_delta_page(
            http_mocker,
            _USERS_DELTA,
            {
                "value": [first_user, {"id": "removed-user", "@removed": {"reason": "deleted"}}],
                "@odata.nextLink": next_link,
            },
        )
        _mock_delta_page(
            http_mocker,
            next_link,
            {"value": [second_user], "@odata.deltaLink": delta_link},
        )

        output = _read(http_mocker, ["users"])

        assert output.errors == [], output.get_formatted_error_message()
        assert [message.record.data for message in output.records] == [first_user, second_user]
        assert _graph_request_urls(http_mocker) == [_USERS_DELTA, next_link]
        assert _token_from_state(output, "users") == delta_link


def test_users_change_sync_emits_updates_and_removed_records():
    stored_delta_link = f"{_USERS_DELTA}?$deltatoken=stored"
    new_delta_link = f"{_USERS_DELTA}?$deltatoken=updated"
    updated_user = {
        "id": "user-1",
        "displayName": "Updated user",
        "userPrincipalName": "user@example.com",
        "businessPhones": ["555-0100"],
    }
    removed_user = {"id": "user-2", "@removed": {"reason": "deleted"}}
    with HttpMocker() as http_mocker:
        _mock_delta_page(
            http_mocker,
            stored_delta_link,
            {"value": [updated_user, removed_user], "@odata.deltaLink": new_delta_link},
        )

        output = _read(http_mocker, ["users"], state=_state_for("users", stored_delta_link))

        assert output.errors == [], output.get_formatted_error_message()
        assert [message.record.data for message in output.records] == [updated_user, removed_user]
        assert _graph_request_urls(http_mocker) == [stored_delta_link]
        assert _token_from_state(output, "users") == new_delta_link


def test_users_empty_terminal_page_advances_state():
    stored_delta_link = f"{_USERS_DELTA}?$deltatoken=stored"
    new_delta_link = f"{_USERS_DELTA}?$deltatoken=empty-page"
    with HttpMocker() as http_mocker:
        _mock_delta_page(
            http_mocker,
            stored_delta_link,
            {"value": [], "@odata.deltaLink": new_delta_link},
        )

        output = _read(http_mocker, ["users"], state=_state_for("users", stored_delta_link))

        assert output.errors == [], output.get_formatted_error_message()
        assert output.records == []
        assert _graph_request_urls(http_mocker) == [stored_delta_link]
        assert _token_from_state(output, "users") == new_delta_link


@pytest.mark.parametrize(
    ("status_code", "body"),
    [
        (410, {"error": {"code": "Gone", "message": "Expired delta link"}}),
        (400, {"error": {"code": "syncStateNotFound", "message": "State not found"}}),
    ],
)
def test_users_expired_delta_token_restarts_full_delta_read(status_code: int, body: dict):
    stored_delta_link = f"{_USERS_DELTA}?$deltatoken=expired"
    new_delta_link = f"{_USERS_DELTA}?$deltatoken=restarted"
    with HttpMocker() as http_mocker:
        _mock_delta_page(http_mocker, stored_delta_link, body, status_code=status_code)
        _mock_delta_page(
            http_mocker,
            _USERS_DELTA,
            {"value": [{"id": "user-1", "displayName": "User"}], "@odata.deltaLink": new_delta_link},
        )

        output = _read(http_mocker, ["users"], state=_state_for("users", stored_delta_link))

        assert output.errors == [], output.get_formatted_error_message()
        assert _graph_request_urls(http_mocker) == [stored_delta_link, _USERS_DELTA]
        assert [message.record.data["id"] for message in output.records] == ["user-1"]
        assert _token_from_state(output, "users") == new_delta_link


def test_groups_initial_request_selects_properties_and_follows_next_link_exactly():
    next_link = f"{_GROUPS_DELTA}?$skiptoken=group-page-2"
    delta_link = f"{_GROUPS_DELTA}?$deltatoken=groups-finished"
    with HttpMocker() as http_mocker:
        _mock_delta_page(
            http_mocker,
            _GROUPS_INITIAL,
            {"value": [{"id": "group-1", "displayName": "Group"}], "@odata.nextLink": next_link},
        )
        _mock_delta_page(
            http_mocker,
            next_link,
            {"value": [{"id": "group-2", "displayName": "Next group"}], "@odata.deltaLink": delta_link},
        )

        output = _read(http_mocker, ["groups"])

        assert output.errors == [], output.get_formatted_error_message()
        assert _graph_request_urls(http_mocker) == [_GROUPS_INITIAL, next_link]
        assert [message.record.data["id"] for message in output.records] == ["group-1", "group-2"]
        assert _token_from_state(output, "groups") == delta_link


def test_users_and_groups_keep_independent_delta_tokens():
    user_delta_link = f"{_USERS_DELTA}?$deltatoken=users-stored"
    updated_user_link = f"{_USERS_DELTA}?$deltatoken=users-updated"
    group_delta_link = f"{_GROUPS_DELTA}?$deltatoken=groups-updated"
    state = _state_for("users", user_delta_link)
    with HttpMocker() as http_mocker:
        _mock_delta_page(
            http_mocker,
            user_delta_link,
            {"value": [{"id": "user-1"}], "@odata.deltaLink": updated_user_link},
        )
        _mock_delta_page(
            http_mocker,
            _GROUPS_INITIAL,
            {"value": [{"id": "group-1"}], "@odata.deltaLink": group_delta_link},
        )

        output = _read(http_mocker, ["users", "groups"], state=state)

        assert output.errors == [], output.get_formatted_error_message()
        assert _graph_request_urls(http_mocker) == [user_delta_link, _GROUPS_INITIAL]
        assert _token_from_state(output, "users") == updated_user_link
        assert _token_from_state(output, "groups") == group_delta_link


def test_users_full_refresh_uses_delta_endpoint_and_filters_removed_records():
    with HttpMocker() as http_mocker:
        _mock_delta_page(
            http_mocker,
            _USERS_DELTA,
            {
                "value": [
                    {"id": "user-1", "displayName": "User"},
                    {"id": "removed-user", "@removed": {"reason": "deleted"}},
                ],
                "@odata.deltaLink": f"{_USERS_DELTA}?$deltatoken=full-refresh",
            },
        )

        output = _read(http_mocker, ["users"], sync_mode=SyncMode.full_refresh)

        assert output.errors == [], output.get_formatted_error_message()
        assert _graph_request_urls(http_mocker) == [_USERS_DELTA]
        assert [message.record.data["id"] for message in output.records] == ["user-1"]
