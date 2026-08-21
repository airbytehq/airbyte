#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#
import base64
from urllib.parse import parse_qs

import pytest

from airbyte_cdk.models import FailureType, SyncMode, Type
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder


CONFIG = {
    "credentials": {
        "auth_type": "Client",
        "client_id": "test-client",
        "client_secret": "test-secret",
        "refresh_token": "test-refresh-token",
    }
}


def _register_token(requests_mock):
    token_requests = []

    def token_callback(request, context):
        token_requests.append(request)
        context.status_code = 200
        return {
            "access_token": "access-token",
            "expires_at": "2030-01-01T00:00:00+0000",
            "refresh_token": "rotated-refresh-token",
        }

    requests_mock.post("https://auth.greenhouse.io/token", json=token_callback)
    return token_requests


def test_applications_cursor_pagination_uses_cursor_only_follow_up(requests_mock, get_source):
    token_requests = _register_token(requests_mock)
    application_requests = []

    def applications_callback(request, context):
        application_requests.append(request)
        if len(application_requests) == 1:
            assert request.qs == {
                "per_page": ["500"],
                "updated_at": ["gte|1970-01-01t00:00:00.000z"],
            }
            context.status_code = 200
            context.headers["Link"] = '<https://harvest.greenhouse.io/v3/applications?cursor=cursor-2>; rel="next"'
            return [{"id": 1, "created_at": "2024-01-01T00:00:00.000Z"}]

        assert parse_qs(request.query) == {"cursor": ["cursor-2"]}
        context.status_code = 200
        return [{"id": 2, "created_at": "2024-01-02T00:00:00.000Z"}]

    requests_mock.get("https://harvest.greenhouse.io/v3/applications", json=applications_callback)

    source = get_source(CONFIG)
    catalog = CatalogBuilder().with_stream("applications", SyncMode.incremental).build()
    output = read(source, config=CONFIG, catalog=catalog)

    assert [record.record.data["id"] for record in output.records] == [1, 2]
    assert len(application_requests) == 2
    assert len(token_requests) == 1


def test_applications_retries_429_and_completes(requests_mock, get_source):
    _register_token(requests_mock)
    application_requests = []

    def applications_callback(request, context):
        application_requests.append(request)
        if len(application_requests) == 1:
            context.status_code = 429
            context.headers["X-RateLimit-Remaining"] = "0"
            context.headers["Retry-After"] = "1"
            return {"message": "Too Many Requests"}
        context.status_code = 200
        context.headers["X-RateLimit-Remaining"] = "50"
        return [
            {
                "id": 1,
                "created_at": "2024-01-01T00:00:00.000Z",
                "updated_at": "2024-01-01T00:00:00.000Z",
            }
        ]

    requests_mock.get("https://harvest.greenhouse.io/v3/applications", json=applications_callback)

    source = get_source(CONFIG)
    catalog = CatalogBuilder().with_stream("applications", SyncMode.incremental).build()
    output = read(source, config=CONFIG, catalog=catalog)

    assert [record.record.data["id"] for record in output.records] == [1]
    assert len(application_requests) == 2


def test_applications_429_waits_for_retry_after(requests_mock, get_source, monkeypatch):
    waits = []
    monkeypatch.setattr(
        "airbyte_cdk.sources.streams.http.rate_limiting.time.sleep",
        lambda seconds: waits.append(seconds),
    )
    _register_token(requests_mock)
    application_requests = []

    def applications_callback(request, context):
        application_requests.append(request)
        if len(application_requests) == 1:
            context.status_code = 429
            context.headers["X-RateLimit-Remaining"] = "0"
            context.headers["Retry-After"] = "1"
            return {"message": "Too Many Requests"}
        context.status_code = 200
        context.headers["X-RateLimit-Remaining"] = "50"
        return [{"id": 1, "updated_at": "2024-01-01T00:00:00.000Z"}]

    requests_mock.get("https://harvest.greenhouse.io/v3/applications", json=applications_callback)

    source = get_source(CONFIG)
    catalog = CatalogBuilder().with_stream("applications", SyncMode.incremental).build()
    output = read(source, config=CONFIG, catalog=catalog)

    assert not output.errors
    assert waits
    assert waits[0] == pytest.approx(2)


def test_shared_error_handler_surfaces_403_as_config_error(requests_mock, get_source):
    _register_token(requests_mock)
    requests_mock.get(
        "https://harvest.greenhouse.io/v3/offices",
        status_code=403,
        json={"message": "Forbidden"},
    )

    source = get_source(CONFIG)
    catalog = CatalogBuilder().with_stream("offices", SyncMode.full_refresh).build()
    output = read(source, config=CONFIG, catalog=catalog, expecting_exception=True)

    assert output.errors
    assert all(trace.trace.error.failure_type == FailureType.config_error for trace in output.errors)
    assert any("Site Admin" in trace.trace.error.message for trace in output.errors)
    assert any("harvest:<resource>:list" in trace.trace.error.message for trace in output.errors)


def test_custom_field_options_stream_is_unfiltered_and_paginated(requests_mock, get_source):
    _register_token(requests_mock)
    option_requests = []

    def options_callback(request, context):
        option_requests.append(request)
        if len(option_requests) == 1:
            assert request.qs == {"per_page": ["500"]}
            context.status_code = 200
            context.headers["Link"] = '<https://harvest.greenhouse.io/v3/custom_field_options?cursor=cursor-2>; rel="next"'
            return [{"id": 1, "custom_field_id": 10, "name": "Full-time"}]

        assert parse_qs(request.query) == {"cursor": ["cursor-2"]}
        context.status_code = 200
        return [{"id": 2, "custom_field_id": 10, "name": "Part-time"}]

    requests_mock.get("https://harvest.greenhouse.io/v3/custom_field_options", json=options_callback)

    source = get_source(CONFIG)
    catalog = CatalogBuilder().with_stream("custom_field_options", SyncMode.full_refresh).build()
    output = read(source, config=CONFIG, catalog=catalog)

    assert [record.record.data["id"] for record in output.records] == [1, 2]
    assert len(option_requests) == 2


def test_oauth_refresh_token_request_shape(requests_mock, get_source):
    token_requests = _register_token(requests_mock)
    requests_mock.get(
        "https://harvest.greenhouse.io/v3/applications",
        json=[{"id": 1, "created_at": "2024-01-01T00:00:00.000Z"}],
    )

    source = get_source(CONFIG)
    catalog = CatalogBuilder().with_stream("applications", SyncMode.incremental).build()
    read(source, config=CONFIG, catalog=catalog)

    request = token_requests[0]
    assert request.headers["Authorization"] == "Basic " + base64.b64encode(b"test-client:test-secret").decode()
    token_params = parse_qs(request.query)
    assert token_params["grant_type"] == ["refresh_token"]
    assert token_params["refresh_token"] == ["test-refresh-token"]
    assert "sub" not in token_params


def test_oauth_rotated_refresh_token_is_persisted(requests_mock, get_source):
    _register_token(requests_mock)
    requests_mock.get(
        "https://harvest.greenhouse.io/v3/applications",
        json=[{"id": 1, "created_at": "2024-01-01T00:00:00.000Z"}],
    )

    source = get_source(CONFIG)
    catalog = CatalogBuilder().with_stream("applications", SyncMode.incremental).build()
    output = read(source, config=CONFIG, catalog=catalog)

    control_messages = output.get_message_by_types([Type.CONTROL])
    assert control_messages, "expected a CONNECTOR_CONFIG control message persisting the rotated refresh token"
    updated_credentials = control_messages[-1].control.connectorConfig.config["credentials"]
    assert updated_credentials["refresh_token"] == "rotated-refresh-token"
    assert updated_credentials["access_token"] == "access-token"
    assert updated_credentials["token_expiry_date"]


def test_manifest_application_state_migration_reaches_request(requests_mock, get_source):
    _register_token(requests_mock)
    application_requests = []

    def applications_callback(request, context):
        application_requests.append(request)
        context.status_code = 200
        return [
            {
                "id": 1,
                "created_at": "2024-01-01T00:00:00.000Z",
                "updated_at": "2024-01-01T00:00:00.000Z",
            }
        ]

    requests_mock.get("https://harvest.greenhouse.io/v3/applications", json=applications_callback)

    state = (
        StateBuilder()
        .with_stream_state(
            "applications",
            {"applied_at": "2024-01-01T00:00:00.000Z"},
        )
        .build()
    )
    source = get_source(CONFIG, state=state)
    catalog = CatalogBuilder().with_stream("applications", SyncMode.incremental).build()
    output = read(source, config=CONFIG, catalog=catalog)

    assert application_requests[0].qs["updated_at"] == ["gte|1970-01-01t00:00:00.000z"]
    assert not output.errors
    assert [record.record.data["id"] for record in output.records] == [1]
    assert vars(output.most_recent_state.stream_state) == {"updated_at": "2024-01-01T00:00:00.000Z"}


def test_flat_child_cursor_pagination_uses_cursor_only_follow_up(requests_mock, get_source):
    _register_token(requests_mock)
    interview_requests = []

    def interviews_callback(request, context):
        interview_requests.append(request)
        if len(interview_requests) == 1:
            assert request.qs == {
                "per_page": ["500"],
                "updated_at": ["gte|1970-01-01t00:00:00.000z"],
            }
            context.status_code = 200
            context.headers["Link"] = '<https://harvest.greenhouse.io/v3/interviews?cursor=cursor-2>; rel="next"'
            return [{"id": 1, "updated_at": "2024-01-01T00:00:00.000Z"}]

        assert parse_qs(request.query) == {"cursor": ["cursor-2"]}
        context.status_code = 200
        return [{"id": 2, "updated_at": "2024-01-02T00:00:00.000Z"}]

    requests_mock.get("https://harvest.greenhouse.io/v3/interviews", json=interviews_callback)

    source = get_source(CONFIG)
    catalog = CatalogBuilder().with_stream("applications_interviews", SyncMode.incremental).build()
    output = read(source, config=CONFIG, catalog=catalog)

    assert [record.record.data["id"] for record in output.records] == [1, 2]
    assert len(interview_requests) == 2


def test_manifest_flat_child_state_migration_reaches_request(requests_mock, get_source):
    _register_token(requests_mock)
    interview_requests = []

    def interviews_callback(request, context):
        interview_requests.append(request)
        context.status_code = 200
        return [{"id": 1, "updated_at": "2024-01-01T00:00:00.000Z"}]

    requests_mock.get("https://harvest.greenhouse.io/v3/interviews", json=interviews_callback)

    state = (
        StateBuilder()
        .with_stream_state(
            "applications_interviews",
            {
                "states": [
                    {
                        "partition": {"application_id": 42},
                        "cursor": {"updated_at": "2024-01-01T00:00:00.000Z"},
                    }
                ],
                "parent_state": {"applications": {"applied_at": "2024-01-01T00:00:00.000Z"}},
            },
        )
        .build()
    )
    source = get_source(CONFIG, state=state)
    catalog = CatalogBuilder().with_stream("applications_interviews", SyncMode.incremental).build()
    read(source, config=CONFIG, catalog=catalog)

    assert interview_requests[0].qs == {
        "per_page": ["500"],
        "updated_at": ["gte|2024-01-01t00:00:00.000z"],
    }


def test_users_include_service_accounts_only_on_first_page(requests_mock, get_source):
    _register_token(requests_mock)
    user_requests = []

    def users_callback(request, context):
        user_requests.append(request)
        context.status_code = 200
        if len(user_requests) == 1:
            context.headers["Link"] = (
                '<https://harvest.greenhouse.io/v3/users?cursor=cursor-2>; rel="next"'
            )
        return [{"id": len(user_requests), "updated_at": "2024-01-01T00:00:00.000Z"}]

    requests_mock.get("https://harvest.greenhouse.io/v3/users", json=users_callback)

    source = get_source(CONFIG)
    catalog = CatalogBuilder().with_stream("users", SyncMode.incremental).build()
    output = read(source, config=CONFIG, catalog=catalog)

    assert not output.errors
    assert len(user_requests) == 2
    assert user_requests[0].qs == {
        "per_page": ["500"],
        "updated_at": ["gte|1970-01-01t00:00:00.000z"],
        "show_service_accounts": ["true"],
    }
    assert user_requests[1].qs == {"cursor": ["cursor-2"]}


def test_activity_feed_reads_notes_for_candidate_and_uses_note_id(
    requests_mock, get_source
):
    _register_token(requests_mock)
    candidate_requests = []
    note_requests = []

    def candidates_callback(request, context):
        candidate_requests.append(request)
        context.status_code = 200
        return [{"id": 42, "updated_at": "2024-01-01T00:00:00.000Z"}]

    def notes_callback(request, context):
        note_requests.append(request)
        context.status_code = 200
        return [
            {
                "id": 101,
                "candidate_id": 42,
                "application_id": None,
                "body": "Candidate contacted",
                "type": "NOTE",
            }
        ]

    requests_mock.get("https://harvest.greenhouse.io/v3/candidates", json=candidates_callback)
    requests_mock.get("https://harvest.greenhouse.io/v3/notes", json=notes_callback)

    source = get_source(CONFIG)
    catalog = CatalogBuilder().with_stream("activity_feed", SyncMode.full_refresh).build()
    output = read(source, config=CONFIG, catalog=catalog)

    assert not output.errors
    assert candidate_requests
    assert len(note_requests) == 1
    assert note_requests[0].qs == {"per_page": ["500"], "candidate_ids": ["42"]}
    assert [record.record.data["id"] for record in output.records] == [101]
    assert output.records[0].record.data["candidate_id"] == 42


@pytest.mark.parametrize(
    "status_code, message",
    [
        (400, "Bad Request Params"),
        (401, "Unauthorized"),
    ],
)
def test_oauth_refresh_failure_surfaces_reauthenticate_config_error(
    status_code, message, requests_mock, get_source
):
    def token_callback(request, context):
        context.status_code = status_code
        return {
            "message": message,
            "errors": [
                "Refresh token expired at 2026-01-01T00:00:00Z. The user must re-authorize consent"
            ],
        }

    requests_mock.post("https://auth.greenhouse.io/token", json=token_callback)

    source = get_source(CONFIG)
    catalog = CatalogBuilder().with_stream("applications", SyncMode.incremental).build()
    output = read(source, config=CONFIG, catalog=catalog, expecting_exception=True)

    messages = [trace.trace.error.message for trace in output.errors]
    assert any("Please re-authenticate" in text for text in messages), messages
    assert all(
        trace.trace.error.failure_type == FailureType.config_error for trace in output.errors
    ), [
        (trace.trace.error.failure_type, trace.trace.error.message)
        for trace in output.errors
    ]
