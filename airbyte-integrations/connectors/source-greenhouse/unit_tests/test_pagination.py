#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#
import base64
import datetime
from unittest.mock import patch
from urllib.parse import parse_qs

import pytest
import yaml
from jsonschema import validate

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
CONFIG_WITH_EPOCH_START_DATE = {**CONFIG, "start_date": "1970-01-01T00:00:00Z"}
CONFIG_WITH_LATER_START_DATE = {**CONFIG, "start_date": "2025-01-01T00:00:00Z"}
CURSOR_NOW = datetime.datetime(2026, 8, 27, tzinfo=datetime.timezone.utc)


def _freeze_cursor_time():
    return patch(
        "airbyte_cdk.sources.streams.concurrent.state_converters.datetime_stream_state_converter.ab_datetime_now",
        return_value=CURSOR_NOW,
    )


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
                "updated_at": ["gte|1970-01-01t00:00:00.000z|lte|2026-08-27t00:00:00.000z"],
            }
            context.status_code = 200
            context.headers["Link"] = '<https://harvest.greenhouse.io/v3/applications?cursor=cursor-2>; rel="next"'
            return [{"id": 1, "created_at": "2024-01-01T00:00:00.000Z"}]

        assert parse_qs(request.query) == {"cursor": ["cursor-2"]}
        context.status_code = 200
        return [{"id": 2, "created_at": "2024-01-02T00:00:00.000Z"}]

    requests_mock.get("https://harvest.greenhouse.io/v3/applications", json=applications_callback)

    source = get_source(CONFIG_WITH_EPOCH_START_DATE)
    catalog = CatalogBuilder().with_stream("applications", SyncMode.incremental).build()
    with _freeze_cursor_time():
        output = read(source, config=CONFIG_WITH_EPOCH_START_DATE, catalog=catalog)

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
            context.headers["X-RateLimit-Reset"] = "0"
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


def test_applications_cursor_pagination_crosses_two_follow_up_boundaries(requests_mock, get_source):
    _register_token(requests_mock)
    application_requests = []

    def applications_callback(request, context):
        application_requests.append(request)
        if len(application_requests) == 1:
            assert request.qs == {
                "per_page": ["500"],
                "updated_at": ["gte|1970-01-01t00:00:00.000z|lte|2026-08-27t00:00:00.000z"],
            }
            context.status_code = 200
            context.headers["Link"] = '<https://harvest.greenhouse.io/v3/applications?cursor=cursor-2>; rel="next"'
            return [{"id": 1, "created_at": "2024-01-01T00:00:00.000Z"}]
        if len(application_requests) == 2:
            assert parse_qs(request.query) == {"cursor": ["cursor-2"]}
            context.status_code = 200
            context.headers["Link"] = '<https://harvest.greenhouse.io/v3/applications?cursor=cursor-3>; rel="next"'
            return [{"id": 2, "created_at": "2024-01-02T00:00:00.000Z"}]

        assert parse_qs(request.query) == {"cursor": ["cursor-3"]}
        context.status_code = 200
        return [{"id": 3, "created_at": "2024-01-03T00:00:00.000Z"}]

    requests_mock.get("https://harvest.greenhouse.io/v3/applications", json=applications_callback)

    source = get_source(CONFIG_WITH_EPOCH_START_DATE)
    catalog = CatalogBuilder().with_stream("applications", SyncMode.incremental).build()
    with _freeze_cursor_time():
        output = read(source, config=CONFIG_WITH_EPOCH_START_DATE, catalog=catalog)

    assert not output.errors
    assert [record.record.data["id"] for record in output.records] == [1, 2, 3]
    assert len(application_requests) == 3


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
            context.headers["X-RateLimit-Reset"] = "0"
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


def test_applications_refreshes_token_on_401(requests_mock, get_source):
    token_requests = []

    def token_callback(request, context):
        token_requests.append(request)
        context.status_code = 200
        return {
            "access_token": f"token-{len(token_requests)}",
            "expires_at": "2030-01-01T00:00:00+0000",
            "refresh_token": f"refresh-token-{len(token_requests)}",
        }

    application_requests = []

    def applications_callback(request, context):
        application_requests.append(request)
        if request.headers["Authorization"] == "Bearer token-1":
            context.status_code = 401
            return {"message": "Unauthorized"}
        context.status_code = 200
        return [{"id": 1, "updated_at": "2024-01-01T00:00:00.000Z"}]

    requests_mock.post("https://auth.greenhouse.io/token", json=token_callback)
    requests_mock.get("https://harvest.greenhouse.io/v3/applications", json=applications_callback)

    source = get_source(CONFIG)
    catalog = CatalogBuilder().with_stream("applications", SyncMode.incremental).build()
    output = read(source, config=CONFIG, catalog=catalog)

    assert len(token_requests) == 2
    assert len(application_requests) == 2
    assert application_requests[1].headers["Authorization"] == "Bearer token-2"
    assert not output.errors
    assert [record.record.data["id"] for record in output.records] == [1]


@pytest.mark.parametrize("stream_name", ["offices", "users"])
def test_shared_error_handler_surfaces_403_as_config_error(requests_mock, get_source, stream_name):
    _register_token(requests_mock)
    requests_mock.get(
        f"https://harvest.greenhouse.io/v3/{stream_name}",
        status_code=403,
        json={"message": "Forbidden"},
    )

    source = get_source(CONFIG)
    sync_mode = SyncMode.incremental if stream_name == "users" else SyncMode.full_refresh
    catalog = CatalogBuilder().with_stream(stream_name, sync_mode).build()
    output = read(source, config=CONFIG, catalog=catalog, expecting_exception=True)

    assert output.errors
    assert all(trace.trace.error.failure_type == FailureType.config_error for trace in output.errors)


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


@pytest.mark.parametrize(
    "stream_name, custom_field_key",
    [
        ("degrees", "degree"),
        ("disciplines", "discipline"),
        ("schools", "school_name"),
    ],
)
def test_custom_field_option_streams_filter_on_first_page_only(requests_mock, get_source, stream_name, custom_field_key):
    _register_token(requests_mock)
    option_requests = []

    def options_callback(request, context):
        option_requests.append(request)
        context.status_code = 200
        if len(option_requests) == 1:
            assert request.qs == {"per_page": ["500"], "custom_field_key": [custom_field_key]}
            context.headers["Link"] = '<https://harvest.greenhouse.io/v3/custom_field_options?cursor=cursor-2>; rel="next"'
            return [{"id": 1, "custom_field_id": 10, "name": "Bachelor's Degree"}]

        assert parse_qs(request.query) == {"cursor": ["cursor-2"]}
        return [{"id": 2, "custom_field_id": 10, "name": "Master's Degree"}]

    requests_mock.get("https://harvest.greenhouse.io/v3/custom_field_options", json=options_callback)

    source = get_source(CONFIG)
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    output = read(source, config=CONFIG, catalog=catalog)

    assert not output.errors
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
    assert request.headers["Content-Type"] == "application/x-www-form-urlencoded"
    assert request.query == "", "Refresh args must not be on the query string because Greenhouse reads them from the body"
    token_params = parse_qs(request.text)
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


def _read_application_start_date_request(requests_mock, get_source, config):
    _register_token(requests_mock)
    application_requests = []

    def applications_callback(request, context):
        application_requests.append(request)
        context.status_code = 200
        return [{"id": 1, "created_at": "2024-01-01T00:00:00.000Z"}]

    requests_mock.get("https://harvest.greenhouse.io/v3/applications", json=applications_callback)

    source = get_source(config)
    catalog = CatalogBuilder().with_stream("applications", SyncMode.incremental).build()
    with _freeze_cursor_time():
        read(source, config=config, catalog=catalog)
    return application_requests[0]


def test_start_date_defaults_to_epoch(requests_mock, get_source):
    request = _read_application_start_date_request(requests_mock, get_source, CONFIG)

    assert request.qs["updated_at"] == ["gte|1970-01-01t00:00:00.000z|lte|2026-08-27t00:00:00.000z"]


def test_start_date_uses_configured_value(requests_mock, get_source):
    request = _read_application_start_date_request(
        requests_mock,
        get_source,
        {**CONFIG, "start_date": "2025-01-01T00:00:00Z"},
    )

    assert request.qs["updated_at"] == ["gte|2025-01-01t00:00:00.000z|lte|2026-08-27t00:00:00.000z"]


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
    source = get_source(CONFIG_WITH_EPOCH_START_DATE, state=state)
    catalog = CatalogBuilder().with_stream("applications", SyncMode.incremental).build()
    with _freeze_cursor_time():
        output = read(source, config=CONFIG_WITH_EPOCH_START_DATE, catalog=catalog)

    assert application_requests[0].qs["updated_at"] == ["gte|1970-01-01t00:00:00.000z|lte|2026-08-27t00:00:00.000z"]
    assert not output.errors
    assert [record.record.data["id"] for record in output.records] == [1]
    assert vars(output.most_recent_state.stream_state) == {"updated_at": "2024-01-01T00:00:00.000Z"}


def test_top_level_interviews_cursor_pagination_uses_cursor_only_follow_up(requests_mock, get_source):
    _register_token(requests_mock)
    interview_requests = []

    def interviews_callback(request, context):
        interview_requests.append(request)
        if len(interview_requests) == 1:
            assert request.qs == {
                "per_page": ["500"],
                "updated_at": ["gte|1970-01-01t00:00:00.000z|lte|2026-08-27t00:00:00.000z"],
            }
            context.status_code = 200
            context.headers["Link"] = '<https://harvest.greenhouse.io/v3/interviews?cursor=cursor-2>; rel="next"'
            return [{"id": 1, "updated_at": "2024-01-01T00:00:00.000Z"}]

        assert parse_qs(request.query) == {"cursor": ["cursor-2"]}
        context.status_code = 200
        return [{"id": 2, "updated_at": "2024-01-02T00:00:00.000Z"}]

    requests_mock.get("https://harvest.greenhouse.io/v3/interviews", json=interviews_callback)

    source = get_source(CONFIG_WITH_EPOCH_START_DATE)
    catalog = CatalogBuilder().with_stream("interviews", SyncMode.incremental).build()
    with _freeze_cursor_time():
        output = read(source, config=CONFIG_WITH_EPOCH_START_DATE, catalog=catalog)

    assert [record.record.data["id"] for record in output.records] == [1, 2]
    assert len(interview_requests) == 2


def test_users_include_service_accounts_only_on_first_page(requests_mock, get_source):
    _register_token(requests_mock)
    user_requests = []

    def users_callback(request, context):
        user_requests.append(request)
        context.status_code = 200
        if len(user_requests) == 1:
            context.headers["Link"] = '<https://harvest.greenhouse.io/v3/users?cursor=cursor-2>; rel="next"'
        return [{"id": len(user_requests), "updated_at": "2024-01-01T00:00:00.000Z"}]

    requests_mock.get("https://harvest.greenhouse.io/v3/users", json=users_callback)

    source = get_source(CONFIG_WITH_EPOCH_START_DATE)
    catalog = CatalogBuilder().with_stream("users", SyncMode.incremental).build()
    with _freeze_cursor_time():
        output = read(source, config=CONFIG_WITH_EPOCH_START_DATE, catalog=catalog)

    assert not output.errors
    assert len(user_requests) == 2
    assert user_requests[0].qs == {
        "per_page": ["500"],
        "updated_at": ["gte|1970-01-01t00:00:00.000z|lte|2026-08-27t00:00:00.000z"],
        "show_service_accounts": ["true"],
    }
    assert user_requests[1].qs == {"cursor": ["cursor-2"]}


def test_activity_feed_reads_notes_for_candidate_and_uses_note_id(requests_mock, get_source):
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


def test_grouped_substreams_batch_parent_ids_at_the_50_id_api_cap(requests_mock, get_source):
    """Greenhouse caps every *_ids filter at maxItems: 50, so GroupingPartitionRouter must comma-join parents in batches of at most 50 and issue one request per batch."""
    _register_token(requests_mock)
    note_requests = []

    def candidates_callback(request, context):
        context.status_code = 200
        return [{"id": candidate_id, "updated_at": "2024-01-01T00:00:00.000Z"} for candidate_id in range(1, 52)]

    def notes_callback(request, context):
        note_requests.append(request)
        context.status_code = 200
        return [{"id": 100 + len(note_requests), "candidate_id": 1, "type": "NOTE"}]

    requests_mock.get("https://harvest.greenhouse.io/v3/candidates", json=candidates_callback)
    requests_mock.get("https://harvest.greenhouse.io/v3/notes", json=notes_callback)

    source = get_source(CONFIG)
    catalog = CatalogBuilder().with_stream("activity_feed", SyncMode.full_refresh).build()
    output = read(source, config=CONFIG, catalog=catalog)

    assert not output.errors
    assert len(note_requests) == 2, "51 candidates must be split into two <=50-id batches"
    assert note_requests[0].qs["candidate_ids"] == [",".join(str(i) for i in range(1, 51))]
    assert note_requests[1].qs["candidate_ids"] == ["51"]
    for request in note_requests:
        assert len(request.qs["candidate_ids"][0].split(",")) <= 50


@pytest.mark.parametrize(
    "substream, parent_stream, parent_url, child_url",
    [
        ("jobs_openings", "jobs", "https://harvest.greenhouse.io/v3/jobs", "https://harvest.greenhouse.io/v3/openings"),
        ("activity_feed", "candidates", "https://harvest.greenhouse.io/v3/candidates", "https://harvest.greenhouse.io/v3/notes"),
        (
            "user_permissions",
            "users",
            "https://harvest.greenhouse.io/v3/users",
            "https://harvest.greenhouse.io/v3/user_job_permissions",
        ),
    ],
)
def test_substream_parents_ignore_start_date_while_standalone_parents_use_it(
    requests_mock, get_source, substream, parent_stream, parent_url, child_url
):
    _register_token(requests_mock)
    parent_requests = []

    def parent_callback(request, context):
        parent_requests.append(request)
        context.status_code = 200
        return [{"id": 1, "updated_at": "2024-01-01T00:00:00.000Z"}]

    requests_mock.get(parent_url, json=parent_callback)
    requests_mock.get(child_url, json=[])

    source = get_source(CONFIG_WITH_LATER_START_DATE)
    catalog = CatalogBuilder().with_stream(substream, SyncMode.full_refresh).build()
    with _freeze_cursor_time():
        output = read(source, config=CONFIG_WITH_LATER_START_DATE, catalog=catalog)

    assert not output.errors
    assert parent_requests[0].qs["updated_at"] == ["gte|1970-01-01t00:00:00.000z|lte|2026-08-27t00:00:00.000z"]

    source = get_source(CONFIG_WITH_LATER_START_DATE)
    catalog = CatalogBuilder().with_stream(parent_stream, SyncMode.incremental).build()
    with _freeze_cursor_time():
        output = read(source, config=CONFIG_WITH_LATER_START_DATE, catalog=catalog)

    assert not output.errors
    assert parent_requests[1].qs["updated_at"] == ["gte|2025-01-01t00:00:00.000z|lte|2026-08-27t00:00:00.000z"]


def test_documented_v3_examples_validate_against_stream_schemas(connector_path):
    with open(connector_path / "manifest.yaml") as manifest_file:
        manifest = yaml.safe_load(manifest_file)

    documented_examples = {
        "applications": {
            "id": 1,
            "referrer_id": 1,
            "source_id": 1,
            "agency_note_id": 1,
            "recruiter_id": 1,
            "coordinator_id": 1,
            "needs_decision": False,
            "prospect": False,
            "rejected_at": None,
            "created_at": "2024-01-01T12:30:30.000Z",
            "updated_at": "2024-01-01T00:00:00.000Z",
            "last_activity_at": "2024-01-01T00:00:00.000Z",
            "stage_id": 1,
            "job_interview_stage_id": 1,
            "candidate_id": 1,
            "job_id": 1,
            "job_post_id": None,
            "status": "in_process",
            "stage_name": "Application Review",
            "custom_fields": {
                "custom_field_1": {
                    "name": "Custom Field 1",
                    "type": "short_text",
                    "value": "some value",
                }
            },
            "location_address": "455 Broadway St., New York, NY",
            "answers": [{"question": "Simple question", "answer": "some answer"}],
            "prospective_job_ids": [],
        },
        "users": {
            "id": 1,
            "first_name": "Admin",
            "last_name": "User",
            "job_title": None,
            "agency_id": None,
            "created_at": "2024-01-01T00:00:00.000Z",
            "updated_at": "2024-01-01T00:00:00.000Z",
            "primary_email": "bob_johnson727@localhost.com",
            "name": "Admin User",
            "deactivated": False,
            "site_admin": True,
            "employee_id": None,
            "linked_candidate_ids": [],
            "office_ids": [],
            "department_ids": [],
            "interviewer_tags": [],
            "custom_fields": {
                "select_custom_field": {
                    "name": "Select custom field",
                    "type": "single_select",
                    "value": None,
                }
            },
        },
        "activity_feed": {
            "id": 1,
            "body": "Admin-only note",
            "created_at": "2024-01-01T12:30:30.000Z",
            "updated_at": "2024-01-01T12:30:30.000Z",
            "subject": None,
            "user_id": 1,
            "visibility": "admin_only_visible",
            "email_from": None,
            "email_to": None,
            "email_cc": None,
            "import_hash": None,
            "body_with_tags": None,
            "email_attachment_file_names": None,
            "candidate_id": 1,
            "type": "NOTE",
            "application_id": None,
        },
    }

    for stream_name, record in documented_examples.items():
        schema = manifest["schemas"][stream_name]
        validate(record, schema)
        # Full documented-example coverage for every stream is a follow-up.
        undeclared = sorted(set(record) - set(schema["properties"]))
        assert not undeclared, (
            f"{stream_name} schema omits documented v3 fields {undeclared}; "
            "schemas are additionalProperties:true, so validate() alone cannot catch this"
        )


def test_manifest_uses_greenhouse_fixed_window_api_budget(connector_path):
    manifest = yaml.safe_load((connector_path / "manifest.yaml").read_text())

    assert "SelectiveAuthenticator" not in yaml.safe_dump(manifest)
    assert manifest["spec"]["advanced_auth"]["predicate_value"] == "Client"
    authenticator = manifest["definitions"]["base_requester"]["authenticator"]
    assert authenticator["type"] == "OAuthAuthenticator"
    assert authenticator["grant_type"] == "refresh_token"
    assert "refresh_token_updater" in authenticator
    credentials = manifest["spec"]["connection_specification"]["properties"]["credentials"]
    assert len(credentials["oneOf"]) == 1
    credentials_option = credentials["oneOf"][0]
    assert credentials_option["properties"]["auth_type"]["const"] == "Client"
    assert "ClientCredentials" not in yaml.safe_dump(credentials)
    assert "sub" not in yaml.safe_dump(credentials)
    assert manifest["api_budget"]["ratelimit_reset_header"] == "X-RateLimit-Reset"
    assert manifest["api_budget"]["policies"] == [
        {
            "type": "FixedWindowCallRatePolicy",
            "call_limit": 50,
            "period": "PT30S",
            "matchers": [],
        }
    ]


def test_eeoc_uses_submitted_at_filter_and_cursor_only_follow_up(requests_mock, get_source):
    _register_token(requests_mock)
    eeoc_requests = []

    def eeoc_callback(request, context):
        eeoc_requests.append(request)
        context.status_code = 200
        if len(eeoc_requests) == 1:
            context.headers["Link"] = '<https://harvest.greenhouse.io/v3/eeoc?cursor=cursor-2>; rel="next"'
            return [{"application_id": 1, "submitted_at": "2024-01-01T00:00:00.000Z"}]
        return [{"application_id": 2, "submitted_at": "2024-01-02T00:00:00.000Z"}]

    requests_mock.get("https://harvest.greenhouse.io/v3/eeoc", json=eeoc_callback)

    source = get_source(CONFIG_WITH_EPOCH_START_DATE)
    catalog = CatalogBuilder().with_stream("eeoc", SyncMode.incremental).build()
    with _freeze_cursor_time():
        output = read(source, config=CONFIG_WITH_EPOCH_START_DATE, catalog=catalog)

    assert not output.errors
    assert eeoc_requests[0].qs == {
        "per_page": ["500"],
        "submitted_at": ["gte|1970-01-01t00:00:00.000z|lte|2026-08-27t00:00:00.000z"],
    }
    assert parse_qs(eeoc_requests[1].query) == {"cursor": ["cursor-2"]}
    assert [record.record.data["application_id"] for record in output.records] == [1, 2]


def test_email_templates_incremental_stateful_cursor_pagination(requests_mock, get_source):
    _register_token(requests_mock)
    email_template_requests = []

    def email_templates_callback(request, context):
        email_template_requests.append(request)
        context.status_code = 200
        if len(email_template_requests) == 1:
            context.headers["Link"] = '<https://harvest.greenhouse.io/v3/email_templates?cursor=cursor-2>; rel="next"'
            return [{"id": 1, "updated_at": "2026-08-24T12:30:00.000Z"}]
        return [{"id": 2, "updated_at": "2026-08-24T13:00:00.000Z"}]

    requests_mock.get("https://harvest.greenhouse.io/v3/email_templates", json=email_templates_callback)

    state = StateBuilder().with_stream_state("email_templates", {"updated_at": "2026-08-24T12:00:00.000Z"}).build()
    source = get_source(CONFIG_WITH_EPOCH_START_DATE, state=state)
    catalog = CatalogBuilder().with_stream("email_templates", SyncMode.incremental).build()
    with _freeze_cursor_time():
        output = read(source, config=CONFIG_WITH_EPOCH_START_DATE, catalog=catalog)

    assert email_template_requests[0].qs == {
        "per_page": ["500"],
        "updated_at": ["gte|2026-08-24t11:00:00.000z|lte|2026-08-27t00:00:00.000z"],
    }
    assert parse_qs(email_template_requests[1].query) == {"cursor": ["cursor-2"]}
    assert [record.record.data["id"] for record in output.records] == [1, 2]
    assert vars(output.most_recent_state.stream_state) == {"updated_at": "2026-08-24T13:00:00.000Z"}


def test_lookback_window_widens_resume_bound(requests_mock, get_source):
    _register_token(requests_mock)
    candidate_requests = []

    def candidates_callback(request, context):
        candidate_requests.append(request)
        context.status_code = 200
        return [{"id": 1, "updated_at": "2026-08-24T12:00:00.000Z"}]

    requests_mock.get("https://harvest.greenhouse.io/v3/candidates", json=candidates_callback)

    state = StateBuilder().with_stream_state("candidates", {"updated_at": "2026-08-24T12:00:00.000Z"}).build()
    source = get_source(CONFIG_WITH_EPOCH_START_DATE, state=state)
    catalog = CatalogBuilder().with_stream("candidates", SyncMode.incremental).build()
    with _freeze_cursor_time():
        read(source, config=CONFIG_WITH_EPOCH_START_DATE, catalog=catalog)

    assert candidate_requests[0].qs["updated_at"] == ["gte|2026-08-24t11:00:00.000z|lte|2026-08-27t00:00:00.000z"]


@pytest.mark.parametrize(
    "status_code, error",
    [
        pytest.param(400, "invalid_grant", id="expired_or_rotated_refresh_token"),
        pytest.param(401, "invalid_client", id="bad_client_credentials"),
        pytest.param(400, "unauthorized_client", id="client_not_allowed_grant"),
    ],
)
def test_oauth_refresh_failure_surfaces_reauthenticate_config_error(status_code, error, requests_mock, get_source):
    def token_callback(request, context):
        context.status_code = status_code
        return {
            "error": error,
            "error_description": "Refresh token has been invalidated at 2026-01-01T00:00:00Z. The user must re-authorize consent",
        }

    requests_mock.post("https://auth.greenhouse.io/token", json=token_callback)

    source = get_source(CONFIG)
    catalog = CatalogBuilder().with_stream("applications", SyncMode.incremental).build()
    output = read(source, config=CONFIG, catalog=catalog, expecting_exception=True)

    messages = [trace.trace.error.message for trace in output.errors]
    assert any("Please re-authenticate" in text for text in messages), messages
    assert all(trace.trace.error.failure_type == FailureType.config_error for trace in output.errors), [
        (trace.trace.error.failure_type, trace.trace.error.message) for trace in output.errors
    ]
