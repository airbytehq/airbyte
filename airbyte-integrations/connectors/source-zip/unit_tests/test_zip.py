# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Unit tests for `source-zip` covering the manifest behaviors that are easy to regress:

- the `Zip-Api-Key` and `Zip-Api-Version` headers and the exact set of parameters every stream sends
- `DefaultPaginator` + `CursorPagination`: `page_size` on every request, `page_token` set to the
  previous response's `next_page_token`, and a stop when the token is missing or null
- the per-endpoint filter parameter (`last_updated_after` or `updated_after`) carrying the state
  cursor, or the `start_date`, as epoch seconds
- the state cursor advancing to the latest `updated_at` read
- the merged schema: `id` and `updated_at` keep their pinned types, every other discovered
  top-level key is a nullable string, and an empty endpoint leaves only the pinned fields
- a 401 or 403 failing as `config_error` without retries, and 429 and 5xx being retried

Each stream's `DynamicSchemaLoader` reads one page from the same endpoint before the sync starts.
That request never carries the incremental filter, while every sync request does, so the mocks
below register the schema read on the bare URL and the sync reads on the URL with the filter.
"""

import logging
import time

import pytest
import requests_mock
from _helpers import (
    API_KEY,
    API_VERSION,
    CONFIG,
    DEFAULT_START_DATE_EPOCH,
    REQUESTS_PATH,
    REQUESTS_URL,
    START_DATE_EPOCH,
    STREAMS,
    config_without,
    get_source,
    mock_schema_read,
    page,
    query_params,
    read_stream,
    record,
    record_ids,
    requests_to,
    schema_requests,
    stream_schema,
    sync_requests,
    sync_url,
)

from airbyte_cdk.models import FailureType, Status, SyncMode
from airbyte_cdk.test.state_builder import StateBuilder


@pytest.mark.parametrize("stream_name", list(STREAMS))
def test_headers_and_parameters_per_stream(stream_name):
    """Every stream's request carries the two Zip headers and exactly the expected query parameters."""
    stream = STREAMS[stream_name]
    with requests_mock.Mocker() as mocker:
        mock_schema_read(mocker, stream_name)
        mocker.get(sync_url(stream_name, START_DATE_EPOCH), json=page([record("x-1", 1718000500)]))
        output = read_stream(stream_name)

    assert record_ids(output) == ["x-1"]
    data_requests = requests_to(mocker.request_history, stream["path"])
    assert len(data_requests) == 2, f"expected one schema read and one sync request, got {len(data_requests)}"
    for request in data_requests:
        assert request.headers["Zip-Api-Key"] == API_KEY
        assert request.headers["Zip-Api-Version"] == API_VERSION
        params = query_params(request)
        assert params["sort_by"] == "updated_at", params
        assert params["sort_order"] == "desc", params
        assert params["include_attributes"] == "true", params
        assert params["page_size"] == stream["page_size"], params

    sync = sync_requests(mocker.request_history, stream_name)
    assert len(sync) == 1
    # Exactly this set, as seen against the live API. The other endpoint's filter name returns HTTP 400.
    assert set(query_params(sync[0])) == {"sort_by", "sort_order", "include_attributes", "page_size", stream["filter"]}


def test_api_version_defaults_when_not_configured():
    """A config without `api_version` still sends the header, with the manifest's default."""
    with requests_mock.Mocker() as mocker:
        mocker.get(REQUESTS_URL, json=page([record("r-1", 1718000500)]))
        output = read_stream("requests", config=config_without("api_version"))

    assert record_ids(output) == ["r-1"]
    data_requests = requests_to(mocker.request_history, REQUESTS_PATH)
    assert data_requests
    for request in data_requests:
        assert request.headers["Zip-Api-Version"] == "2024-06-06"


def test_pagination():
    """`page_token` carries the previous page's `next_page_token`, and `page_size` is sent on every page."""
    page_1 = page([record("r-1", 1718000500), record("r-2", 1718000400)], next_page_token="tok-2")
    page_2 = page([record("r-3", 1718000300)])

    with requests_mock.Mocker() as mocker:
        mock_schema_read(mocker, "requests")
        mocker.get(sync_url("requests", START_DATE_EPOCH), [{"json": page_1, "status_code": 200}, {"json": page_2, "status_code": 200}])
        output = read_stream("requests")

    assert record_ids(output) == ["r-1", "r-2", "r-3"]

    sync = sync_requests(mocker.request_history, "requests")
    assert len(sync) == 2, f"expected 2 paginated requests, got {len(sync)}"

    first_params = query_params(sync[0])
    assert first_params["page_size"] == "30"
    assert "page_token" not in first_params, f"first request must not carry a page token, got {first_params}"

    second_params = query_params(sync[1])
    assert second_params.get("page_token") == "tok-2", f"second request must resume from the token, got {second_params}"
    assert second_params["page_size"] == "30"


def test_pagination_stops_on_null_token():
    """A response whose `next_page_token` is present but null must end the read instead of looping."""
    body = {**page([record("r-1", 1718000500)]), "next_page_token": None}

    with requests_mock.Mocker() as mocker:
        mock_schema_read(mocker, "requests")
        mocker.get(
            sync_url("requests", START_DATE_EPOCH),
            [
                {"json": body, "status_code": 200},
                # A stop condition that is not null-safe loops on the same page forever. Failing the
                # second request keeps that regression a fast test failure instead of a hung suite.
                {"json": {}, "status_code": 400},
            ],
        )
        output = read_stream("requests")

    assert record_ids(output) == ["r-1"]
    assert len(sync_requests(mocker.request_history, "requests")) == 1


@pytest.mark.parametrize("stream_name", list(STREAMS))
def test_state_cursor_is_sent_as_the_endpoint_filter(stream_name):
    """Each endpoint gets the saved `updated_at` under its own filter name."""
    stream = STREAMS[stream_name]
    cursor = "1718000000"
    state = StateBuilder().with_stream_state(stream_name, {"updated_at": cursor}).build()

    with requests_mock.Mocker() as mocker:
        mock_schema_read(mocker, stream_name)
        mocker.get(sync_url(stream_name, cursor), json=page([record("x-2", 1718000600)]))
        output = read_stream(stream_name, sync_mode=SyncMode.incremental, state=state)

    assert record_ids(output) == ["x-2"]
    sync = sync_requests(mocker.request_history, stream_name)
    assert len(sync) == 1, f"expected one sync request, got {len(sync)}"
    assert query_params(sync[0])[stream["filter"]] == cursor


def test_start_date_wins_over_an_older_state():
    """A saved cursor earlier than `start_date` is not used; the sync starts at `start_date`."""
    state = StateBuilder().with_stream_state("requests", {"updated_at": "1000"}).build()

    with requests_mock.Mocker() as mocker:
        mock_schema_read(mocker, "requests")
        mocker.get(sync_url("requests", START_DATE_EPOCH), json=page([]))
        output = read_stream("requests", sync_mode=SyncMode.incremental, state=state)

    assert not output.errors, [error.trace.error.message for error in output.errors]
    sync = sync_requests(mocker.request_history, "requests")
    assert len(sync) == 1
    assert query_params(sync[0])["last_updated_after"] == START_DATE_EPOCH


@pytest.mark.parametrize(
    "start_date, expected_epoch",
    [
        pytest.param(None, DEFAULT_START_DATE_EPOCH, id="default"),
        pytest.param("2024-01-01T00:00:00Z", START_DATE_EPOCH, id="whole_seconds"),
        pytest.param("2024-01-01T00:00:00.000Z", START_DATE_EPOCH, id="fractional_seconds"),
    ],
)
def test_start_date_is_sent_as_epoch_seconds(start_date, expected_epoch):
    """Without saved state, the first sync filters from `start_date` (or the manifest default) in epoch seconds."""
    config = config_without("start_date")
    if start_date is not None:
        config["start_date"] = start_date

    with requests_mock.Mocker() as mocker:
        mocker.get(REQUESTS_URL, json=page([]))
        output = read_stream("requests", config=config, sync_mode=SyncMode.incremental)

    assert not output.errors, [error.trace.error.message for error in output.errors]
    sync = sync_requests(mocker.request_history, "requests")
    assert len(sync) == 1, f"expected one sync request against /requests, got {len(sync)}"
    assert query_params(sync[0])["last_updated_after"] == expected_epoch


def test_state_advances_to_the_latest_updated_at():
    """After a sync, the stream state holds the largest `updated_at` read, as epoch seconds."""
    with requests_mock.Mocker() as mocker:
        mock_schema_read(mocker, "requests")
        mocker.get(sync_url("requests", START_DATE_EPOCH), json=page([record("r-1", 1718000500), record("r-2", 1718000400)]))
        output = read_stream("requests", sync_mode=SyncMode.incremental)

    assert record_ids(output) == ["r-1", "r-2"]
    state = output.most_recent_state.stream_state.__dict__
    assert state.get("updated_at") == "1718000500", state


def test_schema_merges_pinned_types_with_discovered_strings():
    """`id` and `updated_at` keep the pinned types; every other key of the first record is a nullable string."""
    with requests_mock.Mocker() as mocker:
        mocker.get(REQUESTS_URL, json=page([record("r-1", 1718000500), record("r-2", 1718000400, extra_key="x")]))
        schema = stream_schema("requests")

    properties = schema["properties"]
    assert properties["id"] == {"type": "string"}
    assert properties["updated_at"] == {"type": "integer"}
    for key in ("name", "status", "amount_usd", "created_at", "description"):
        assert properties[key] == {"type": ["null", "string"]}, (key, properties[key])
    # Nested objects and arrays are declared as strings too. The connector emits them unchanged;
    # typed destinations store them as JSON text.
    assert properties["vendor"] == {"type": ["null", "string"]}
    assert properties["attributes"] == {"type": ["null", "string"]}
    # Only the first record is inspected.
    assert "extra_key" not in properties
    # The CDK's merged schema omits `additionalProperties`, so undeclared fields stay allowed.
    assert schema.get("additionalProperties") is not False

    schema_reads = schema_requests(mocker.request_history, "requests")
    assert len(schema_reads) == 1, f"expected one schema read, got {len(schema_reads)}"
    assert "page_token" not in query_params(schema_reads[0])


def test_schema_of_an_empty_endpoint_keeps_the_pinned_fields():
    """When the endpoint returns no records, the schema still declares `id` and `updated_at`."""
    with requests_mock.Mocker() as mocker:
        mocker.get(REQUESTS_URL, json=page([]))
        schema = stream_schema("requests")

    assert set(schema["properties"]) == {"id", "updated_at"}
    assert schema["properties"]["id"] == {"type": "string"}
    assert schema["properties"]["updated_at"] == {"type": "integer"}
    assert schema.get("additionalProperties") is not False


def test_check_uses_requests():
    """`check` succeeds off the `requests` stream."""
    with requests_mock.Mocker() as mocker:
        mocker.get(REQUESTS_URL, json=page([record("r-1", 1718000500)]))
        status = get_source(CONFIG).check(logging.getLogger("test_check_uses_requests"), CONFIG)

    assert status.status == Status.SUCCEEDED, f"expected a successful check, got {status}"
    assert requests_to(mocker.request_history, REQUESTS_PATH), "check must exercise the requests stream"


def test_check_fails_with_the_api_key_message_on_401():
    """A rejected key makes `check` fail and surface the connector's own message."""
    with requests_mock.Mocker() as mocker:
        mocker.get(REQUESTS_URL, json={"message": "The provided API key is not valid"}, status_code=401)
        status = get_source(CONFIG).check(logging.getLogger("test_check_fails"), CONFIG)

    assert status.status == Status.FAILED, status
    assert "Zip rejected the API key" in (status.message or ""), status.message


@pytest.mark.parametrize("stream_name", list(STREAMS))
@pytest.mark.parametrize("status_code", [401, 403])
def test_rejected_api_key_is_a_config_error(stream_name, status_code):
    """A rejected key on the sync request fails as `config_error` with an actionable message, without retries."""
    with requests_mock.Mocker() as mocker:
        mock_schema_read(mocker, stream_name)
        mocker.get(sync_url(stream_name, START_DATE_EPOCH), json={"message": "The provided API key is not valid"}, status_code=status_code)
        output = read_stream(stream_name)

    errors = [message.trace.error for message in output.errors]
    assert errors, "expected the read to emit an error trace"
    assert errors[0].failure_type == FailureType.config_error, errors[0].failure_type
    # Load-bearing: the CDK already maps 401 and 403 to config_error, so only the message proves the
    # manifest's own response filter is in place.
    assert "Zip rejected the API key" in errors[0].message, errors[0].message
    assert len(sync_requests(mocker.request_history, stream_name)) == 1, "auth errors must not be retried"


def test_transient_errors_are_retried(monkeypatch):
    """429 and 5xx responses are retried with the CDK defaults, and the read completes."""
    monkeypatch.setattr(time, "sleep", lambda seconds: None)

    with requests_mock.Mocker() as mocker:
        mock_schema_read(mocker, "requests")
        mocker.get(
            sync_url("requests", START_DATE_EPOCH),
            [
                {"json": {"message": "rate limited"}, "status_code": 429},
                {"json": {"message": "upstream error"}, "status_code": 500},
                {"json": page([record("r-1", 1718000500)]), "status_code": 200},
            ],
        )
        output = read_stream("requests")

    assert record_ids(output) == ["r-1"]
    assert not output.errors, [error.trace.error.message for error in output.errors]
    assert len(sync_requests(mocker.request_history, "requests")) == 3
