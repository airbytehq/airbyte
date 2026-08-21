#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#
import base64
from urllib.parse import parse_qs

from airbyte_cdk.models import SyncMode, Type
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


def test_child_cursor_pagination_suppresses_parent_filter(requests_mock, get_source):
    _register_token(requests_mock)
    parent_requests = []
    interview_requests = []

    def applications_callback(request, context):
        parent_requests.append(request)
        context.status_code = 200
        return [{"id": 42, "created_at": "2024-01-01T00:00:00.000Z"}]

    def interviews_callback(request, context):
        interview_requests.append(request)
        if len(interview_requests) == 1:
            assert request.qs == {
                "per_page": ["500"],
                "updated_at": ["gte|1970-01-01t00:00:00.000z"],
                "application_ids": ["42"],
            }
            context.status_code = 200
            context.headers["Link"] = '<https://harvest.greenhouse.io/v3/interviews?cursor=cursor-2>; rel="next"'
            return [{"id": 1, "updated_at": "2024-01-01T00:00:00.000Z"}]

        assert parse_qs(request.query) == {"cursor": ["cursor-2"]}
        context.status_code = 200
        return [{"id": 2, "updated_at": "2024-01-02T00:00:00.000Z"}]

    requests_mock.get("https://harvest.greenhouse.io/v3/applications", json=applications_callback)
    requests_mock.get("https://harvest.greenhouse.io/v3/interviews", json=interviews_callback)

    source = get_source(CONFIG)
    catalog = CatalogBuilder().with_stream("applications_interviews", SyncMode.incremental).build()
    output = read(source, config=CONFIG, catalog=catalog)

    assert [record.record.data["id"] for record in output.records] == [1, 2]
    assert len(parent_requests) == 1
    assert len(interview_requests) == 2


def test_manifest_child_state_migration_reaches_parent_request(requests_mock, get_source):
    _register_token(requests_mock)
    parent_requests = []
    interview_requests = []

    def applications_callback(request, context):
        parent_requests.append(request)
        context.status_code = 200
        return [{"id": 42, "created_at": "2024-01-01T00:00:00.000Z"}]

    def interviews_callback(request, context):
        interview_requests.append(request)
        context.status_code = 200
        return [{"id": 1, "updated_at": "2024-01-01T00:00:00.000Z"}]

    requests_mock.get("https://harvest.greenhouse.io/v3/applications", json=applications_callback)
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

    assert interview_requests[0].qs["application_ids"] == ["42"]
    assert parent_requests[0].qs["updated_at"] == ["gte|2024-01-01t00:00:00.000z"]
