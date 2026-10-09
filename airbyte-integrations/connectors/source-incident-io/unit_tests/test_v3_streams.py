# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Unit tests for `source-incident-io`: the v3 `actions` and `follow-ups` streams, the check stream,
incremental state handling, error handling, and the `users` stream options.

Verifies that both streams read from the paginated `/v3` endpoints (the `/v2`
endpoints are deprecated), follow the `pagination_meta.after` cursor, stop when
no `after` value is returned, and query every `incident_mode` partition
(`standard`, `retrospective`, `test`, `tutorial`, `stream`) so records from all
incident modes are synced.

Each test registers a catch-all empty response for the path first, then
mode-specific responses for `?incident_mode=<mode>` URLs. requests_mock matches
later registrations first, so the mode-specific mocks take precedence over the
catch-all.
"""

import logging
from pathlib import Path
from unittest import mock

import jsonschema
import pytest
import requests_mock
import yaml

from airbyte_cdk.models import Status, SyncMode
from airbyte_cdk.sources.declarative.parsers.manifest_reference_resolver import ManifestReferenceResolver
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder


def _get_manifest_path() -> Path:
    ci_path = Path("/airbyte/integration_code/source_declarative_manifest")
    if ci_path.exists():
        return ci_path
    return Path(__file__).parent.parent


_MANIFEST_PATH = _get_manifest_path() / "manifest.yaml"
_CONFIG = {"api_key": "test-key"}
# A start_date inside one P30D window of "now", so tests that count requests see a single slice.
_RECENT_CONFIG = {"api_key": "test-key", "start_date": "2026-10-06T00:00:00Z"}
_BASE_URL = "https://api.incident.io"
_MODES = ["standard", "retrospective", "test", "tutorial", "stream"]
_STATUS_CATEGORIES = ["triage", "live", "learning", "paused", "closed", "declined", "canceled", "merged"]


def _get_source(state=None, config=None):
    return YamlDeclarativeSource(
        path_to_yaml=str(_MANIFEST_PATH),
        catalog=CatalogBuilder().build(),
        config=config or _CONFIG,
        state=state if state is not None else StateBuilder().build(),
    )


def _read_stream(stream_name, sync_mode=SyncMode.full_refresh, state=None, config=None):
    catalog = CatalogBuilder().with_stream(stream_name, sync_mode).build()
    return read(_get_source(state, config), config or _CONFIG, catalog, state=state)


def _mock_empty(mocker, path, records_field):
    mocker.get(
        f"{_BASE_URL}{path}",
        json={records_field: [], "pagination_meta": {"page_size": 100}},
    )


def _mock_mode(mocker, path, mode, *args, **kwargs):
    mocker.get(f"{_BASE_URL}{path}?incident_mode={mode}", *args, **kwargs)


@pytest.mark.parametrize(
    ("stream_name", "path", "records_field"),
    [
        ("actions", "/v3/actions", "actions"),
        ("follow-ups", "/v3/follow_ups", "follow_ups"),
    ],
)
def test_stream_reads_v3_endpoint_and_follows_pagination(stream_name, path, records_field):
    first_response = {
        records_field: [{"id": "a-1", "title": "first"}],
        "pagination_meta": {"after": "a-1", "page_size": 100},
    }
    second_response = {
        records_field: [{"id": "a-2"}],
        "pagination_meta": {"page_size": 100},
    }

    with requests_mock.Mocker() as mocker:
        _mock_empty(mocker, path, records_field)
        _mock_mode(mocker, path, "standard", [{"json": first_response}, {"json": second_response}])
        output = _read_stream(stream_name, config=_RECENT_CONFIG)

        requests_made = mocker.request_history

    assert [message.record.data["id"] for message in output.records] == ["a-1", "a-2"]
    assert len(requests_made) == len(_MODES) + 1
    standard_requests = [request for request in requests_made if request.qs["incident_mode"] == ["standard"]]
    assert len(standard_requests) == 2
    assert "after" not in standard_requests[0].qs
    assert standard_requests[1].qs["after"] == ["a-1"]
    assert all(request.qs["page_size"] == ["250"] for request in requests_made)
    assert all("/v2/" not in request.path for request in requests_made)


@pytest.mark.parametrize(
    ("stream_name", "path", "records_field"),
    [
        ("actions", "/v3/actions", "actions"),
        ("follow-ups", "/v3/follow_ups", "follow_ups"),
    ],
)
def test_stream_queries_every_incident_mode(stream_name, path, records_field):
    with requests_mock.Mocker() as mocker:
        _mock_empty(mocker, path, records_field)
        for mode in _MODES:
            _mock_mode(
                mocker,
                path,
                mode,
                json={
                    records_field: [{"id": f"{mode}-1"}],
                    "pagination_meta": {"page_size": 100},
                },
            )
        output = _read_stream(stream_name, config=_RECENT_CONFIG)

        requests_made = mocker.request_history

    assert len(requests_made) == len(_MODES)
    assert all(len(request.qs["incident_mode"]) == 1 for request in requests_made)
    assert {request.qs["incident_mode"][0] for request in requests_made} == set(_MODES)
    assert sorted(message.record.data["id"] for message in output.records) == sorted(f"{mode}-1" for mode in _MODES)


@pytest.mark.parametrize(
    ("stream_name", "path", "records_field"),
    [
        ("actions", "/v3/actions", "actions"),
        ("follow-ups", "/v3/follow_ups", "follow_ups"),
    ],
)
def test_stream_stops_after_single_page(stream_name, path, records_field):
    response = {
        records_field: [{"id": "a-1"}],
        "pagination_meta": {"page_size": 100},
    }

    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}{path}", json=response)
        output = _read_stream(stream_name, config=_RECENT_CONFIG)

        requests_made = mocker.request_history

    assert len(requests_made) == len(_MODES)
    assert all("after" not in request.qs for request in requests_made)
    assert [message.record.data["id"] for message in output.records] == ["a-1"] * len(_MODES)


def test_follow_ups_record_keeps_category():
    category = {"id": "c1", "name": "Bug", "description": "d", "rank": 1}
    response = {
        "follow_ups": [{"id": "fu-1", "category": category}],
        "pagination_meta": {"page_size": 100},
    }

    with requests_mock.Mocker() as mocker:
        _mock_empty(mocker, "/v3/follow_ups", "follow_ups")
        _mock_mode(mocker, "/v3/follow_ups", "standard", json=response)
        output = _read_stream("follow-ups", config=_RECENT_CONFIG)

    assert output.records[0].record.data["category"] == category


def test_check_uses_incidents_stream():
    """The check stream is `incidents`: a current endpoint that needs only the base incident read scope."""
    with requests_mock.Mocker() as mocker:
        mocker.get(
            f"{_BASE_URL}/v2/incidents",
            json={"incidents": [{"id": "inc-1", "updated_at": "2026-09-18T10:38:18.161Z"}], "pagination_meta": {}},
        )
        connection_status = _get_source().check(logging.getLogger("airbyte"), _CONFIG)

        assert len(mocker.request_history) >= 1
        assert mocker.request_history[0].path == "/v2/incidents"
        assert all("/v3/actions" not in request.url for request in mocker.request_history)

    assert connection_status.status == Status.SUCCEEDED


def test_incidents_requests_all_status_categories():
    response = {
        "incidents": [{"id": "1", "updated_at": "2026-09-18T10:38:18.161Z"}],
        "pagination_meta": {},
    }
    config = {**_CONFIG, "time_window": "P36500D"}

    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}/v2/incidents", json=response)
        output = _read_stream("incidents", config=config)
        requests_made = mocker.request_history

    assert [message.record.data["id"] for message in output.records] == ["1"]
    assert requests_made
    assert all(request.qs["status_category[one_of]"] == _STATUS_CATEGORIES for request in requests_made)


@pytest.mark.parametrize(
    ("stream_name", "path", "records_field"),
    [
        ("incidents", "/v2/incidents", "incidents"),
        ("alerts", "/v2/alerts", "alerts"),
        ("escalations", "/v2/escalations", "escalations"),
        ("actions", "/v3/actions", "actions"),
        ("follow-ups", "/v3/follow_ups", "follow_ups"),
    ],
)
def test_incremental_sends_a_date_range_window_and_keeps_full_timestamp(stream_name, path, records_field):
    """`updated_at[gte]`+`updated_at[lte]` together are a 422, so each slice goes out as one
    `updated_at[date_range]=<start>~<end>` parameter. Resuming applies the PT5M lookback for the
    timestamp-level streams (alerts/actions/follow-ups); incidents and escalations send dates only
    (see CONTRIBUTING.md)."""
    state = StateBuilder().with_stream_state(stream_name, {"updated_at": "2026-09-18T10:38:18Z"}).build()
    response = {
        records_field: [{"id": "r-1", "updated_at": "2026-09-20T08:00:00.123Z"}],
        "pagination_meta": {"page_size": 100},
    }

    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}{path}", json=response)
        output = _read_stream(stream_name, SyncMode.incremental, state)
        requests_made = mocker.request_history

    assert requests_made, "no request was made"
    expected_start = "2026-09-18t10:33:18" if stream_name in ("alerts", "actions", "follow-ups") else "2026-09-18~"
    for request in requests_made:
        assert "updated_at[gte]" not in request.qs
        assert "updated_at[lte]" not in request.qs
        assert request.qs["updated_at[date_range]"][0].lower().startswith(expected_start)
    assert [message.record.data["id"] for message in output.records][:1] == ["r-1"]
    final_state = output.most_recent_state.stream_state.__dict__
    if stream_name in ("actions", "follow-ups"):
        # One cursor per incident_mode plus a global fallback; every partition saw the same record.
        assert final_state["state"] == {"updated_at": "2026-09-20T08:00:00.123000Z"}
        assert {s["partition"]["incident_mode"] for s in final_state["states"]} == set(_MODES)
        assert all(s["cursor"] == {"updated_at": "2026-09-20T08:00:00.123000Z"} for s in final_state["states"])
    else:
        assert final_state == {"updated_at": "2026-09-20T08:00:00.123000Z"}


@pytest.mark.parametrize(
    ("stream_name", "path", "records_field"),
    [
        ("actions", "/v3/actions", "actions"),
        ("follow-ups", "/v3/follow_ups", "follow_ups"),
    ],
)
def test_per_partition_state_sets_each_mode_filter(stream_name, path, records_field):
    """After the first 0.2.0 sync the state carries one cursor per incident_mode; each partition must resume
    from its own date and the others from the global one."""
    state = (
        StateBuilder()
        .with_stream_state(
            stream_name,
            {
                "use_global_cursor": False,
                "state": {"updated_at": "2026-09-18T10:38:18Z"},
                "states": [{"partition": {"incident_mode": "standard"}, "cursor": {"updated_at": "2026-09-19T00:00:00Z"}}],
            },
        )
        .build()
    )
    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}{path}", json={records_field: [], "pagination_meta": {"page_size": 250}})
        output = _read_stream(stream_name, SyncMode.incremental, state)
        by_mode = {request.qs["incident_mode"][0]: request.qs["updated_at[date_range]"][0].lower() for request in mocker.request_history}

    # The standard partition resumes 5 minutes before its own cursor; the others from the global one.
    assert by_mode["standard"].startswith("2026-09-18t23:55:00")
    assert all(by_mode[mode].startswith("2026-09-18t10:33:18") for mode in _MODES if mode != "standard")
    final_state = output.most_recent_state.stream_state.__dict__
    standard = next(s for s in final_state["states"] if s["partition"] == {"incident_mode": "standard"})
    assert standard["cursor"] == {"updated_at": "2026-09-19T00:00:00.000000Z"}


def test_start_date_config_starts_the_first_window():
    config = {**_CONFIG, "start_date": "2025-03-01T00:00:00Z"}
    catalog = CatalogBuilder().with_stream("incidents", SyncMode.full_refresh).build()
    source = YamlDeclarativeSource(path_to_yaml=str(_MANIFEST_PATH), catalog=catalog, config=config, state=StateBuilder().build())
    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}/v2/incidents", json={"incidents": [], "pagination_meta": {}})
        read(source, config, catalog)
        assert any(request.qs["updated_at[date_range]"][0].startswith("2025-03-01~") for request in mocker.request_history)


@pytest.mark.parametrize(
    ("stream_name", "path", "records_field", "expected"),
    [
        ("incidents", "/v2/incidents", "incidents", "250"),
        ("incident_updates", "/v2/incident_updates", "incident_updates", "250"),
        ("escalations", "/v2/escalations", "escalations", "50"),
        ("alerts", "/v2/alerts", "alerts", "50"),
        ("schedules", "/v2/schedules", "schedules", "100"),
    ],
)
def test_page_sizes_match_what_the_api_serves(stream_name, path, records_field, expected):
    """incidents is capped at 250 by the live API (spec says 500); schedules stays at 100 on purpose, see CONTRIBUTING.md."""
    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}{path}", json={records_field: [], "pagination_meta": {}})
        _read_stream(stream_name)
        assert mocker.request_history[0].qs["page_size"] == [expected]


@pytest.mark.parametrize(
    ("stream_name", "path", "records_field"),
    [
        ("incidents", "/v2/incidents", "incidents"),
        ("actions", "/v3/actions", "actions"),
    ],
)
def test_full_refresh_without_start_date_reads_everything(stream_name, path, records_field):
    """The cursor window is applied in full refresh too, so the default start must predate all
    incident.io data. A relative default (for example two years back) silently dropped 2023 records on
    an existing full-refresh connection. One huge `time_window` keeps this to a single request."""
    config = {**_CONFIG, "time_window": "P36500D"}
    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}{path}", json={records_field: [{"id": "r-1"}], "pagination_meta": {}})
        _read_stream(stream_name, config=config)
        requests_made = mocker.request_history

    assert requests_made
    assert all(request.qs["updated_at[date_range]"][0].startswith("2020-01-01") for request in requests_made)


@pytest.mark.parametrize(
    ("stream_name", "path", "records_field", "first_window", "second_window"),
    [
        # Timestamp-level streams: half-open [start, end) slices at microsecond precision.
        (
            "alerts",
            "/v2/alerts",
            "alerts",
            "2020-01-01t00:00:00.000000z~2020-01-30t23:59:59.999999z",
            "2020-01-31t00:00:00.000000z~2020-02-29t23:59:59.999999z",
        ),
        # Date-level streams: both bounds inclusive, formatted as dates.
        (
            "escalations",
            "/v2/escalations",
            "escalations",
            "2020-01-01~2020-01-30",
            "2020-01-31~2020-02-29",
        ),
    ],
)
def test_p30d_slices_tile_without_gaps(stream_name, path, records_field, first_window, second_window):
    """Consecutive P30D slices neither overlap nor gap: each slice ends one cursor_granularity tick
    before the next one starts."""
    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}{path}", json={records_field: [], "pagination_meta": {}})
        _read_stream(stream_name, SyncMode.incremental)

        windows = [request.qs["updated_at[date_range]"][0].lower() for request in mocker.request_history]

    assert len(windows) > 1
    assert windows[0] == first_window
    assert windows[1] == second_window


def test_time_window_config_changes_the_slice_size():
    """`time_window` overrides the default P30D step; P365D tiles the same range in ~365-day windows."""
    config = {**_CONFIG, "start_date": "2020-01-01T00:00:00Z", "time_window": "P365D"}
    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}/v2/alerts", json={"alerts": [], "pagination_meta": {}})
        _read_stream("alerts", SyncMode.incremental, config=config)

        windows = [request.qs["updated_at[date_range]"][0].lower() for request in mocker.request_history]

    assert windows[0] == "2020-01-01t00:00:00.000000z~2020-12-30t23:59:59.999999z"
    assert windows[1].startswith("2020-12-31t00:00:00.000000z~")
    assert len(windows) < 10


def test_missing_scope_is_a_config_error_naming_the_scope():
    """A 403 is a configuration problem the user can fix; the message carries the scope the API names."""
    # Real body captured from the API on 2026-10-07 with a key lacking the scope (scope name swapped).
    body = {
        "type": "resource_forbidden",
        "status": 403,
        "request_id": "ZtsoWDj7",
        "errors": [
            {
                "code": "missing_required_scope",
                "message": "missing a required scope: workflows.view",
                "metadata": {"scope": "workflows.view"},
            }
        ],
    }

    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}/v2/workflows", status_code=403, json=body)
        output = _read_stream("workflows")

    assert output.records == []
    error = _stream_error(output, "workflows")
    assert error.failure_type.value == "config_error"
    assert error.message == (
        "The API key lacks a permission this stream needs: missing a required scope: workflows.view. "
        "Grant it in incident.io under Settings > API keys, or deselect the stream."
    )


def _stream_error(output, stream_name):
    """The stream-level traced error, not the end-of-sync summary the concurrent source adds last."""
    return next(
        message.trace.error
        for message in output.errors
        if message.trace.error.stream_descriptor and message.trace.error.stream_descriptor.name == stream_name
    )


def test_403_vendor_message_is_capped_at_300_characters():
    """A vendor message can be arbitrarily long; the template cuts it to 300 characters."""
    body = {"errors": [{"code": "missing_required_scope", "message": "a" * 300 + "b" * 700}]}
    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}/v2/workflows", status_code=403, json=body)
        output = _read_stream("workflows")

    error = _stream_error(output, "workflows")
    assert error.failure_type.value == "config_error"
    assert error.message == (
        "The API key lacks a permission this stream needs: " + "a" * 300 + ". "
        "Grant it in incident.io under Settings > API keys, or deselect the stream."
    )


def test_422_vendor_message_is_capped_at_300_characters():
    body = {"errors": [{"code": "invalid_value", "message": "a" * 300 + "b" * 700}]}
    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}/v2/incidents", status_code=422, json=body)
        output = _read_stream("incidents")

    error = _stream_error(output, "incidents")
    assert error.failure_type.value == "system_error"
    assert error.message == "incident.io rejected the request: " + "a" * 300


def test_403_null_vendor_message_falls_back_to_the_default():
    body = {"errors": [{"code": "missing_required_scope", "message": None}]}
    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}/v2/workflows", status_code=403, json=body)
        output = _read_stream("workflows")

    error = _stream_error(output, "workflows")
    assert error.failure_type.value == "config_error"
    assert error.message.startswith("The API key lacks a permission this stream needs: see the incident.io error response.")


@pytest.mark.parametrize("body", [{"errors": []}, {"errors": None}, {}])
def test_403_without_a_vendor_message_is_still_a_config_error(body):
    """An empty or missing errors list must not break the message template (it used to raise UndefinedError
    inside the error handler, turning a clear configuration error into a generic system error)."""
    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}/v2/workflows", status_code=403, json=body)
        output = _read_stream("workflows")

    error = _stream_error(output, "workflows")
    assert error.failure_type.value == "config_error"
    assert error.message.startswith("The API key lacks a permission this stream needs: see the incident.io error response.")


@pytest.mark.parametrize(
    ("status", "body", "failure_type", "expected"),
    [
        (
            401,
            {
                "type": "authentication_error",
                "status": 401,
                "errors": [{"code": "access_token_invalid", "message": "Access token is not valid"}],
            },
            "config_error",
            "The API key is invalid or has been revoked. Create a new key in incident.io under Settings > API keys and update the connector configuration.",
        ),
        (
            422,
            {
                "type": "validation_error",
                "status": 422,
                "errors": [{"code": "invalid_value", "message": "Filter field date_range must provide a date in the format yyyy-mm-dd"}],
            },
            "system_error",
            "incident.io rejected the request: Filter field date_range must provide a date in the format yyyy-mm-dd",
        ),
    ],
)
def test_fail_responses_surface_the_manifest_messages(status, body, failure_type, expected):
    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}/v2/incidents", status_code=status, json=body)
        output = _read_stream("incidents")

    error = _stream_error(output, "incidents")
    assert error.failure_type.value == failure_type
    assert error.message == expected


def test_rate_limit_waits_for_retry_after_then_succeeds():
    responses = [
        {
            "status_code": 429,
            "headers": {"retry-after": "7", "x-ratelimit-remaining": "0"},
            "json": {"type": "rate_limit_error", "status": 429, "errors": [{"code": "rate_limited", "message": "rate limited"}]},
        },
        {"status_code": 200, "json": {"incidents": [{"id": "i-1", "updated_at": "2026-09-20T08:00:00.123Z"}], "pagination_meta": {}}},
    ]
    with mock.patch("time.sleep") as sleep, requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}/v2/incidents", responses)
        output = _read_stream("incidents", config=_RECENT_CONFIG)
        assert len(mocker.request_history) == 2

    assert output.errors == []
    assert [message.record.data["id"] for message in output.records] == ["i-1"]
    assert any(call.args and call.args[0] >= 7 for call in sleep.call_args_list)


def test_spec_exposes_num_workers_within_the_max_concurrency():
    spec = _get_source().spec(logging.getLogger("airbyte"))
    properties = spec.connectionSpecification["properties"]
    assert "num_workers" not in spec.connectionSpecification.get("required", [])
    num_workers = properties["num_workers"]
    assert num_workers["type"] == "integer"
    assert num_workers["default"] == 4
    assert num_workers["minimum"] == 1
    assert num_workers["maximum"] == 10


@pytest.mark.parametrize(
    "value, valid",
    [
        ("P1D", True),
        ("P30D", True),
        ("P365D", True),
        ("PT1H", False),
        ("P0D", False),
        ("PT0S", False),
        ("P1W", False),
        ("P1DT1H", False),
    ],
)
def test_spec_time_window_accepts_whole_days_only(value, valid):
    spec = _get_source().spec(logging.getLogger("airbyte"))
    time_window = spec.connectionSpecification["properties"]["time_window"]
    assert jsonschema.Draft7Validator(time_window).is_valid(value) is valid


@pytest.mark.parametrize("num_workers", [1, 10])
def test_num_workers_config_reads_a_stream(num_workers):
    config = {**_RECENT_CONFIG, "num_workers": num_workers}
    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}/v2/incidents", json={"incidents": [{"id": "i-1"}], "pagination_meta": {}})
        output = _read_stream("incidents", config=config)

    assert output.errors == []
    assert [message.record.data["id"] for message in output.records] == ["i-1"]


def test_users_requests_inactive_users():
    """`users` asks for deactivated accounts too, so a user who leaves does not vanish from the stream."""
    with requests_mock.Mocker() as mocker:
        mocker.get(
            f"{_BASE_URL}/v2/users",
            json={"users": [{"id": "u-1", "is_active": False}], "pagination_meta": {"page_size": 100}},
        )
        output = _read_stream("users")
        requests_made = mocker.request_history

    assert requests_made[0].qs["include_inactive"] == ["true"]
    assert requests_made[0].qs["page_size"] == ["10000"]
    assert output.records[0].record.data["is_active"] is False


def test_incident_types_reads_v1_endpoint():
    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}/v1/incident_types", json={"incident_types": [{"id": "type-1", "name": "Production"}]})
        output = _read_stream("incident_types")

    assert [message.record.data["id"] for message in output.records] == ["type-1"]


def test_incident_attachments_partitions_by_incident_and_ignores_404():
    incidents = {
        "incidents": [
            {"id": "incident-1", "updated_at": "2026-10-08T00:00:00Z"},
            {"id": "incident-2", "updated_at": "2026-10-08T00:00:00Z"},
        ],
        "pagination_meta": {},
    }
    attachment = {
        "incident_attachments": [
            {
                "id": "attachment-2",
                "incident_id": "incident-2",
                "resource": {"external_id": "123", "permalink": "https://example.com", "title": "Alert", "resource_type": "arbitrary_url"},
            }
        ]
    }

    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}/v2/incidents", json=incidents)
        mocker.get(
            f"{_BASE_URL}/v1/incident_attachments?incident_id=incident-1",
            complete_qs=True,
            status_code=404,
            json={"errors": [{"message": "Incident was deleted"}]},
        )
        mocker.get(
            f"{_BASE_URL}/v1/incident_attachments?incident_id=incident-2",
            complete_qs=True,
            json=attachment,
        )
        output = _read_stream("incident_attachments", config=_RECENT_CONFIG)
        attachment_requests = [request for request in mocker.request_history if request.path == "/v1/incident_attachments"]

    assert output.errors == []
    assert [message.record.data["id"] for message in output.records] == ["attachment-2"]
    assert sorted(request.qs["incident_id"][0] for request in attachment_requests) == ["incident-1", "incident-2"]


def test_incident_attachments_retries_transient_errors():
    incidents = {
        "incidents": [{"id": "incident-1", "updated_at": "2026-10-08T00:00:00Z"}],
        "pagination_meta": {},
    }
    attachment = {"incident_attachments": [{"id": "attachment-1", "incident_id": "incident-1"}]}

    with mock.patch("time.sleep"), requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}/v2/incidents", json=incidents)
        mocker.get(
            f"{_BASE_URL}/v1/incident_attachments?incident_id=incident-1",
            [
                {"status_code": 503, "json": {"errors": [{"message": "Temporary service error"}]}},
                {"json": attachment},
            ],
            complete_qs=True,
        )
        output = _read_stream("incident_attachments", config=_RECENT_CONFIG)
        attachment_requests = [request for request in mocker.request_history if request.path == "/v1/incident_attachments"]

    assert output.errors == []
    assert [message.record.data["id"] for message in output.records] == ["attachment-1"]
    assert len(attachment_requests) == 2


def test_incident_attachments_error_handler_reuses_base_filters():
    raw_manifest = yaml.safe_load(_MANIFEST_PATH.read_text())
    manifest = ManifestReferenceResolver().preprocess_manifest(raw_manifest)
    definitions = manifest["definitions"]
    base_requester_handlers = definitions["base_requester"]["error_handler"]["error_handlers"]
    assert len(base_requester_handlers) == 1
    base_handler = base_requester_handlers[0]

    attachment_requester = definitions["streams"]["incident_attachments"]["retriever"]["requester"]
    attachment_handlers = attachment_requester["error_handler"]["error_handlers"]
    assert len(attachment_handlers) == 1
    attachment_handler = attachment_handlers[0]
    assert attachment_handler["type"] == "DefaultErrorHandler"
    assert attachment_handler["max_retries"] == base_handler["max_retries"]

    base_filters = base_handler["response_filters"]
    attachment_filters = attachment_handler["response_filters"]
    assert len(attachment_filters) == len(base_filters) + 1
    assert attachment_filters[0]["action"] == "IGNORE"
    assert attachment_filters[0]["http_codes"] == [404]
    assert [(filter["action"], filter["http_codes"]) for filter in attachment_filters[1:]] == [
        (filter["action"], filter["http_codes"]) for filter in base_filters
    ]


def test_catalog_entries_partitions_and_follows_all_pages():
    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}/v2/catalog_types", json={"catalog_types": [{"id": "catalog-type-1"}]})
        mocker.get(
            f"{_BASE_URL}/v3/catalog_entries",
            [
                {
                    "json": {
                        "catalog_entries": [{"id": "entry-1", "catalog_type_id": "catalog-type-1"}],
                        "pagination_meta": {"after": "entry-1"},
                    }
                },
                {"json": {"catalog_entries": [{"id": "entry-2", "catalog_type_id": "catalog-type-1"}], "pagination_meta": {}}},
            ],
        )
        output = _read_stream("catalog_entries")
        entry_requests = [request for request in mocker.request_history if request.path == "/v3/catalog_entries"]

    assert [message.record.data["id"] for message in output.records] == ["entry-1", "entry-2"]
    assert len(entry_requests) == 2
    assert all(request.qs["catalog_type_id"] == ["catalog-type-1"] for request in entry_requests)
    assert all(request.qs["page_size"] == ["250"] for request in entry_requests)
    assert "after" not in entry_requests[0].qs
    assert entry_requests[1].qs["after"] == ["entry-1"]


def test_catalog_resources_records_are_keyed_by_type():
    with requests_mock.Mocker() as mocker:
        mocker.get(
            f"{_BASE_URL}/v3/catalog_resources",
            json={"resources": [{"type": "Boolean", "label": "Boolean value"}]},
        )
        output = _read_stream("catalog_resources")
        stream = next(stream for stream in _get_source().streams(_CONFIG) if stream.name == "catalog_resources")

    assert stream._primary_key == ["type"]
    assert [message.record.data["type"] for message in output.records] == ["Boolean"]


def test_custom_field_options_partitions_and_follows_all_pages():
    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_BASE_URL}/v2/custom_fields", json={"custom_fields": [{"id": "custom-field-1", "field_type": "single_select"}]})
        mocker.get(
            f"{_BASE_URL}/v1/custom_field_options",
            [
                {
                    "json": {
                        "custom_field_options": [{"id": "option-1", "custom_field_id": "custom-field-1", "value": "one"}],
                        "pagination_meta": {"after": "option-1"},
                    }
                },
                {
                    "json": {
                        "custom_field_options": [{"id": "option-2", "custom_field_id": "custom-field-1", "value": "two"}],
                        "pagination_meta": {},
                    }
                },
            ],
        )
        output = _read_stream("custom_field_options")
        option_requests = [request for request in mocker.request_history if request.path == "/v1/custom_field_options"]

    assert [message.record.data["id"] for message in output.records] == ["option-1", "option-2"]
    assert len(option_requests) == 2
    assert all(request.qs["custom_field_id"] == ["custom-field-1"] for request in option_requests)
    assert all(request.qs["page_size"] == ["250"] for request in option_requests)
    assert "after" not in option_requests[0].qs
    assert option_requests[1].qs["after"] == ["option-1"]
