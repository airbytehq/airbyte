# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Unit tests for `messages`, `activities`, `people`, `segment_memberships` and `esp_suppressions`: time windows and their
lookback, the early stop of the activity log, the people search and hydrate, membership paging and suppression partitions."""

import logging
import time

import pytest
import requests_mock
from _helpers import get_source
from test_error_handling_and_lookback import _API, _FORBIDDEN_MESSAGE, _PRIOR_CURSOR, _START_DATE, _START_EPOCH, _errors
from test_messaging_and_audience_streams import _segment
from test_pagination_region_incremental import _BASE_CONFIG, _read

from airbyte_cdk.models import AirbyteStreamStatus, FailureType, SyncMode
from airbyte_cdk.sources.utils.schema_helpers import check_config_against_spec_or_exit
from airbyte_cdk.test.state_builder import StateBuilder
from airbyte_cdk.utils.traced_exception import AirbyteTracedException


_DAY = 86400
_WINDOW = 30 * _DAY
_SEARCH_URL = f"{_API}/customers"
_HYDRATE_URL = f"{_API}/customers/attributes"
_MATCH_ALL = {"filter": {"and": [{"attribute": {"field": "cio_id", "operator": "exists"}}]}}
_SUPPRESSION_TYPES = ["bounces", "blocks", "spam_reports", "invalid_emails"]
_DOMAINS = ["mail.example.com", "news.example.com"]
# Empty suppression lists come back as null, without a category (live).
_NO_SUPPRESSIONS = {"json": {"suppressions": None}}


def _iso(epoch: int) -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(epoch))


def _message(message_id: str, created: int, **fields) -> dict:
    """A delivery in the live shape: `metrics` holds the time each metric was recorded."""
    return {
        "id": message_id,
        "deduplicate_id": f"{message_id}:{created + 2}",
        "created": created,
        "type": "email",
        "recipient": "person@example.com",
        "customer_id": None,
        "customer_identifiers": {"cio_id": "c0000001", "email": "person@example.com", "id": None},
        "subject": "Welcome",
        "metrics": {"sent": created + 1, "delivered": created + 2},
        "forgotten": False,
        "transactional_message_id": 1,
        "msg_template_id": 1,
        **fields,
    }


def _activity(activity_id: str, timestamp: int) -> dict:
    """An `opened_email` activity in the live shape: `data` holds integer metric times and client details."""
    return {
        "id": activity_id,
        "type": "opened_email",
        "timestamp": timestamp,
        "customer_id": None,
        "customer_identifiers": {"cio_id": "c0000001", "email": "person@example.com"},
        "delivery_id": f"delivery-{activity_id}",
        "delivery_type": "email",
        "data": {"delivery_id": f"delivery-{activity_id}", "opened": timestamp, "ip_address": "192.0.2.1"},
    }


def _identifiers(cio_ids) -> list:
    """Search results in the documented `identifiers` shape."""
    return [{"cio_id": cio_id, "email": f"{cio_id}@example.com", "id": None} for cio_id in cio_ids]


def _customer(cio_id: str) -> dict:
    """One `customers[]` item in the live getPeopleById shape: the spec wraps these fields in `customer`, the API does not."""
    return {
        "attributes": {"cio_id": cio_id, "email": f"{cio_id}@example.com", "plan_name": "premium"},
        "devices": [{"id": f"token-{cio_id}", "platform": "ios", "last_used": _PRIOR_CURSOR}],
        "id": cio_id,
        "identifiers": {"cio_id": cio_id, "email": f"{cio_id}@example.com", "id": None},
        "timestamps": {"cio_id": _PRIOR_CURSOR, "email": _PRIOR_CURSOR},
        "unsubscribed": False,
    }


def _hydrate(request, context) -> dict:
    """Return every requested person, as the API does for ids that exist."""
    return {"customers": [_customer(cio_id) for cio_id in request.json()["ids"]]}


def _member(cio_id: str, person_id=None, email=None) -> dict:
    """One `identifiers` object; `id` or `email` is null when the person has none."""
    return {"cio_id": cio_id, "email": email, "id": person_id}


def _membership(segment_id: int, members: list, next_token="") -> dict:
    """`ids` mirrors `identifiers` as the API sends it: "" for a member without an id, null for an empty segment."""
    ids = [member.get("id") or "" for member in members] or None
    return {"segment_id": segment_id, "ids": ids, "identifiers": members or None, "next": next_token}


def _suppressions(first: int, count: int) -> dict:
    suppressions = [
        {"created": _PRIOR_CURSOR + n, "email": f"person{n:04d}@example.com", "reason": "5.1.1 mailbox does not exist", "status": "550"}
        for n in range(first, first + count)
    ]
    return {"json": {"category": "bounces", "suppressions": suppressions}}


def _ids(output) -> list:
    return [record.record.data["id"] for record in output.records]


def _suppression_keys(output) -> list:
    return sorted(tuple(record.record.data[field] for field in ("suppression_type", "domain", "email")) for record in output.records)


def _requests(mocker, path: str) -> list:
    return [request for request in mocker.request_history if request.path == path]


def _serve_messages(mocker, records: list) -> None:
    """Answer each window with its records, newest first, like the live API: `start_ts` and `end_ts` are both inclusive."""

    def respond(request, context):
        lower, upper = int(request.qs["start_ts"][0]), int(request.qs["end_ts"][0])
        in_window = [record for record in records if lower <= record["created"] <= upper]
        return {"messages": sorted(in_window, key=lambda record: -record["created"]), "next": ""}

    mocker.get(f"{_API}/messages", json=respond)


def _message_queries(mocker) -> list:
    """Query strings of the `messages` requests by window, then page: three workers read windows concurrently."""
    return sorted((request.qs for request in mocker.request_history), key=lambda qs: (int(qs["start_ts"][0]), "start" in qs))


def _window(start_ts: int, end_ts, token=None) -> dict:
    query = {"start_ts": [str(start_ts)], "end_ts": [str(end_ts)], "limit": ["1000"]}
    return {**query, "start": [token]} if token else query


def _serve_activities(mocker, pages: list) -> None:
    """Serve `pages` in order, then a guard page that is served only if the read does not stop."""
    guard = {"json": {"activities": [_activity("guard", _PRIOR_CURSOR)], "next": ""}}
    mocker.get(f"{_API}/activities", [{"json": page} for page in pages] + [guard])


def test_discover_declares_primary_keys_cursors_and_sync_modes():
    """Only `messages` and `activities` have a time field to sync on. The `people` search stays internal, and `activities.data`
    and `messages.metrics` declare no keys: they depend on the activity type or channel, and typed file destinations would drop
    the undeclared ones."""
    full_refresh, incremental = [SyncMode.full_refresh], [SyncMode.full_refresh, SyncMode.incremental]
    expected = {
        "messages": ([["id"]], ["created"], incremental),
        "activities": ([["id"]], ["timestamp"], incremental),
        "people": ([["cio_id"]], None, full_refresh),
        "segment_memberships": ([["segment_id"], ["cio_id"]], None, full_refresh),
        "esp_suppressions": ([["suppression_type"], ["domain"], ["email"]], None, full_refresh),
    }
    catalog = get_source(_BASE_CONFIG).discover(logging.getLogger("airbyte"), _BASE_CONFIG)
    streams = {stream.name: stream for stream in catalog.streams}
    declared = {
        name: (stream.source_defined_primary_key, stream.default_cursor_field, stream.supported_sync_modes)
        for name, stream in streams.items()
    }
    assert {name: declared.get(name) for name in expected} == expected
    assert "people_search" not in streams
    assert "properties" not in streams["activities"].json_schema["properties"]["data"]
    assert "properties" not in streams["messages"].json_schema["properties"]["metrics"]


@pytest.mark.parametrize(
    "field, value, valid",
    [
        ("messages_lookback_days", 1, True),
        ("messages_lookback_days", 30, True),
        ("messages_lookback_days", 180, True),
        ("messages_lookback_days", 0, False),
        ("messages_lookback_days", 181, False),
        ("messages_lookback_days", "30", False),
        ("messages_lookback_days", None, False),
        ("esp_suppression_domains", [], True),
        ("esp_suppression_domains", _DOMAINS, True),
        ("esp_suppression_domains", ["xn--bcher-kva.example"], True),
        ("esp_suppression_domains", ["Mail.example.com"], False),
        ("esp_suppression_domains", ["mail.example.com "], False),
        ("esp_suppression_domains", ["news@mail.example.com"], False),
        ("esp_suppression_domains", ["https://mail.example.com"], False),
        ("esp_suppression_domains", [""], False),
        ("esp_suppression_domains", ["localhost"], False),
        ("esp_suppression_domains", ["mail.example.com", "mail.example.com"], False),
        ("esp_suppression_domains", "mail.example.com", False),
    ],
)
def test_spec_accepts_only_valid_values_of_the_optional_fields(field, value, valid):
    """Both fields are declared and optional; a value outside the range or pattern fails the config check before any request."""
    spec = get_source(_BASE_CONFIG).spec(logging.getLogger("airbyte"))
    assert field in spec.connectionSpecification["properties"]
    assert field not in spec.connectionSpecification["required"]
    config = {**_BASE_CONFIG, field: value}
    if valid:
        check_config_against_spec_or_exit(config, spec)
    else:
        with pytest.raises(AirbyteTracedException):
            check_config_against_spec_or_exit(config, spec)


@pytest.mark.parametrize("stream_name", ["messages", "activities", "people", "segment_memberships", "esp_suppressions"])
def test_403_fails_with_the_key_scope_message(stream_name):
    """A 403 on these endpoints fails with the key scope message, also where the request goes through `substream_error_handler`
    (`segment_memberships`)."""
    forbidden = {"status_code": 403, "json": _errors(403, "forbidden")}
    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_API}/messages", **forbidden)
        mocker.get(f"{_API}/activities", **forbidden)
        mocker.post(_SEARCH_URL, json={"identifiers": _identifiers(["c0000001"]), "next": ""})
        mocker.post(_HYDRATE_URL, **forbidden)
        mocker.get(f"{_API}/segments", json={"segments": [_segment(1, _PRIOR_CURSOR)]})
        mocker.get(f"{_API}/segments/1/membership", **forbidden)
        for suppression_type in _SUPPRESSION_TYPES:
            mocker.get(f"{_API}/esp/suppression/{suppression_type}", **forbidden)
        output = _read(stream_name, {**_BASE_CONFIG, "start_date": _iso(int(time.time()) - _DAY)}, expecting_exception=True)

    errors = [error_message.trace.error for error_message in output.errors]
    assert {error.failure_type for error in errors} == {FailureType.config_error}
    assert {error.message for error in errors if error.stream_descriptor and error.stream_descriptor.name == stream_name} == {
        _FORBIDDEN_MESSAGE
    }
    assert output.get_stream_statuses(stream_name)[-1] == AirbyteStreamStatus.INCOMPLETE
    assert not output.records


def test_messages_reads_30_day_windows_from_start_date():
    """Both window bounds are inclusive (live), so windows meet 1 s apart; the last one ends now, and only the window and `limit`
    are sent."""
    start = int(time.time()) - 45 * _DAY
    records = [_message("m1", start), _message("m2", start + _WINDOW - 1, customer_identifiers=None), _message("m3", start + _WINDOW)]
    with requests_mock.Mocker() as mocker:
        _serve_messages(mocker, records)
        before = int(time.time())
        output = _read("messages", {**_BASE_CONFIG, "start_date": _iso(start)})
        after = int(time.time())

    queries = _message_queries(mocker)
    end = int(queries[-1]["end_ts"][0])
    assert before <= end <= after
    assert queries == [_window(start, start + _WINDOW - 1), _window(start + _WINDOW, end)]
    assert sorted(_ids(output)) == ["m1", "m2", "m3"]
    assert output.get_stream_statuses("messages")[-1] == AirbyteStreamStatus.COMPLETE


def test_messages_follows_next_into_start_within_each_window():
    """Each window pages with its own `next`, sent back case-preserved with the same bounds and `limit`; an empty or missing
    `next` ends the window."""
    start = int(time.time()) - 75 * _DAY
    last_start = start + 2 * _WINDOW
    served = {}

    def respond(request, context):
        """Serve each window's pages in order, then a guard page, so a lost token fails on the ids instead of looping."""
        lower = int(request.qs["start_ts"][0])
        served[lower] = served.get(lower, 0) + 1
        own_token = request.qs.get("start") == [f"Tk/{lower}+=="]
        pages = [
            {"messages": [_message(f"{lower}-1", lower)], "next": f"Tk/{lower}+=="},
            {"messages": [_message(f"{lower}-2" if own_token else "wrong-token", lower)], "next": ""},
        ]
        if lower == last_start:
            pages = [{"messages": [_message("last", lower)]}]
        return pages[served[lower] - 1] if served[lower] <= len(pages) else {"messages": [_message("guard", lower)], "next": ""}

    with requests_mock.Mocker(case_sensitive=True) as mocker:
        mocker.get(f"{_API}/messages", json=respond)
        output = _read("messages", {**_BASE_CONFIG, "start_date": _iso(start)})

    queries = _message_queries(mocker)
    assert queries == [
        _window(start, start + _WINDOW - 1),
        _window(start, start + _WINDOW - 1, f"Tk/{start}+=="),
        _window(start + _WINDOW, last_start - 1),
        _window(start + _WINDOW, last_start - 1, f"Tk/{start + _WINDOW}+=="),
        _window(last_start, queries[-1]["end_ts"][0]),
    ]
    assert sorted(_ids(output)) == sorted([f"{start}-1", f"{start}-2", f"{start + _WINDOW}-1", f"{start + _WINDOW}-2", "last"])


def test_messages_resume_rereads_30_days_before_the_saved_cursor():
    """Metrics land after a delivery is created, so a resumed read starts the default 30 days before the saved cursor and
    re-emits those deliveries with their new metrics; the state moves to the newest `created`."""
    cursor = int(time.time()) - _DAY
    records = [
        _message("before-lookback", cursor - _WINDOW - 1),
        _message("re-read", cursor - _WINDOW, metrics={"sent": cursor - _WINDOW + 1, "opened": cursor + 30}),
        _message("at-cursor", cursor),
        _message("new", cursor + 5),
    ]
    state = StateBuilder().with_stream_state("messages", {"created": str(cursor)}).build()
    with requests_mock.Mocker() as mocker:
        _serve_messages(mocker, records)
        output = _read("messages", _BASE_CONFIG, SyncMode.incremental, state)

    queries = _message_queries(mocker)
    assert queries[0] == _window(cursor - _WINDOW, cursor - 1)
    assert [query["start_ts"] for query in queries[1:]] == [[str(cursor)]]
    emitted = {record.record.data["id"]: record.record.data for record in output.records}
    assert sorted(emitted) == ["at-cursor", "new", "re-read"]
    assert emitted["re-read"]["metrics"]["opened"] == cursor + 30
    assert int(output.most_recent_state.stream_state.created) == cursor + 5


@pytest.mark.parametrize(
    "lookback_days, start_date_days, window_start_days",
    [(None, None, [30, 0]), (7, None, [7]), (90, None, [90, 60, 30, 0]), (None, 3, [3])],
    ids=["default_30", "7", "90", "start_date_floors_the_lookback"],
)
def test_messages_lookback_days_moves_the_first_window(lookback_days, start_date_days, window_start_days):
    """`messages_lookback_days` sets how far before the saved cursor a resumed read starts, in 30-day windows; the Start Date
    floors it. A read without records keeps the saved cursor."""
    cursor = int(time.time()) - _DAY
    config = dict(_BASE_CONFIG)
    if lookback_days:
        config["messages_lookback_days"] = lookback_days
    if start_date_days:
        config["start_date"] = _iso(cursor - start_date_days * _DAY)
    state = StateBuilder().with_stream_state("messages", {"created": str(cursor)}).build()
    with requests_mock.Mocker() as mocker:
        _serve_messages(mocker, [])
        output = _read("messages", config, SyncMode.incremental, state)

    assert [int(query["start_ts"][0]) for query in _message_queries(mocker)] == [cursor - days * _DAY for days in window_start_days]
    assert int(output.most_recent_state.stream_state.created) == cursor


@pytest.mark.parametrize("messages", [[], None], ids=["empty", "null"])
def test_messages_empty_windows_complete_without_records(messages):
    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_API}/messages", json={"messages": messages, "next": ""})
        output = _read("messages", {**_BASE_CONFIG, "start_date": _iso(int(time.time()) - 45 * _DAY)})

    assert not output.records
    assert not output.errors
    assert mocker.call_count == 2
    assert output.get_stream_statuses("messages")[-1] == AirbyteStreamStatus.COMPLETE


def test_messages_without_start_date_reads_contiguous_windows_from_1970():
    """The first window is `start_ts=0&end_ts=2591999` (200 and empty live). The windows are listed without requests: reading
    about 690 of them takes over a minute under the 10 requests per second budget."""
    stream = next(stream for stream in get_source(_BASE_CONFIG).streams(_BASE_CONFIG) if stream.name == "messages")
    before = int(time.time())
    windows = [(int(window["start_time"]), int(window["end_time"])) for window in stream.cursor.stream_slices()]
    after = int(time.time())

    assert windows[0] == (0, _WINDOW - 1)
    assert all(end == start + _WINDOW - 1 for start, end in windows[:-1])
    assert all(next_start == end + 1 for (_, end), (next_start, _) in zip(windows, windows[1:]))
    assert before <= windows[-1][1] <= after


def test_messages_future_start_date_reads_one_window_at_now():
    """`max_datetime` caps a future Start Date at now: one window whose bounds are both now (equal bounds return 200 live), and
    the future date is never saved as the cursor."""
    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_API}/messages", json={"messages": [], "next": ""})
        before = int(time.time())
        output = _read("messages", {**_BASE_CONFIG, "start_date": "2099-01-01T00:00:00Z"}, SyncMode.incremental)
        after = int(time.time())

    [query] = _message_queries(mocker)
    assert before <= int(query["start_ts"][0]) <= int(query["end_ts"][0]) <= after
    assert int(output.most_recent_state.stream_state.created) <= after
    assert output.get_stream_statuses("messages")[-1] == AirbyteStreamStatus.COMPLETE


def test_messages_start_date_before_1970_starts_at_0():
    """`min_datetime` keeps `start_ts` at 0 or later, the first window verified live, instead of sending negative times."""
    with requests_mock.Mocker() as mocker:
        _serve_messages(mocker, [])
        _read("messages", {**_BASE_CONFIG, "start_date": "1900-01-01T00:00:00Z"})

    assert _message_queries(mocker)[0] == _window(0, 2591999)


def test_activities_start_date_in_year_1_reads_normally():
    """`min_datetime` also keeps the window math in range: without it, year 1 minus the lookback overflows before any request."""
    now = int(time.time())
    with requests_mock.Mocker() as mocker:
        _serve_activities(mocker, [{"activities": [_activity("a1", now - 600)], "next": ""}])
        output = _read("activities", {**_BASE_CONFIG, "start_date": "0001-01-01T00:00:00Z"}, SyncMode.incremental)

    assert _ids(output) == ["a1"]


def test_messages_reads_past_an_empty_page_that_carries_next():
    """Only an empty `next` ends a window: an empty page that still carries a token is not the last one."""
    start = int(time.time()) - 10 * _DAY
    pages = [{"json": {"messages": [], "next": "MTAwMA=="}}, {"json": {"messages": [_message("m1", start)], "next": ""}}]
    with requests_mock.Mocker(case_sensitive=True) as mocker:
        mocker.get(f"{_API}/messages", pages)
        output = _read("messages", {**_BASE_CONFIG, "start_date": _iso(start)})

    assert _ids(output) == ["m1"]
    assert [request.qs.get("start") for request in mocker.request_history] == [None, ["MTAwMA=="]]


def test_activities_sends_deleted_true_and_follows_next_into_start():
    """Every request asks for deleted people's activities too (live, the same list), with the maximum page size."""
    pages = [
        {"activities": [_activity("a3", _PRIOR_CURSOR + 3), _activity("a2", _PRIOR_CURSOR + 2)], "next": "900000000000000014"},
        {"activities": [_activity("a1", _PRIOR_CURSOR + 1)], "next": "900000000000000013"},
        {"activities": [], "next": ""},
    ]
    with requests_mock.Mocker() as mocker:
        _serve_activities(mocker, pages)
        output = _read("activities", _BASE_CONFIG)

    assert _ids(output) == ["a3", "a2", "a1"]
    assert [request.qs for request in mocker.request_history] == [
        {"deleted": ["true"], "limit": ["100"]},
        {"deleted": ["true"], "limit": ["100"], "start": ["900000000000000014"]},
        {"deleted": ["true"], "limit": ["100"], "start": ["900000000000000013"]},
    ]
    assert output.get_stream_statuses("activities")[-1] == AirbyteStreamStatus.COMPLETE


@pytest.mark.parametrize("last_page", [{"next": ""}, {"next": None}, {}], ids=["empty", "null", "absent"])
def test_activities_stops_when_next_is_empty(last_page):
    with requests_mock.Mocker() as mocker:
        _serve_activities(mocker, [{"activities": [_activity("a1", _PRIOR_CURSOR)], **last_page}])
        output = _read("activities", _BASE_CONFIG)

    assert _ids(output) == ["a1"]
    assert mocker.call_count == 1


@pytest.mark.parametrize("activities", [[], None], ids=["empty", "null"])
def test_activities_stops_on_an_empty_page_even_with_a_next_token(activities):
    pages = [
        {"activities": [_activity("a1", _PRIOR_CURSOR)], "next": "900000000000000014"},
        {"activities": activities, "next": "900000000000000013"},
    ]
    with requests_mock.Mocker() as mocker:
        _serve_activities(mocker, pages)
        output = _read("activities", _BASE_CONFIG)

    assert _ids(output) == ["a1"]
    assert mocker.call_count == 2


def test_activities_drops_activities_before_start_date_and_stops_at_the_first_page_before_it():
    pages = [
        {"activities": [_activity("a3", _START_EPOCH + 1), _activity("a2", _START_EPOCH)], "next": "900000000000000014"},
        {"activities": [_activity("a1", _START_EPOCH - 1)], "next": "900000000000000013"},
    ]
    with requests_mock.Mocker() as mocker:
        _serve_activities(mocker, pages)
        output = _read("activities", {**_BASE_CONFIG, "start_date": _START_DATE})

    assert _ids(output) == ["a3", "a2"]
    assert mocker.call_count == 2


def test_activities_resume_stops_at_the_first_page_with_no_activity_in_the_lookback_window():
    """Activities come newest first (live), so the read ends at the first page with none at or after the saved cursor minus one
    hour. A single older activity does not end it: a2 follows a1. The state moves to the newest timestamp."""
    pages = [
        {"activities": [_activity("a5", _PRIOR_CURSOR + 10), _activity("a4", _PRIOR_CURSOR)], "next": "900000000000000016"},
        {"activities": [_activity("a3", _PRIOR_CURSOR - 3600), _activity("a1", _PRIOR_CURSOR - 3601)], "next": "900000000000000014"},
        {"activities": [_activity("a2", _PRIOR_CURSOR - 1800)], "next": "900000000000000013"},
        {"activities": [_activity("a0", _PRIOR_CURSOR - 7200)], "next": "900000000000000012"},
    ]
    state = StateBuilder().with_stream_state("activities", {"timestamp": str(_PRIOR_CURSOR)}).build()
    with requests_mock.Mocker() as mocker:
        _serve_activities(mocker, pages)
        output = _read("activities", _BASE_CONFIG, SyncMode.incremental, state)

    assert _ids(output) == ["a5", "a4", "a3", "a2"]
    assert mocker.call_count == 4
    assert int(output.most_recent_state.stream_state.timestamp) == _PRIOR_CURSOR + 10


def test_activities_reads_past_a_page_of_future_dated_activities():
    """Activities dated after now are dropped and leave the state alone, but a page of them does not end the read: the next
    page's new activity is emitted, and the read stops at the following page of older activities."""
    now = int(time.time())
    pages = [
        {"activities": [_activity("future-2", now + _DAY), _activity("future-1", now + 3600)], "next": "900000000000000019"},
        {"activities": [_activity("new", now - 600)], "next": "900000000000000018"},
        {"activities": [_activity("old", now - 10 * _DAY)], "next": "900000000000000017"},
    ]
    state = StateBuilder().with_stream_state("activities", {"timestamp": str(now - _DAY)}).build()
    with requests_mock.Mocker() as mocker:
        _serve_activities(mocker, pages)
        output = _read("activities", _BASE_CONFIG, SyncMode.incremental, state)

    assert _ids(output) == ["new"]
    assert mocker.call_count == 3
    assert int(output.most_recent_state.stream_state.timestamp) == now - 600
    assert output.get_stream_statuses("activities")[-1] == AirbyteStreamStatus.COMPLETE


def test_activities_future_start_date_reads_one_page_and_never_saves_the_future_date():
    """`max_datetime` caps a future Start Date at now: one request, no records, and a cursor at or before now, so correcting the
    date later resumes the stream instead of leaving it behind a cursor in 2099."""
    now = int(time.time())
    with requests_mock.Mocker() as mocker:
        _serve_activities(mocker, [{"activities": [_activity("a1", now - 600)], "next": "900000000000000013"}])
        before = int(time.time())
        output = _read("activities", {**_BASE_CONFIG, "start_date": "2099-01-01T00:00:00Z"}, SyncMode.incremental)
        after = int(time.time())

    assert mocker.call_count == 1
    assert not output.records
    assert before <= int(output.most_recent_state.stream_state.timestamp) <= after
    assert output.get_stream_statuses("activities")[-1] == AirbyteStreamStatus.COMPLETE


def test_people_searches_everyone_and_hydrates_100_cio_ids_per_request():
    """One match-all search with `limit=1000`, then `id_type=cio_id` bodies of at most 100 ids, in search order."""
    cio_ids = [f"c{n:07d}" for n in range(250)]
    with requests_mock.Mocker() as mocker:
        mocker.post(_SEARCH_URL, json={"identifiers": _identifiers(cio_ids), "ids": [""] * 250, "next": ""})
        mocker.post(_HYDRATE_URL, json=_hydrate)
        output = _read("people", _BASE_CONFIG)

    [search] = _requests(mocker, "/v1/customers")
    assert (search.json(), search.qs) == (_MATCH_ALL, {"limit": ["1000"]})
    hydrates = _requests(mocker, "/v1/customers/attributes")
    assert all(request.qs == {"id_type": ["cio_id"]} for request in hydrates)
    groups = sorted((request.json()["ids"] for request in hydrates), key=lambda ids: ids[0])
    assert [len(ids) for ids in groups] == [100, 100, 50]
    assert [cio_id for ids in groups for cio_id in ids] == cio_ids
    assert sorted(record.record.data["cio_id"] for record in output.records) == cio_ids
    assert output.get_stream_statuses("people")[-1] == AirbyteStreamStatus.COMPLETE


def test_people_search_follows_next_into_start_and_groups_across_pages():
    """`next` goes back case-preserved as `start` with the same body, and a group of 100 spans search pages."""
    first, second = [f"a{n:07d}" for n in range(150)], [f"b{n:07d}" for n in range(50)]
    pages = [
        {"json": {"identifiers": _identifiers(first), "next": "MDoxNTA="}},
        {"json": {"identifiers": _identifiers(second), "next": ""}},
    ]
    with requests_mock.Mocker(case_sensitive=True) as mocker:
        mocker.post(_SEARCH_URL, pages)
        mocker.post(_HYDRATE_URL, json=_hydrate)
        output = _read("people", _BASE_CONFIG)

    searches = _requests(mocker, "/v1/customers")
    assert [request.qs for request in searches] == [{"limit": ["1000"]}, {"limit": ["1000"], "start": ["MDoxNTA="]}]
    assert all(request.json() == _MATCH_ALL for request in searches)
    groups = sorted((request.json()["ids"] for request in _requests(mocker, "/v1/customers/attributes")), key=lambda ids: ids[0])
    assert groups == [first[:100], first[100:] + second]
    assert len(output.records) == 200


def test_people_keeps_no_set_of_every_cio_id():
    """`deduplicate: false`: a cio_id listed again on a later search page is fetched again; the router keeps no set of every
    cio_id of the sync."""
    first = [f"a{n:07d}" for n in range(100)]
    second = [first[-1], "b0000000"]
    pages = [
        {"json": {"identifiers": _identifiers(first), "next": "MDoxMDA="}},
        {"json": {"identifiers": _identifiers(second), "next": ""}},
    ]
    with requests_mock.Mocker() as mocker:
        mocker.post(_SEARCH_URL, pages)
        mocker.post(_HYDRATE_URL, json=_hydrate)
        _read("people", _BASE_CONFIG)

    groups = sorted((request.json()["ids"] for request in _requests(mocker, "/v1/customers/attributes")), key=lambda ids: ids[0])
    assert groups == [first, second]


def test_people_cio_id_comes_from_identifiers_or_attributes_and_stays_a_string():
    """The spec examples carry `cio_id` only in `attributes`; digit-like ids stay strings, and a profile without one gets ""."""
    attributes_only = _customer("30000001")
    del attributes_only["identifiers"]
    neither = _customer("c0000004")
    del neither["identifiers"], neither["attributes"]["cio_id"]
    with requests_mock.Mocker() as mocker:
        mocker.post(_SEARCH_URL, json={"identifiers": _identifiers(["c0000001", "30000001", "30e00001", "c0000004"]), "next": ""})
        mocker.post(_HYDRATE_URL, json={"customers": [_customer("c0000001"), attributes_only, _customer("30e00001"), neither]})
        output = _read("people", _BASE_CONFIG)

    assert {record.record.data["attributes"]["email"]: record.record.data["cio_id"] for record in output.records} == {
        "c0000001@example.com": "c0000001",
        "30000001@example.com": "30000001",
        "30e00001@example.com": "30e00001",
        "c0000004@example.com": "",
    }


def test_people_skips_ids_missing_from_the_hydrate_response():
    """The API omits ids that no longer exist."""
    with requests_mock.Mocker() as mocker:
        mocker.post(_SEARCH_URL, json={"identifiers": _identifiers(["c1", "c2", "c3"]), "next": ""})
        mocker.post(_HYDRATE_URL, json={"customers": [_customer("c1"), _customer("c3")]})
        output = _read("people", _BASE_CONFIG)

    assert sorted(record.record.data["cio_id"] for record in output.records) == ["c1", "c3"]
    assert not output.errors
    assert output.get_stream_statuses("people")[-1] == AirbyteStreamStatus.COMPLETE


def test_people_hydrate_404_fails_the_sync():
    """getPeopleById omits unknown ids with 200 (live), so a 404 is not a deleted group: the sync fails after one attempt instead
    of dropping up to 100 people from a stream that mirrors the workspace."""
    cio_ids = [f"c{n:07d}" for n in range(150)]

    def hydrate(request, context):
        if cio_ids[0] in request.json()["ids"]:
            context.status_code = 404
            return _errors(404, "not found")
        return _hydrate(request, context)

    with requests_mock.Mocker() as mocker:
        mocker.post(_SEARCH_URL, json={"identifiers": _identifiers(cio_ids), "next": ""})
        mocker.post(_HYDRATE_URL, json=hydrate)
        output = _read("people", _BASE_CONFIG, expecting_exception=True)

    errors = [message.trace.error for message in output.errors]
    assert {error.failure_type for error in errors if error.stream_descriptor and error.stream_descriptor.name == "people"} == {
        FailureType.system_error
    }
    assert len([request for request in _requests(mocker, "/v1/customers/attributes") if cio_ids[0] in request.json()["ids"]]) == 1
    assert output.get_stream_statuses("people")[-1] == AirbyteStreamStatus.INCOMPLETE


def test_people_sends_no_hydrate_request_when_the_search_is_empty():
    with requests_mock.Mocker() as mocker:
        mocker.post(_SEARCH_URL, json={"identifiers": None, "ids": None, "next": ""})
        mocker.post(_HYDRATE_URL, json=_hydrate)
        output = _read("people", _BASE_CONFIG)

    assert not _requests(mocker, "/v1/customers/attributes")
    assert not output.records
    assert output.get_stream_statuses("people")[-1] == AirbyteStreamStatus.COMPLETE


def test_segment_memberships_emits_identifiers_with_an_integer_segment_id():
    """Records come from `identifiers` (never `ids`), each gets its segment's id, and every request asks for 30000 members."""
    members_7 = [
        _member("a1", "1", "one@example.com"),
        _member("a2", None, "email-only@example.com"),
        {"cio_id": "a3", "id": "3"},  # the "id only" variant has no email key
    ]
    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_API}/segments", json={"segments": [_segment(7, _PRIOR_CURSOR), _segment(9, _PRIOR_CURSOR)]})
        mocker.get(f"{_API}/segments/7/membership", json=_membership(7, members_7))
        mocker.get(f"{_API}/segments/9/membership", json=_membership(9, [_member("a1", "1", "one@example.com")]))
        output = _read("segment_memberships", _BASE_CONFIG)

    # The serialized record omits null values, so a null id or email reads back as missing.
    records = sorted(tuple(record.record.data.get(field) for field in ("segment_id", "cio_id", "id", "email")) for record in output.records)
    assert records == [
        (7, "a1", "1", "one@example.com"),
        (7, "a2", None, "email-only@example.com"),
        (7, "a3", "3", None),
        (9, "a1", "1", "one@example.com"),
    ]
    assert sorted((request.path, request.query) for request in mocker.request_history if request.path.endswith("/membership")) == [
        ("/v1/segments/7/membership", "limit=30000"),
        ("/v1/segments/9/membership", "limit=30000"),
    ]
    assert output.get_stream_statuses("segment_memberships")[-1] == AirbyteStreamStatus.COMPLETE


def test_segment_memberships_follows_next_into_start_until_next_is_empty():
    """`next` goes back unchanged as `start` (base64 tokens keep their case and padding) until a page returns an empty `next`."""
    pages = [
        _membership(5, [_member("b1", "12")], "MDo1"),
        _membership(5, [_member("b2", "59")], "MDo2MQ=="),
        _membership(5, [], ""),
        _membership(5, [_member("guard", "99")], ""),  # served only if the read does not stop
    ]
    with requests_mock.Mocker(case_sensitive=True) as mocker:
        mocker.get(f"{_API}/segments", json={"segments": [_segment(5, _PRIOR_CURSOR)]})
        mocker.get(f"{_API}/segments/5/membership", [{"json": page} for page in pages])
        output = _read("segment_memberships", _BASE_CONFIG)

    assert [record.record.data["cio_id"] for record in output.records] == ["b1", "b2"]
    assert [request.qs for request in _requests(mocker, "/v1/segments/5/membership")] == [
        {"limit": ["30000"]},
        {"limit": ["30000"], "start": ["MDo1"]},
        {"limit": ["30000"], "start": ["MDo2MQ=="]},
    ]


@pytest.mark.parametrize("last_page", [{"next": ""}, {"next": None}, {}], ids=["empty", "null", "absent"])
def test_segment_memberships_stops_when_next_is_empty(last_page):
    page = {key: value for key, value in _membership(7, [_member("a1", "1")]).items() if key != "next"}
    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_API}/segments", json={"segments": [_segment(7, _PRIOR_CURSOR)]})
        mocker.get(f"{_API}/segments/7/membership", [{"json": {**page, **last_page}}, {"json": _membership(7, [_member("guard")])}])
        output = _read("segment_memberships", _BASE_CONFIG)

    assert [record.record.data["cio_id"] for record in output.records] == ["a1"]
    assert len(_requests(mocker, "/v1/segments/7/membership")) == 1


@pytest.mark.parametrize("identifiers", [None, []], ids=["null", "empty"])
def test_segment_memberships_reads_an_empty_segment_as_no_records(identifiers):
    """Live empty segments return `identifiers: null`, `ids: null` and `next: ""`."""
    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_API}/segments", json={"segments": [_segment(3, _PRIOR_CURSOR)]})
        mocker.get(f"{_API}/segments/3/membership", json={"segment_id": 3, "ids": None, "identifiers": identifiers, "next": ""})
        output = _read("segment_memberships", _BASE_CONFIG)

    assert not output.records
    assert not output.errors
    assert output.get_stream_statuses("segment_memberships")[-1] == AirbyteStreamStatus.COMPLETE
    assert len(_requests(mocker, "/v1/segments/3/membership")) == 1


def test_segment_memberships_reads_past_an_empty_page_that_carries_next():
    """Only an empty `next` ends a segment: the token is a position, so an empty page that still carries one is not the end."""
    with requests_mock.Mocker(case_sensitive=True) as mocker:
        mocker.get(f"{_API}/segments", json={"segments": [_segment(5, _PRIOR_CURSOR)]})
        mocker.get(
            f"{_API}/segments/5/membership",
            [{"json": _membership(5, [], "MTow")}, {"json": _membership(5, [_member("c1", "70000")], "")}],
        )
        output = _read("segment_memberships", _BASE_CONFIG)

    assert [record.record.data["cio_id"] for record in output.records] == ["c1"]


def test_segment_memberships_skips_404_for_a_segment_deleted_mid_sync():
    """A missing segment returns 404 (live); `substream_error_handler` skips it without a retry and reads the other segments."""
    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_API}/segments", json={"segments": [_segment(1, _PRIOR_CURSOR), _segment(2, _PRIOR_CURSOR)]})
        mocker.get(f"{_API}/segments/1/membership", status_code=404, json=_errors(404, "not found"))
        mocker.get(f"{_API}/segments/2/membership", json=_membership(2, [_member("c2", "2")]))
        output = _read("segment_memberships", _BASE_CONFIG)

    assert [(record.record.data["segment_id"], record.record.data["cio_id"]) for record in output.records] == [(2, "c2")]
    assert not output.errors
    assert output.get_stream_statuses("segment_memberships")[-1] == AirbyteStreamStatus.COMPLETE
    assert sorted(request.path for request in mocker.request_history) == [
        "/v1/segments",
        "/v1/segments/1/membership",
        "/v1/segments/2/membership",
    ]


def test_segment_memberships_reads_segments_updated_before_start_date():
    """The inline `segments` parent has no cursor, so the Start Date never hides a segment's members."""
    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_API}/segments", json={"segments": [_segment(1, _START_EPOCH - _DAY)]})
        mocker.get(f"{_API}/segments/1/membership", json=_membership(1, [_member("c1", "1")]))
        output = _read("segment_memberships", {**_BASE_CONFIG, "start_date": _START_DATE})

    assert [record.record.data["cio_id"] for record in output.records] == ["c1"]


@pytest.mark.parametrize("domains", [None, []], ids=["field_absent", "empty_list"])
def test_esp_suppressions_without_domains_reads_each_type_once_without_a_domain_parameter(domains):
    """No configured domain still gives one partition per type, and the empty fallback value is never sent."""
    config = _BASE_CONFIG if domains is None else {**_BASE_CONFIG, "esp_suppression_domains": domains}
    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_API}/esp/suppression/bounces", [_suppressions(1, 2)])
        mocker.get(f"{_API}/esp/suppression/spam_reports", [_suppressions(1, 1)])
        mocker.get(f"{_API}/esp/suppression/blocks", [_NO_SUPPRESSIONS])
        mocker.get(f"{_API}/esp/suppression/invalid_emails", [_NO_SUPPRESSIONS])
        output = _read("esp_suppressions", config)

    assert {t: [request.qs for request in _requests(mocker, f"/v1/esp/suppression/{t}")] for t in _SUPPRESSION_TYPES} == {
        t: [{"limit": ["1000"]}] for t in _SUPPRESSION_TYPES
    }
    assert _suppression_keys(output) == [
        ("bounces", "", "person0001@example.com"),
        ("bounces", "", "person0002@example.com"),
        ("spam_reports", "", "person0001@example.com"),
    ]
    assert output.get_stream_statuses("esp_suppressions")[-1] == AirbyteStreamStatus.COMPLETE


def test_esp_suppressions_split_every_type_by_configured_domain():
    """Each type is read once per domain; an address suppressed on two domains gives two keys."""
    with requests_mock.Mocker() as mocker:
        for suppression_type in _SUPPRESSION_TYPES:
            mocker.get(f"{_API}/esp/suppression/{suppression_type}", [_NO_SUPPRESSIONS])
        for domain in _DOMAINS:
            mocker.get(f"{_API}/esp/suppression/bounces?domain={domain}", [_suppressions(1, 1)])
        output = _read("esp_suppressions", {**_BASE_CONFIG, "esp_suppression_domains": _DOMAINS})

    assert {
        t: sorted(request.qs["domain"][0] for request in _requests(mocker, f"/v1/esp/suppression/{t}")) for t in _SUPPRESSION_TYPES
    } == {t: _DOMAINS for t in _SUPPRESSION_TYPES}
    assert all(request.qs["limit"] == ["1000"] and "offset" not in request.qs for request in mocker.request_history)
    assert _suppression_keys(output) == [("bounces", domain, "person0001@example.com") for domain in _DOMAINS]


@pytest.mark.parametrize(
    "domains, last_page, expected_records",
    [(None, _suppressions(1001, 1), 1001), (None, _NO_SUPPRESSIONS, 1000), (["mail.example.com"], _suppressions(1001, 1), 1001)],
    ids=["short_last_page", "full_page_then_null", "domain_on_every_page"],
)
def test_esp_suppressions_page_by_offset_until_a_page_is_shorter_than_the_limit(domains, last_page, expected_records):
    """The first request sends only `limit`, the next `offset=1000`; a short page or a null list (live past the end) ends it."""
    config = _BASE_CONFIG if domains is None else {**_BASE_CONFIG, "esp_suppression_domains": domains}
    domain_query = {"domain": domains} if domains else {}
    with requests_mock.Mocker() as mocker:
        for suppression_type in _SUPPRESSION_TYPES:
            mocker.get(f"{_API}/esp/suppression/{suppression_type}", [_NO_SUPPRESSIONS])
        # The guard page is served only if the read asks past the end, so a missing stop fails on the count.
        mocker.get(f"{_API}/esp/suppression/bounces", [_suppressions(1, 1000), last_page, _suppressions(9000, 1)])
        output = _read("esp_suppressions", config)

    assert [request.qs for request in _requests(mocker, "/v1/esp/suppression/bounces")] == [
        {"limit": ["1000"], **domain_query},
        {"limit": ["1000"], "offset": ["1000"], **domain_query},
    ]
    assert len(output.records) == expected_records
    assert {record.record.data["domain"] for record in output.records} == {domains[0] if domains else ""}
    assert output.get_stream_statuses("esp_suppressions")[-1] == AirbyteStreamStatus.COMPLETE
