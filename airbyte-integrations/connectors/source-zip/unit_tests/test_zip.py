# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Unit tests for `source-zip` covering the manifest behaviours that are easy to regress:

- the `Zip-Api-Key` and `Zip-Api-Version` headers and the parameters sent on every request
- `DefaultPaginator` + `CursorPagination`: `page_size` on every request, `page_token` set to the
  previous response's `next_page_token`, and a stop when the token is missing or null
- the per-endpoint filter parameter (`last_updated_after` or `updated_after`) carrying the state
  cursor, or the `start_date`, as epoch seconds
- the state cursor advancing to the latest `updated_at` read
- the merged schema: `id` and `updated_at` keep their pinned types, every other discovered
  top-level key is a nullable string, and an empty endpoint leaves only the pinned fields
- a 401 failing as `config_error` without retries

Each stream's `DynamicSchemaLoader` reads one page from the same endpoint before the sync starts.
That request never carries the incremental filter, while every sync request does, so the mocks
below register the schema read on the bare URL and the sync reads on the URL with the filter.
"""

import logging

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
    get_source,
    page,
    query_params,
    read_stream,
    record,
    record_ids,
    requests_to,
)

from airbyte_cdk.models import FailureType, Status, SyncMode
from airbyte_cdk.test.state_builder import StateBuilder


def _sync_url(stream_name: str, cursor: str) -> str:
    """The stream's URL with the filter parameter a sync request carries."""
    stream = STREAMS[stream_name]
    return f"{stream['url']}?{stream['filter']}={cursor}"


def _sync_requests(request_history, stream_name: str) -> list:
    """Recorded requests to the stream's endpoint that carry the incremental filter."""
    stream = STREAMS[stream_name]
    return [request for request in requests_to(request_history, stream["path"]) if stream["filter"] in query_params(request)]


def _schema_requests(request_history, stream_name: str) -> list:
    """Recorded requests to the stream's endpoint made by the schema loader (no filter)."""
    stream = STREAMS[stream_name]
    return [request for request in requests_to(request_history, stream["path"]) if stream["filter"] not in query_params(request)]


def test_headers_and_default_parameters():
    """Every request sends the API key and version headers, sorts newest first and asks for custom fields."""
    with requests_mock.Mocker() as mocker:
        mocker.get(REQUESTS_URL, json=page([record("r-1", 1718000500)]))
        output = read_stream("requests")

    assert record_ids(output) == ["r-1"]
    data_requests = requests_to(mocker.request_history, REQUESTS_PATH)
    assert data_requests, "expected at least one request against /requests"
    for request in data_requests:
        assert request.headers["Zip-Api-Key"] == API_KEY
        assert request.headers["Zip-Api-Version"] == API_VERSION
        params = query_params(request)
        assert params.get("sort_by") == "updated_at", params
        assert params.get("sort_order") == "desc", params
        assert params.get("include_attributes") == "true", params


def test_api_version_defaults_when_not_configured():
    """A config without `api_version` still sends the header, with the manifest's default."""
    config = {key: value for key, value in CONFIG.items() if key != "api_version"}

    with requests_mock.Mocker() as mocker:
        mocker.get(REQUESTS_URL, json=page([record("r-1", 1718000500)]))
        output = read_stream("requests", config=config)

    assert not output.errors, [error.trace.error.message for error in output.errors]
    for request in requests_to(mocker.request_history, REQUESTS_PATH):
        assert request.headers["Zip-Api-Version"] == "2024-06-06"


def test_pagination():
    """`page_token` carries the previous page's `next_page_token`, and `page_size` is sent on every page."""
    page_1 = page([record("r-1", 1718000500), record("r-2", 1718000400)], next_page_token="tok-2")
    page_2 = page([record("r-3", 1718000300)])

    with requests_mock.Mocker() as mocker:
        mocker.get(REQUESTS_URL, json=page_1)
        mocker.get(_sync_url("requests", START_DATE_EPOCH), [{"json": page_1, "status_code": 200}, {"json": page_2, "status_code": 200}])
        output = read_stream("requests")

    assert record_ids(output) == ["r-1", "r-2", "r-3"]

    sync_requests = _sync_requests(mocker.request_history, "requests")
    assert len(sync_requests) == 2, f"expected 2 paginated requests, got {len(sync_requests)}"

    first_params = query_params(sync_requests[0])
    assert first_params.get("page_size") == "30"
    assert "page_token" not in first_params, f"first request must not carry a page token, got {first_params}"

    second_params = query_params(sync_requests[1])
    assert second_params.get("page_token") == "tok-2", f"second request must resume from the token, got {second_params}"
    assert second_params.get("page_size") == "30"


def test_pagination_stops_on_null_token():
    """A response whose `next_page_token` is present but null must end the read instead of looping."""
    body = {**page([record("r-1", 1718000500)]), "next_page_token": None}

    with requests_mock.Mocker() as mocker:
        mocker.get(REQUESTS_URL, json=body)
        mocker.get(
            _sync_url("requests", START_DATE_EPOCH),
            [
                {"json": body, "status_code": 200},
                # A stop condition that is not null-safe loops on the same page forever. Failing the
                # second request keeps that regression a fast test failure instead of a hung suite.
                {"json": {}, "status_code": 400},
            ],
        )
        output = read_stream("requests")

    assert record_ids(output) == ["r-1"]
    assert len(_sync_requests(mocker.request_history, "requests")) == 1


@pytest.mark.parametrize("stream_name", list(STREAMS))
def test_state_cursor_is_sent_as_the_endpoint_filter(stream_name):
    """Each endpoint gets the saved `updated_at` under its own filter name, with its own page size."""
    stream = STREAMS[stream_name]
    cursor = "1718000000"
    state = StateBuilder().with_stream_state(stream_name, {"updated_at": cursor}).build()

    with requests_mock.Mocker() as mocker:
        mocker.get(stream["url"], json=page([record("x-1", 1718000500)]))
        mocker.get(_sync_url(stream_name, cursor), json=page([record("x-2", 1718000600)]))
        output = read_stream(stream_name, sync_mode=SyncMode.incremental, state=state)

    assert record_ids(output) == ["x-2"]
    sync_requests = _sync_requests(mocker.request_history, stream_name)
    assert len(sync_requests) == 1, f"expected one sync request, got {len(sync_requests)}"
    params = query_params(sync_requests[0])
    assert params.get(stream["filter"]) == cursor, params
    assert params.get("page_size") == stream["page_size"], params
    # The other endpoint's filter name returns HTTP 400 from Zip, so it must never be sent.
    other_filter = "updated_after" if stream["filter"] == "last_updated_after" else "last_updated_after"
    assert other_filter not in params, params


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
    config = {key: value for key, value in CONFIG.items() if key != "start_date"}
    if start_date is not None:
        config["start_date"] = start_date

    with requests_mock.Mocker() as mocker:
        mocker.get(REQUESTS_URL, json=page([]))
        output = read_stream("requests", config=config, sync_mode=SyncMode.incremental)

    assert not output.errors, [error.trace.error.message for error in output.errors]
    sync_requests = _sync_requests(mocker.request_history, "requests")
    assert sync_requests, "expected a sync request against /requests"
    for request in sync_requests:
        assert query_params(request).get("last_updated_after") == expected_epoch


def test_state_advances_to_the_latest_updated_at():
    """After a sync, the stream state holds the largest `updated_at` read, as epoch seconds."""
    with requests_mock.Mocker() as mocker:
        mocker.get(REQUESTS_URL, json=page([record("r-1", 1718000500)]))
        mocker.get(_sync_url("requests", START_DATE_EPOCH), json=page([record("r-1", 1718000500), record("r-2", 1718000400)]))
        output = read_stream("requests", sync_mode=SyncMode.incremental)

    assert record_ids(output) == ["r-1", "r-2"]
    state = output.most_recent_state.stream_state.__dict__
    assert state.get("updated_at") == "1718000500", state


def test_schema_merges_pinned_types_with_discovered_strings():
    """`id` and `updated_at` keep the pinned types; every other key of the first record is a nullable string."""
    with requests_mock.Mocker() as mocker:
        mocker.get(REQUESTS_URL, json=page([record("r-1", 1718000500), record("r-2", 1718000400, extra_key="x")]))
        schema = next(stream for stream in get_source(CONFIG).streams(CONFIG) if stream.name == "requests").get_json_schema()

    properties = schema["properties"]
    assert properties["id"] == {"type": "string"}
    assert properties["updated_at"] == {"type": "integer"}
    for key in ("name", "status", "amount_usd", "created_at", "description"):
        assert properties[key] == {"type": ["null", "string"]}, (key, properties[key])
    # Nested objects and arrays are declared as strings too; they land JSON-serialized.
    assert properties["vendor"] == {"type": ["null", "string"]}
    assert properties["attributes"] == {"type": ["null", "string"]}
    # Only the first record is inspected.
    assert "extra_key" not in properties
    # The CDK's merged schema carries no `additionalProperties`, so undeclared fields are still allowed.
    assert schema.get("additionalProperties") is not False

    schema_requests = _schema_requests(mocker.request_history, "requests")
    assert len(schema_requests) == 1, f"expected one schema read, got {len(schema_requests)}"
    assert "page_token" not in query_params(schema_requests[0])


def test_schema_of_an_empty_endpoint_keeps_the_pinned_fields():
    """When the endpoint returns no records, the schema still declares `id` and `updated_at`."""
    with requests_mock.Mocker() as mocker:
        mocker.get(REQUESTS_URL, json=page([]))
        schema = next(stream for stream in get_source(CONFIG).streams(CONFIG) if stream.name == "requests").get_json_schema()

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


@pytest.mark.parametrize("status_code", [401, 403])
def test_rejected_api_key_is_a_config_error(status_code):
    """A rejected key fails the sync as `config_error` with an actionable message, without retries."""
    with requests_mock.Mocker() as mocker:
        mocker.get(REQUESTS_URL, json={"error": "unauthorized"}, status_code=status_code)
        output = read_stream("requests")

    errors = [message.trace.error for message in output.errors]
    assert errors, "expected the read to emit an error trace"
    assert errors[0].failure_type == FailureType.config_error, errors[0].failure_type
    assert "Zip rejected the API key" in errors[0].message, errors[0].message
    assert len(requests_to(mocker.request_history, REQUESTS_PATH)) == 1, "auth errors must not be retried"
