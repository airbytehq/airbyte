# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Unit tests for `broadcasts`, `broadcast_actions`, `newsletter_variants`, `transactional_messages`, `sender_identities`,
`segments` and `segment_usage`."""

import logging
from operator import itemgetter

import pytest
import requests_mock
from _helpers import get_source
from test_error_handling_and_lookback import _API, _PRIOR_CURSOR, _START_DATE, _START_EPOCH, _errors
from test_pagination_region_incremental import _BASE_CONFIG, _newsletter, _read

from airbyte_cdk.models import AirbyteStreamStatus, SyncMode
from airbyte_cdk.test.state_builder import StateBuilder


def _broadcast(broadcast_id: int, updated: int) -> dict:
    return {
        "id": broadcast_id,
        "name": f"broadcast-{broadcast_id}",
        "type": "triggered_broadcast",
        "state": "running",
        "active": True,
        "created": updated,
        "updated": updated,
        "tags": ["onboarding"],
        "actions": [{"id": broadcast_id * 10, "type": "email"}],
    }


def _broadcast_action(action_id, updated: int) -> dict:
    """No `broadcast_id`: the spec declares it but no live response confirms it, so the stream adds it from the partition."""
    return {"id": action_id, "type": "email", "name": f"action-{action_id}", "language": "", "created": updated, "updated": updated}


def _transactional_message(message_id: int, updated_at: int) -> dict:
    return {
        "id": message_id,
        "name": f"template-{message_id}",
        "trigger_name": f"trigger-{message_id}",
        "send_to_unsubscribed": True,
        "link_tracking": True,
        "open_tracking": True,
        "hide_message_body": False,
        "queue_drafts": False,
        "created_at": updated_at,
        "updated_at": updated_at,
    }


def _segment(segment_id: int, updated_at: int) -> dict:
    return {
        "id": segment_id,
        "name": f"segment-{segment_id}",
        "type": "dynamic",
        "state": "finished",
        "tags": ["Sample"],
        "conditions": {"and": [{"attribute": {"field": "plan", "operator": "eq", "value": "pro"}}]},
        "created_at": updated_at,
        "updated_at": updated_at,
    }


def _variant(variant_id: int, newsletter_id: int, language: str = "") -> dict:
    """Variants carry `newsletter_id` and `from_id` (a sender identity id) natively."""
    return {
        "id": variant_id,
        "newsletter_id": newsletter_id,
        "from_id": newsletter_id,
        "language": language,
        "type": "email",
        "subject": "hi",
    }


def _sender(sender_id: int, hidden: bool = False) -> dict:
    return {
        "id": sender_id,
        "name": f"sender-{sender_id}",
        "email": f"sender{sender_id}@example.com",
        "template_type": "email",
        "hidden": hidden,
    }


def _used_by(segment_id: int, campaigns: tuple = (), draft_newsletters: tuple = ()) -> dict:
    return {
        "used_by": {
            "segment_id": segment_id,
            "campaigns": list(campaigns),
            "draft_newsletters": list(draft_newsletters),
            "sent_newsletters": [],
        }
    }


# Stream >> (request path, records key, cursor field, record builder)
_LISTS = {
    "broadcasts": ("broadcasts", "broadcasts", "updated", _broadcast),
    "transactional_messages": ("transactional", "messages", "updated_at", _transactional_message),
    "segments": ("segments", "segments", "updated_at", _segment),
}
# Stream >> (parent path and records key, parent builder, child path, child response for a parent id, partition field)
_SUBSTREAMS = {
    "broadcast_actions": (
        "broadcasts",
        _broadcast,
        "broadcasts/{}/actions",
        lambda parent_id: {"actions": [_broadcast_action(parent_id * 10, _PRIOR_CURSOR)]},
        "broadcast_id",
    ),
    "newsletter_variants": (
        "newsletters",
        _newsletter,
        "newsletters/{}/contents",
        lambda parent_id: {"contents": [_variant(parent_id * 10, parent_id)]},
        "newsletter_id",
    ),
    "segment_usage": ("segments", _segment, "segments/{}/used_by", _used_by, "segment_id"),
}
_SENDERS_URL = f"{_API}/sender_identities"
# Served only if the read asks for a page past the end, so a missing stop fails on the ids instead of looping.
_GUARD_PAGE = {"json": {"sender_identities": [_sender(99)], "next": ""}}


def test_discover_declares_primary_keys_cursors_and_sync_modes():
    """Keys follow the vendor spec; streams without a usable cursor are full refresh only."""
    full_refresh, incremental = [SyncMode.full_refresh], [SyncMode.full_refresh, SyncMode.incremental]
    expected = {
        "broadcasts": ([["id"]], ["updated"], incremental),
        "broadcast_actions": ([["broadcast_id"], ["id"]], ["updated"], incremental),
        "newsletter_variants": ([["newsletter_id"], ["id"]], None, full_refresh),
        "transactional_messages": ([["id"]], ["updated_at"], incremental),
        "sender_identities": ([["id"]], None, full_refresh),
        "segments": ([["id"]], ["updated_at"], incremental),
        "segment_usage": ([["segment_id"]], None, full_refresh),
    }
    catalog = get_source(_BASE_CONFIG).discover(logging.getLogger("airbyte"), _BASE_CONFIG)
    declared = {
        stream.name: (stream.source_defined_primary_key, stream.default_cursor_field, stream.supported_sync_modes)
        for stream in catalog.streams
    }
    assert {name: declared.get(name) for name in expected} == expected


@pytest.mark.parametrize("stream_name", list(_LISTS))
def test_list_stream_reads_one_unpaged_request_and_drops_records_before_start_date(stream_name):
    """One request without query parameters returns the whole list; the client-side cursor drops records before the Start Date."""
    path, records_key, _, build = _LISTS[stream_name]
    records = [build(1, _START_EPOCH - 1), build(2, _START_EPOCH), build(3, _START_EPOCH + 1)]
    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_API}/{path}", json={records_key: records})
        output = _read(stream_name, {**_BASE_CONFIG, "start_date": _START_DATE})

    assert [record.record.data for record in output.records] == records[1:]
    assert [(request.path, request.qs) for request in mocker.request_history] == [(f"/v1/{path}", {})]
    assert output.get_stream_statuses(stream_name)[-1] == AirbyteStreamStatus.COMPLETE


@pytest.mark.parametrize("stream_name", list(_LISTS))
def test_list_stream_resumes_from_state_with_one_hour_lookback(stream_name):
    """A resumed read re-emits records down to one hour below the saved cursor and advances the state to the newest record."""
    path, records_key, cursor_field, build = _LISTS[stream_name]
    records = [build(1, _PRIOR_CURSOR - 3601), build(2, _PRIOR_CURSOR - 3600), build(3, _PRIOR_CURSOR), build(4, _PRIOR_CURSOR + 10)]
    state = StateBuilder().with_stream_state(stream_name, {cursor_field: str(_PRIOR_CURSOR)}).build()
    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_API}/{path}", json={records_key: records})
        output = _read(stream_name, _BASE_CONFIG, SyncMode.incremental, state)

    assert [record.record.data["id"] for record in output.records] == [2, 3, 4]
    assert int(getattr(output.most_recent_state.stream_state, cursor_field)) == _PRIOR_CURSOR + 10


def _serve_senders(mocker, visible_pages: list, hidden_pages: list) -> None:
    """Serve the visible (`hidden=false`) and hidden (`hidden=true`) sender lists, each followed by the guard page."""
    mocker.get(f"{_SENDERS_URL}?hidden=false", [{"json": page} for page in visible_pages] + [_GUARD_PAGE])
    hidden_guard = {"json": {"sender_identities": [_sender(99, hidden=True)], "next": ""}}
    mocker.get(f"{_SENDERS_URL}?hidden=true", [{"json": page} for page in hidden_pages] + [hidden_guard])


def test_sender_identities_reads_visible_and_hidden_senders_and_follows_next_into_start():
    """`hidden=true` returns only hidden senders, so both values are read; `next` goes into `start` until the empty last page."""
    # case_sensitive keeps the base64 `start` tokens intact in `request.qs`.
    with requests_mock.Mocker(case_sensitive=True) as mocker:
        _serve_senders(
            mocker,
            visible_pages=[
                {"sender_identities": [_sender(1)], "next": "Mg=="},
                {"sender_identities": [_sender(3)], "next": "Mw=="},
                {"sender_identities": [], "next": ""},
            ],
            hidden_pages=[{"sender_identities": [_sender(2, hidden=True)], "next": "MQ=="}, {"sender_identities": [], "next": ""}],
        )
        output = _read("sender_identities", _BASE_CONFIG)

    assert sorted(record.record.data["id"] for record in output.records) == [1, 2, 3]
    assert sorted((request.qs["hidden"][0], request.qs.get("start", [""])[0]) for request in mocker.request_history) == [
        ("false", ""),
        ("false", "Mg=="),
        ("false", "Mw=="),
        ("true", ""),
        ("true", "MQ=="),
    ]
    assert all(request.qs["limit"] == ["100"] for request in mocker.request_history)


@pytest.mark.parametrize("last_page", [{"next": ""}, {"next": None}, {}], ids=["empty", "null", "absent"])
def test_sender_identities_stops_when_next_is_empty(last_page):
    """An empty, null or missing `next` ends each list after one request."""
    with requests_mock.Mocker() as mocker:
        _serve_senders(
            mocker,
            visible_pages=[{"sender_identities": [_sender(1)], **last_page}],
            hidden_pages=[{"sender_identities": [_sender(2, hidden=True)], **last_page}],
        )
        output = _read("sender_identities", _BASE_CONFIG)

    assert sorted(record.record.data["id"] for record in output.records) == [1, 2]
    assert mocker.call_count == 2


def test_broadcast_actions_reads_every_broadcast_with_integer_keys():
    """One partition per broadcast: `broadcast_id` comes from the partition, a string `id` is cast to integer, `next` goes into `start`."""
    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_API}/broadcasts", json={"broadcasts": [_broadcast(1, _PRIOR_CURSOR), _broadcast(2, _PRIOR_CURSOR)]})
        mocker.get(
            f"{_API}/broadcasts/1/actions",
            [
                # Live `listCampaignActions` returns `id` as a string although the spec says integer.
                {"json": {"actions": [{**_broadcast_action("11", _PRIOR_CURSOR), "broadcast_id": 1}], "next": "tok-2"}},
                {"json": {"actions": [_broadcast_action(12, _PRIOR_CURSOR)], "next": ""}},
            ],
        )
        mocker.get(f"{_API}/broadcasts/2/actions", json={"actions": [_broadcast_action(21, _PRIOR_CURSOR)]})
        output = _read("broadcast_actions", _BASE_CONFIG)

    keys = sorted(((record.record.data["broadcast_id"], record.record.data["id"]) for record in output.records), key=itemgetter(0))
    assert keys == [(1, 11), (1, 12), (2, 21)]
    assert sorted((request.path, request.query) for request in mocker.request_history if request.path != "/v1/broadcasts") == [
        ("/v1/broadcasts/1/actions", ""),
        ("/v1/broadcasts/1/actions", "start=tok-2"),
        ("/v1/broadcasts/2/actions", ""),
    ]


def test_broadcast_actions_resumes_each_broadcast_from_its_own_cursor():
    """A resumed read keeps each broadcast's actions down to one hour below that broadcast's saved cursor, not the global one."""
    state = (
        StateBuilder()
        .with_stream_state(
            "broadcast_actions",
            {
                "use_global_cursor": False,
                "states": [
                    {"partition": {"broadcast_id": 1, "parent_slice": {}}, "cursor": {"updated": str(_PRIOR_CURSOR)}},
                    {"partition": {"broadcast_id": 2, "parent_slice": {}}, "cursor": {"updated": str(_PRIOR_CURSOR + 7200)}},
                ],
                "state": {"updated": str(_PRIOR_CURSOR + 7200)},
            },
        )
        .build()
    )
    first_actions = [
        _broadcast_action(11, _PRIOR_CURSOR - 3601),
        _broadcast_action(12, _PRIOR_CURSOR - 3600),
        _broadcast_action(13, _PRIOR_CURSOR + 5),
    ]
    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_API}/broadcasts", json={"broadcasts": [_broadcast(1, _PRIOR_CURSOR), _broadcast(2, _PRIOR_CURSOR)]})
        mocker.get(f"{_API}/broadcasts/1/actions", json={"actions": first_actions})
        mocker.get(
            f"{_API}/broadcasts/2/actions",
            json={"actions": [_broadcast_action(21, _PRIOR_CURSOR), _broadcast_action(22, _PRIOR_CURSOR + 7200)]},
        )
        output = _read("broadcast_actions", _BASE_CONFIG, SyncMode.incremental, state)

    assert sorted((record.record.data["broadcast_id"], record.record.data["id"]) for record in output.records) == [
        (1, 12),
        (1, 13),
        (2, 22),
    ]


def test_newsletter_variants_reads_contents_of_every_newsletter():
    """The inline `newsletters` parent keeps its `start`/`limit` paginator; each one-time send gets one `/contents` request without parameters."""
    with requests_mock.Mocker() as mocker:
        mocker.get(
            f"{_API}/newsletters",
            [
                {"json": {"newsletters": [_newsletter(1, _PRIOR_CURSOR), _newsletter(2, _PRIOR_CURSOR)], "next": "tok"}},
                {"json": {"newsletters": [_newsletter(3, _PRIOR_CURSOR)], "next": ""}},
            ],
        )
        mocker.get(f"{_API}/newsletters/1/contents", json={"contents": [_variant(10, 1), _variant(11, 1, language="fr")]})
        mocker.get(f"{_API}/newsletters/2/contents", json={"contents": [_variant(20, 2)]})
        mocker.get(f"{_API}/newsletters/3/contents", json={"contents": []})
        output = _read("newsletter_variants", _BASE_CONFIG)

    variants = sorted(
        (record.record.data["newsletter_id"], record.record.data["id"], record.record.data["from_id"]) for record in output.records
    )
    assert variants == [(1, 10, 1), (1, 11, 1), (2, 20, 2)]
    assert [request.qs for request in mocker.request_history if request.path == "/v1/newsletters"] == [
        {"limit": ["100"]},
        {"limit": ["100"], "start": ["tok"]},
    ]
    contents_requests = [request for request in mocker.request_history if request.path.endswith("/contents")]
    assert sorted(request.path for request in contents_requests) == [
        f"/v1/newsletters/{newsletter_id}/contents" for newsletter_id in (1, 2, 3)
    ]
    assert not any(request.qs for request in contents_requests)


def test_segment_usage_emits_the_used_by_object_once_per_segment():
    """`used_by` is one object, so each segment yields exactly one record with its id arrays intact."""
    used_by_7 = _used_by(7, campaigns=(1, 2), draft_newsletters=(3,))
    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_API}/segments", json={"segments": [_segment(7, _PRIOR_CURSOR), _segment(9, _PRIOR_CURSOR)]})
        mocker.get(f"{_API}/segments/7/used_by", json=used_by_7)
        mocker.get(f"{_API}/segments/9/used_by", json=_used_by(9))
        output = _read("segment_usage", _BASE_CONFIG)

    records = sorted((record.record.data for record in output.records), key=itemgetter("segment_id"))
    assert records == [used_by_7["used_by"], _used_by(9)["used_by"]]
    assert sorted(request.path for request in mocker.request_history) == [
        "/v1/segments",
        "/v1/segments/7/used_by",
        "/v1/segments/9/used_by",
    ]


def _serve_substream(mocker, stream_name: str, child_responses: list) -> None:
    """Serve parents 1..n, all updated a day before `_START_DATE`, and answer parent i's child request with `child_responses[i - 1]`."""
    parent_path, build_parent, child_path, _, _ = _SUBSTREAMS[stream_name]
    parents = [build_parent(parent_id, _START_EPOCH - 86400) for parent_id in range(1, len(child_responses) + 1)]
    mocker.get(f"{_API}/{parent_path}", json={parent_path: parents})
    for parent_id, response in enumerate(child_responses, start=1):
        mocker.get(f"{_API}/{child_path.format(parent_id)}", [response])


@pytest.mark.parametrize("stream_name", list(_SUBSTREAMS))
def test_substream_reads_parents_updated_before_start_date(stream_name):
    """The inline parent copy has no cursor, so the Start Date never hides a parent from its substream."""
    parent_path, _, child_path, child_response, partition_field = _SUBSTREAMS[stream_name]
    with requests_mock.Mocker() as mocker:
        _serve_substream(mocker, stream_name, [{"json": child_response(1)}])
        output = _read(stream_name, {**_BASE_CONFIG, "start_date": _START_DATE})

    assert [record.record.data[partition_field] for record in output.records] == [1]
    assert sorted(request.path for request in mocker.request_history) == [f"/v1/{parent_path}", f"/v1/{child_path.format(1)}"]


@pytest.mark.parametrize("stream_name", list(_SUBSTREAMS))
def test_substream_skips_404_for_a_parent_deleted_mid_sync(stream_name):
    """`substream_error_handler` skips a 404 for one parent without retrying, and the other parent's records are emitted."""
    parent_path, _, child_path, child_response, partition_field = _SUBSTREAMS[stream_name]
    with requests_mock.Mocker() as mocker:
        _serve_substream(mocker, stream_name, [{"status_code": 404, "json": _errors(404, "not found")}, {"json": child_response(2)}])
        output = _read(stream_name, _BASE_CONFIG)

    assert [record.record.data[partition_field] for record in output.records] == [2]
    assert not output.errors
    assert output.get_stream_statuses(stream_name)[-1] == AirbyteStreamStatus.COMPLETE
    assert sorted(request.path for request in mocker.request_history) == [f"/v1/{parent_path}"] + [
        f"/v1/{child_path.format(parent_id)}" for parent_id in (1, 2)
    ]


def test_sender_identities_stops_on_an_empty_page_even_with_a_next_token():
    """An empty page ends the read even if it still carries a `next` token, so a stale token cannot loop."""
    with requests_mock.Mocker() as mocker:
        _serve_senders(
            mocker,
            visible_pages=[{"sender_identities": [_sender(1)], "next": "Mg=="}, {"sender_identities": [], "next": "Mw=="}],
            hidden_pages=[{"sender_identities": [], "next": "MQ=="}],
        )
        output = _read("sender_identities", _BASE_CONFIG)

    assert [record.record.data["id"] for record in output.records] == [1]
    assert mocker.call_count == 3


def test_broadcast_actions_keeps_a_null_id_null():
    """The `id` cast applies only when the API returns an id, so a null id is not turned into the string "None"."""
    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_API}/broadcasts", json={"broadcasts": [_broadcast(1, _PRIOR_CURSOR)]})
        mocker.get(f"{_API}/broadcasts/1/actions", json={"actions": [{**_broadcast_action(11, _PRIOR_CURSOR), "id": None}]})
        output = _read("broadcast_actions", _BASE_CONFIG)

    # The serialized record omits null values, so a null id reads back as missing.
    assert [(record.record.data["broadcast_id"], record.record.data.get("id")) for record in output.records] == [(1, None)]


@pytest.mark.parametrize(
    "visible_ids, hidden_ids",
    [([1], [2]), ([1, 2], [2]), ([1], [1, 2]), ([1, 2], [1, 2])],
    ids=["disjoint", "false_lists_all", "true_lists_all", "both_list_all"],
)
def test_sender_identities_emits_each_sender_once_whatever_the_hidden_lists_overlap(visible_ids, hidden_ids):
    """Sender 2 is hidden; however the two lists overlap, each sender is emitted once, from the list its flag belongs to."""
    page = lambda ids: {"sender_identities": [_sender(i, hidden=(i == 2)) for i in ids], "next": ""}
    with requests_mock.Mocker() as mocker:
        _serve_senders(mocker, visible_pages=[page(visible_ids)], hidden_pages=[page(hidden_ids)])
        output = _read("sender_identities", _BASE_CONFIG)

    assert sorted(record.record.data["id"] for record in output.records) == [1, 2]


def test_broadcast_actions_resumes_from_its_own_state_without_a_gap():
    """The first read saves one cursor per broadcast, so an action edited below another broadcast's newest action is still read."""
    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_API}/broadcasts", json={"broadcasts": [_broadcast(1, _PRIOR_CURSOR), _broadcast(2, _PRIOR_CURSOR)]})
        mocker.get(
            f"{_API}/broadcasts/1/actions",
            [
                {"json": {"actions": [_broadcast_action(11, _PRIOR_CURSOR)]}},
                {"json": {"actions": [_broadcast_action(11, _PRIOR_CURSOR + 5)]}},
            ],
        )
        mocker.get(f"{_API}/broadcasts/2/actions", json={"actions": [_broadcast_action(21, _PRIOR_CURSOR + 7200)]})
        first = _read("broadcast_actions", _BASE_CONFIG, SyncMode.incremental)
        second = _read("broadcast_actions", _BASE_CONFIG, SyncMode.incremental, [first.state_messages[-1].state])

    assert sorted((record.record.data["broadcast_id"], record.record.data["updated"]) for record in second.records) == [
        (1, _PRIOR_CURSOR + 5),
        (2, _PRIOR_CURSOR + 7200),
    ]


def test_broadcast_actions_drops_actions_updated_before_start_date():
    """The Start Date filters each broadcast's actions, while the broadcast itself is never filtered."""
    actions = [_broadcast_action(11, _START_EPOCH - 1), _broadcast_action(12, _START_EPOCH), _broadcast_action(13, _START_EPOCH + 1)]
    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_API}/broadcasts", json={"broadcasts": [_broadcast(1, _START_EPOCH - 86400)]})
        mocker.get(f"{_API}/broadcasts/1/actions", json={"actions": actions})
        output = _read("broadcast_actions", {**_BASE_CONFIG, "start_date": _START_DATE})

    assert [record.record.data["id"] for record in output.records] == [12, 13]
