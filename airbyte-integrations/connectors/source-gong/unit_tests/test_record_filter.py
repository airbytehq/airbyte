# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

"""Unit tests for the auth-scoped `isPrivate` record filter on `source-gong` streams.

Gong's API listing requirements mandate that any integration using **OAuth 2.0** must
drop calls where `isPrivate` is `true` client-side (Gong's API does not expose a
server-side filter). Under **API Key** authentication the customer still owns every
call returned by the API, so no filtering is required.

The `calls` and `extensiveCalls` streams each declare a `RecordFilter` in `manifest.yaml`
whose Jinja `condition` inspects `config.credentials.auth_type` so the filter activates
only under OAuth. These tests mock the Gong API responses and assert the expected
behavior under both auth modes.
"""

import copy

import requests_mock
from _helpers import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


_API_KEY_CONFIG = {
    "credentials": {
        "auth_type": "APIKey",
        "access_key": "test_access_key",
        "access_key_secret": "test_access_key_secret",
    },
    "start_date": "2024-01-01T00:00:00Z",
}

_OAUTH_CONFIG = {
    "credentials": {
        "auth_type": "OAuth2.0",
        "client_id": "test_client_id",
        "client_secret": "test_client_secret",
        "refresh_token": "test_refresh_token",
    },
    "start_date": "2024-01-01T00:00:00Z",
}


def _api_key_config() -> dict:
    """Return a fresh copy of the API Key config so tests cannot mutate each other."""
    return copy.deepcopy(_API_KEY_CONFIG)


def _oauth_config() -> dict:
    """Return a fresh copy of the OAuth config so tests cannot mutate each other.

    The CDK's OAuth authenticator mutates the config in place (writing `access_token` and
    `token_expiry_date` back to `credentials`), so sharing a single config dict across
    tests leaks state and can cause spec validation to fail on later tests.
    """
    return copy.deepcopy(_OAUTH_CONFIG)


def _public_call(call_id: str) -> dict:
    return {
        "id": call_id,
        "url": f"https://us-20768.app.gong.io/call?id={call_id}",
        "title": f"Public call {call_id}",
        "scheduled": "2024-01-02T10:00:00Z",
        "started": "2024-01-02T10:00:00Z",
        "duration": 120,
        "primaryUserId": "1",
        "direction": "Inbound",
        "system": "Gong",
        "scope": "Internal",
        "media": "Video",
        "language": "eng",
        "workspaceId": "ws-1",
        "isPrivate": False,
    }


def _private_call(call_id: str) -> dict:
    return {**_public_call(call_id), "title": f"Private call {call_id}", "isPrivate": True}


def _public_extensive_call(call_id: str) -> dict:
    return {
        "metaData": {
            "id": call_id,
            "url": f"https://us-20768.app.gong.io/call?id={call_id}",
            "title": f"Public extensive call {call_id}",
            "scheduled": "2024-01-02T10:00:00Z",
            "started": "2024-01-02T10:00:00Z",
            "duration": 120,
            "direction": "Inbound",
            "isPrivate": False,
        },
    }


def _private_extensive_call(call_id: str) -> dict:
    call = _public_extensive_call(call_id)
    call["metaData"]["title"] = f"Private extensive call {call_id}"
    call["metaData"]["isPrivate"] = True
    return call


def _sync(stream_name: str, config: dict):
    source = get_source(config=config)
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    return read(source, config, catalog)


def test_calls_stream_drops_private_calls_under_oauth():
    """Under OAuth 2.0 auth, `calls` filters out records where `isPrivate` is `true`."""
    response = {
        "calls": [
            _public_call("public-1"),
            _private_call("private-1"),
            _public_call("public-2"),
            _private_call("private-2"),
        ],
        "records": {"totalRecords": 4, "currentPageSize": 4, "currentPageNumber": 0},
    }

    with requests_mock.Mocker() as mocker:
        mocker.post("https://app.gong.io/oauth2/generate-customer-token", json={"access_token": "t", "expires_in": 3600})
        mocker.get("https://api.gong.io/v2/calls", json=response)
        output = _sync("calls", _oauth_config())

    emitted_ids = [record.record.data["id"] for record in output.records]
    assert emitted_ids == ["public-1", "public-2"], f"expected only public calls under OAuth, got {emitted_ids}"


def test_calls_stream_keeps_private_calls_under_api_key():
    """Under API Key auth, the `isPrivate` filter is not applied — all calls pass through."""
    response = {
        "calls": [
            _public_call("public-1"),
            _private_call("private-1"),
            _public_call("public-2"),
            _private_call("private-2"),
        ],
        "records": {"totalRecords": 4, "currentPageSize": 4, "currentPageNumber": 0},
    }

    with requests_mock.Mocker() as mocker:
        mocker.get("https://api.gong.io/v2/calls", json=response)
        output = _sync("calls", _api_key_config())

    emitted_ids = [record.record.data["id"] for record in output.records]
    assert emitted_ids == [
        "public-1",
        "private-1",
        "public-2",
        "private-2",
    ], f"expected every call to be emitted under API Key auth, got {emitted_ids}"


def test_extensive_calls_stream_drops_private_calls_under_oauth():
    """Under OAuth 2.0, `extensiveCalls` filters out records where `metaData.isPrivate` is `true`."""
    response = {
        "calls": [
            _public_extensive_call("public-1"),
            _private_extensive_call("private-1"),
            _public_extensive_call("public-2"),
            _private_extensive_call("private-2"),
        ],
        "records": {"totalRecords": 4, "currentPageSize": 4, "currentPageNumber": 0},
    }

    with requests_mock.Mocker() as mocker:
        mocker.post("https://app.gong.io/oauth2/generate-customer-token", json={"access_token": "t", "expires_in": 3600})
        mocker.post("https://api.gong.io/v2/calls/extensive", json=response)
        output = _sync("extensiveCalls", _oauth_config())

    emitted_ids = [record.record.data["metaData"]["id"] for record in output.records]
    assert emitted_ids == ["public-1", "public-2"], f"expected only public extensive calls under OAuth, got {emitted_ids}"


def test_extensive_calls_stream_keeps_private_calls_under_api_key():
    """Under API Key auth, `extensiveCalls` emits every record including private ones."""
    response = {
        "calls": [
            _public_extensive_call("public-1"),
            _private_extensive_call("private-1"),
        ],
        "records": {"totalRecords": 2, "currentPageSize": 2, "currentPageNumber": 0},
    }

    with requests_mock.Mocker() as mocker:
        mocker.post("https://api.gong.io/v2/calls/extensive", json=response)
        output = _sync("extensiveCalls", _api_key_config())

    emitted_ids = [record.record.data["metaData"]["id"] for record in output.records]
    assert emitted_ids == [
        "public-1",
        "private-1",
    ], f"expected every extensive call to be emitted under API Key auth, got {emitted_ids}"


def test_calls_stream_emits_no_records_when_all_private_under_oauth():
    """Under OAuth 2.0, when every call has `isPrivate: true` the stream emits nothing."""
    response = {
        "calls": [_private_call("private-1"), _private_call("private-2")],
        "records": {"totalRecords": 2, "currentPageSize": 2, "currentPageNumber": 0},
    }

    with requests_mock.Mocker() as mocker:
        mocker.post("https://app.gong.io/oauth2/generate-customer-token", json={"access_token": "t", "expires_in": 3600})
        mocker.get("https://api.gong.io/v2/calls", json=response)
        output = _sync("calls", _oauth_config())

    assert (
        output.records == []
    ), f"expected zero emitted records under OAuth when all source records are private, got {[r.record.data['id'] for r in output.records]}"
