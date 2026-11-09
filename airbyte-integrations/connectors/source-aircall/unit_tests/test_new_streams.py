# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from datetime import datetime, timezone

import pytest
from freezegun import freeze_time
from unit_tests.conftest import get_source, sleep_moves_clock

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder


_BASE_URL = "https://api.aircall.io/v1"
_CONFIG = {"credentials": {"auth_type": "api_key", "api_id": "test-id", "api_token": "test-token"}}
_NOW = "2026-11-03T00:00:00Z"
_DAY = 86400
_CONVERSATIONS_EPOCH = 1388534400
_FORBIDDEN_GATEWAY_BODY = json.dumps({"message": "Forbidden"})
_STATUS_NAMES = {400: ("Bad Request", "BAD_REQUEST"), 403: ("Forbidden", "FORBIDDEN"), 404: ("Not Found", "NOT_FOUND")}
_NEW_STREAMS = {
    "conversations": [["id"]],
    "conversation_engagements": [["id"]],
    "campaigns": [["id"]],
    "campaign_outcomes": [["id"]],
    "trackers": [["id"]],
    "sms_templates": [["id"]],
    "whatsapp_templates": [["number_id"], ["id"]],
}
_KEY_FIELD_TYPES = {
    "conversations": {"id": "integer", "last_engagement_at": "string"},
    "conversation_engagements": {"id": "integer", "created_at": "string", "conversation_id": "integer"},
    "campaigns": {"id": "string"},
    "campaign_outcomes": {"id": "string"},
    "trackers": {"id": "integer"},
    "sms_templates": {"id": "integer"},
    "whatsapp_templates": {"id": "string", "number_id": "integer"},
}


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("time.sleep", lambda *_args, **_kwargs: None)


def _epoch(value: str) -> int:
    return int(datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp())


def _iso(epoch: int) -> str:
    return datetime.fromtimestamp(epoch, timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")


def _request(path: str, query_params: dict[str, str] | None = None) -> HttpRequest:
    return HttpRequest(f"{_BASE_URL}{path}", query_params=query_params or {})


def _json(body: dict, status_code: int = 200) -> HttpResponse:
    return HttpResponse(body=json.dumps(body), status_code=status_code)


def _app_error(status_code: int, troubleshoot: str) -> HttpResponse:
    error, code = _STATUS_NAMES[status_code]
    return _json(
        {
            "error": error,
            "message": code,
            "errors": [{"status": status_code, "title": error, "detail": code}],
            "troubleshoot": troubleshoot,
            "success": False,
        },
        status_code,
    )


def _read(
    stream_name: str,
    sync_mode: SyncMode = SyncMode.full_refresh,
    config: dict | None = None,
    state=None,
    expecting_exception: bool = False,
) -> EntrypointOutput:
    config = config or _CONFIG
    catalog = CatalogBuilder().with_stream(stream_name, sync_mode).build()
    return read(
        get_source(config=config, state=state),
        config=config,
        catalog=catalog,
        state=state,
        expecting_exception=expecting_exception,
    )


def _windows(start: int, end: int, window_days: int) -> list[tuple[int, int]]:
    windows = []
    while start < end:
        next_start = min(start + window_days * _DAY, end)
        windows.append((start, next_start if next_start == end else next_start - 1))
        start = next_start
    return windows


def _conversation_request(window: tuple[int, int], page: int | None = None) -> HttpRequest:
    params = {"from": str(window[0]), "to": str(window[1]), "order": "asc", "per_page": "50"}
    if page:
        params["page"] = str(page)
    return _request("/conversations", params)


def _conversation(conversation_id: int, last_engagement_at: int) -> dict:
    return {"id": conversation_id, "status": "opened", "last_engagement_at": _iso(last_engagement_at)}


def _engagements_request(conversation_id: int, page: int | None = None) -> HttpRequest:
    params = {"per_page": "50"}
    if page:
        params["page"] = str(page)
    return _request(f"/conversations/{conversation_id}/engagements", params)


def _logs(output: EntrypointOutput) -> list[str]:
    return [log.log.message for log in output.logs]


def _config_error(output: EntrypointOutput):
    assert output.errors
    error = output.errors[0].trace.error
    assert error.failure_type == FailureType.config_error
    return error


def test_new_streams_declare_keys_sync_modes_and_key_field_types() -> None:
    catalog = get_source(_CONFIG).discover(None, _CONFIG)
    streams = {stream.name: stream for stream in catalog.streams}

    for name, primary_key in _NEW_STREAMS.items():
        assert streams[name].source_defined_primary_key == primary_key, name
        properties = streams[name].json_schema["properties"]
        for field, field_type in _KEY_FIELD_TYPES[name].items():
            assert field_type in properties[field]["type"], (name, field)
    assert streams["conversations"].default_cursor_field == ["last_engagement_at"]
    assert streams["conversation_engagements"].default_cursor_field == ["created_at"]
    for name in ("conversations", "conversation_engagements"):
        assert [mode.value for mode in streams[name].supported_sync_modes] == ["full_refresh", "incremental"]
    for name in ("campaigns", "campaign_outcomes", "trackers", "sms_templates", "whatsapp_templates"):
        assert [mode.value for mode in streams[name].supported_sync_modes] == ["full_refresh"]


def test_conversations_incremental_reads_one_window_from_the_lookback_with_pages_and_state() -> None:
    with freeze_time(_NOW), HttpMocker() as http_mocker:
        state_time = _epoch("2026-10-31T00:00:00Z")
        window = (state_time - 3 * _DAY, _epoch(_NOW))
        state = StateBuilder().with_stream_state("conversations", {"last_engagement_at": str(state_time)}).build()
        first = _conversation_request(window)
        second = _conversation_request(window, page=2)
        http_mocker.get(first, _json({"conversations": [_conversation(record_id, state_time + record_id) for record_id in range(1, 51)]}))
        http_mocker.get(second, _json({"conversations": [_conversation(51, state_time + 51)]}))

        # The calls window setting does not change the conversations window.
        output = _read("conversations", SyncMode.incremental, config={**_CONFIG, "window_in_days": 1}, state=state)

        assert output.errors == []
        assert len(output.records) == 51
        assert output.most_recent_state.stream_state.last_engagement_at == str(state_time + 51)
        for request in (first, second):
            http_mocker.assert_number_of_calls(request, 1)


def test_conversations_full_refresh_reads_thirty_day_windows_from_2014() -> None:
    now = "2014-03-01T00:00:00Z"
    with freeze_time(now), HttpMocker() as http_mocker:
        windows = _windows(_CONVERSATIONS_EPOCH, _epoch(now), 30)
        requests = [_conversation_request(window) for window in windows]
        for index, (window, request) in enumerate(zip(windows, requests)):
            http_mocker.get(request, _json({"conversations": [_conversation(index + 1, window[0])]}))

        output = _read("conversations")

        assert output.errors == []
        assert sorted(record.record.data["id"] for record in output.records) == [1, 2]
        for request in requests:
            http_mocker.assert_number_of_calls(request, 1)


def test_conversations_restart_from_the_last_timestamp_instead_of_requesting_page_201(monkeypatch: pytest.MonkeyPatch) -> None:
    with freeze_time(_NOW) as clock, HttpMocker() as http_mocker:
        sleep_moves_clock(clock, monkeypatch)
        state_time = _epoch("2026-10-31T00:00:00Z")
        start, end = state_time - 3 * _DAY, _epoch(_NOW)
        state = StateBuilder().with_stream_state("conversations", {"last_engagement_at": str(state_time)}).build()
        for page in range(1, 201):
            conversations = [_conversation(record_id, state_time + record_id) for record_id in range((page - 1) * 50 + 1, page * 50 + 1)]
            http_mocker.get(_conversation_request((start, end), page=page if page > 1 else None), _json({"conversations": conversations}))
        restart = _conversation_request((state_time + 10000, end))
        http_mocker.get(
            restart, _json({"conversations": [_conversation(10000, state_time + 10000), _conversation(10001, state_time + 10001)]})
        )

        output = _read("conversations", SyncMode.incremental, state=state)

        assert output.errors == []
        assert {record.record.data["id"] for record in output.records} == set(range(1, 10002))
        http_mocker.assert_number_of_calls(restart, 1)
        assert output.most_recent_state.stream_state.last_engagement_at == str(state_time + 10001)


@pytest.mark.parametrize(
    "troubleshoot",
    [
        pytest.param("The Conversations API is not enabled for this Company.", id="documented"),
        pytest.param("Conversations API not enabled for this company", id="variant"),
    ],
)
def test_conversations_not_enabled_403_is_ignored_with_the_url(troubleshoot: str) -> None:
    with freeze_time(_NOW), HttpMocker() as http_mocker:
        window = (_epoch(_NOW) - 3 * _DAY, _epoch(_NOW))
        state = StateBuilder().with_stream_state("conversations", {"last_engagement_at": str(_epoch(_NOW))}).build()
        request = _conversation_request(window)
        http_mocker.get(request, _app_error(403, troubleshoot))

        output = _read("conversations", SyncMode.incremental, state=state)

        assert output.errors == []
        assert output.records == []
        assert (
            "Ignoring https://api.aircall.io/v1/conversations: the Conversations API is not enabled for this Aircall company (HTTP 403)."
            in _logs(output)
        )
        http_mocker.assert_number_of_calls(request, 1)


def test_conversations_other_errors_that_say_not_enabled_are_not_ignored() -> None:
    with freeze_time("2014-01-02T00:00:00Z"), HttpMocker() as http_mocker:
        request = _conversation_request((_CONVERSATIONS_EPOCH, _CONVERSATIONS_EPOCH + _DAY))
        http_mocker.get(request, _app_error(400, "status filter is not enabled"))

        output = _read("conversations", expecting_exception=True)

        assert output.errors
        assert output.errors[0].trace.error.failure_type == FailureType.system_error


def test_conversations_gateway_403_stays_a_config_error() -> None:
    with freeze_time("2014-01-02T00:00:00Z"), HttpMocker() as http_mocker:
        request = _conversation_request((_CONVERSATIONS_EPOCH, _CONVERSATIONS_EPOCH + _DAY))
        http_mocker.get(request, HttpResponse(body=_FORBIDDEN_GATEWAY_BODY, status_code=403))

        output = _read("conversations", expecting_exception=True)

        assert "Aircall returned HTTP 403 for https://api.aircall.io/v1/conversations." in _config_error(output).message


def test_conversation_engagements_read_each_parent_and_paginate() -> None:
    with freeze_time("2014-01-02T00:00:00Z"), HttpMocker() as http_mocker:
        http_mocker.get(
            _conversation_request((_CONVERSATIONS_EPOCH, _CONVERSATIONS_EPOCH + _DAY)),
            _json({"conversations": [_conversation(11, _CONVERSATIONS_EPOCH), _conversation(12, _CONVERSATIONS_EPOCH)]}),
        )
        first, second, other = _engagements_request(11), _engagements_request(11, page=2), _engagements_request(12)
        http_mocker.get(first, _json({"engagements": [{"id": index, "type": "call"} for index in range(50)]}))
        http_mocker.get(second, _json({"engagements": [{"id": 50, "type": "assignment"}]}))
        http_mocker.get(other, _json({"engagements": [{"id": 99, "type": "conversation_closed"}]}))

        output = _read("conversation_engagements")

        assert output.errors == []
        by_parent = {}
        for record in output.records:
            by_parent.setdefault(record.record.data["conversation_id"], []).append(record.record.data)
        assert {parent: len(records) for parent, records in by_parent.items()} == {11: 51, 12: 1}
        assert by_parent[12] == [{"id": 99, "type": "conversation_closed", "conversation_id": 12}]
        for request in (first, second, other):
            http_mocker.assert_number_of_calls(request, 1)


def test_conversation_engagements_next_sync_rereads_conversations_active_since_three_days_before_the_cursor(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    first_sync = "2026-11-02T00:00:00Z"
    active_at = _epoch("2026-11-01T10:00:00Z")
    with freeze_time(first_sync) as clock, HttpMocker() as http_mocker:
        sleep_moves_clock(clock, monkeypatch)
        for window in _windows(_CONVERSATIONS_EPOCH, _epoch(first_sync), 30):
            conversations = [_conversation(11, active_at), _conversation(12, active_at + 1)] if window[1] == _epoch(first_sync) else []
            http_mocker.get(_conversation_request(window), _json({"conversations": conversations}))
        http_mocker.get(_engagements_request(11), _json({"engagements": [{"id": 1, "created_at": _iso(active_at)}]}))
        # An engagement dated in the future must not empty the next syncs.
        http_mocker.get(_engagements_request(12), _json({"engagements": [{"id": 2, "created_at": "2026-12-01T00:00:00.000Z"}]}))

        output = _read("conversation_engagements", SyncMode.incremental)

        assert output.errors == []
        state = output.most_recent_state.stream_state
        assert state.use_global_cursor is True
        assert state.parent_state["conversations"]["last_engagement_at"] == str(active_at + 1)

    second_sync = "2026-11-03T00:00:00Z"
    with freeze_time(second_sync), HttpMocker() as http_mocker:
        window = (active_at + 1 - 3 * _DAY, _epoch(second_sync))
        new_activity = _epoch("2026-11-02T12:00:00Z")
        http_mocker.get(
            _conversation_request(window), _json({"conversations": [_conversation(11, active_at), _conversation(12, new_activity)]})
        )
        reread, active = _engagements_request(11), _engagements_request(12)
        http_mocker.get(reread, _json({"engagements": [{"id": 1, "created_at": _iso(active_at)}]}))
        http_mocker.get(
            active,
            _json({"engagements": [{"id": 3, "created_at": _iso(new_activity)}, {"id": 2, "created_at": "2026-12-01T00:00:00.000Z"}]}),
        )

        output = _read(
            "conversation_engagements",
            SyncMode.incremental,
            state=StateBuilder().with_stream_state("conversation_engagements", state.__dict__).build(),
        )

        assert output.errors == []
        # Conversation 11 is re-read inside the lookback and its older engagement is emitted again: no record filter.
        assert sorted(record.record.data["id"] for record in output.records) == [1, 2, 3]
        for request in (reread, active):
            http_mocker.assert_number_of_calls(request, 1)


@pytest.mark.parametrize(
    "response,message",
    [
        pytest.param(
            _app_error(400, "page * per_page must not exceed 10000"),
            "Aircall returns at most the 10,000 most recent engagements of a conversation; older engagements of "
            "https://api.aircall.io/v1/conversations/11/engagements are not synced.",
            id="result-cap",
        ),
        pytest.param(
            _app_error(400, "page multiplied by per_page exceeds 10,000"),
            "Aircall returns at most the 10,000 most recent engagements of a conversation; older engagements of "
            "https://api.aircall.io/v1/conversations/11/engagements are not synced.",
            id="result-cap-reference-wording",
        ),
        pytest.param(
            _app_error(404, "No Conversation exists with this id for the Company."),
            "Ignoring https://api.aircall.io/v1/conversations/11/engagements: the conversation no longer exists (HTTP 404).",
            id="deleted-conversation",
        ),
        pytest.param(
            _app_error(403, "The Conversations API is not enabled for this Company."),
            "Ignoring https://api.aircall.io/v1/conversations/11/engagements: the Conversations API is not enabled for this "
            "Aircall company (HTTP 403).",
            id="not-enabled",
        ),
    ],
)
def test_conversation_engagements_ignore_documented_per_conversation_errors(response: HttpResponse, message: str) -> None:
    with freeze_time("2014-01-02T00:00:00Z"), HttpMocker() as http_mocker:
        http_mocker.get(
            _conversation_request((_CONVERSATIONS_EPOCH, _CONVERSATIONS_EPOCH + _DAY)),
            _json({"conversations": [_conversation(11, _CONVERSATIONS_EPOCH)]}),
        )
        first, second = _engagements_request(11), _engagements_request(11, page=2)
        http_mocker.get(first, _json({"engagements": [{"id": index, "type": "call"} for index in range(50)]}))
        http_mocker.get(second, response)

        output = _read("conversation_engagements")

        assert output.errors == []
        assert len(output.records) == 50
        assert message in _logs(output)


def test_conversation_engagements_gateway_404_is_not_ignored() -> None:
    with freeze_time("2014-01-02T00:00:00Z"), HttpMocker() as http_mocker:
        http_mocker.get(
            _conversation_request((_CONVERSATIONS_EPOCH, _CONVERSATIONS_EPOCH + _DAY)),
            _json({"conversations": [_conversation(11, _CONVERSATIONS_EPOCH)]}),
        )
        http_mocker.get(_engagements_request(11), _json({"message": "Not Found"}, 404))

        output = _read("conversation_engagements", expecting_exception=True)

        assert output.errors
        assert output.records == []


def test_conversation_engagements_retry_a_500() -> None:
    with freeze_time("2014-01-02T00:00:00Z"), HttpMocker() as http_mocker:
        http_mocker.get(
            _conversation_request((_CONVERSATIONS_EPOCH, _CONVERSATIONS_EPOCH + _DAY)),
            _json({"conversations": [_conversation(11, _CONVERSATIONS_EPOCH)]}),
        )
        request = _engagements_request(11)
        http_mocker.get(request, [_json({"message": "Internal error"}, 500), _json({"engagements": [{"id": 1, "type": "call"}]})])

        output = _read("conversation_engagements")

        assert output.errors == []
        assert [record.record.data["id"] for record in output.records] == [1]
        http_mocker.assert_number_of_calls(request, 2)


def test_conversation_engagements_gateway_403_stays_a_config_error() -> None:
    with freeze_time("2014-01-02T00:00:00Z"), HttpMocker() as http_mocker:
        http_mocker.get(
            _conversation_request((_CONVERSATIONS_EPOCH, _CONVERSATIONS_EPOCH + _DAY)),
            _json({"conversations": [_conversation(11, _CONVERSATIONS_EPOCH)]}),
        )
        http_mocker.get(_engagements_request(11), HttpResponse(body=_FORBIDDEN_GATEWAY_BODY, status_code=403))

        output = _read("conversation_engagements", expecting_exception=True)

        assert "Aircall returned HTTP 403 for https://api.aircall.io/v1/conversations/11/engagements." in _config_error(output).message


@pytest.mark.parametrize("stream_name", ["campaigns", "campaign_outcomes"])
def test_campaign_streams_follow_meta_next_cursor(stream_name: str) -> None:
    with HttpMocker() as http_mocker:
        first = _request(f"/{stream_name}", {"per_page": "50"})
        second = _request(f"/{stream_name}", {"per_page": "50", "cursor": "next-cursor"})
        http_mocker.get(
            first, _json({stream_name: [{"id": "a"}], "meta": {"count": 1, "total": 2, "per_page": 50, "next_cursor": "next-cursor"}})
        )
        http_mocker.get(second, _json({stream_name: [{"id": "b"}], "meta": {"count": 1, "total": 2, "per_page": 50, "next_cursor": None}}))

        output = _read(stream_name)

        assert output.errors == []
        assert [record.record.data["id"] for record in output.records] == ["a", "b"]
        http_mocker.assert_number_of_calls(first, 1)
        http_mocker.assert_number_of_calls(second, 1)


def test_trackers_read_records() -> None:
    with HttpMocker() as http_mocker:
        request = _request("/trackers")
        http_mocker.get(request, _json({"trackers": [{"id": 123, "title": "Pricing objections"}]}))

        output = _read("trackers")

        assert output.errors == []
        assert [record.record.data["id"] for record in output.records] == [123]
        http_mocker.assert_number_of_calls(request, 1)


def test_trackers_without_ai_assist_403_skips_stream_with_message() -> None:
    with HttpMocker() as http_mocker:
        request = _request("/trackers")
        http_mocker.get(request, _app_error(403, "Forbidden access: company cannot access this feature."))

        output = _read("trackers")

        assert output.errors == []
        assert output.records == []
        assert any("AI Assist" in message for message in _logs(output))
        http_mocker.assert_number_of_calls(request, 1)


def test_trackers_gateway_403_stays_a_config_error() -> None:
    with HttpMocker() as http_mocker:
        http_mocker.get(_request("/trackers"), HttpResponse(body=_FORBIDDEN_GATEWAY_BODY, status_code=403))

        output = _read("trackers", expecting_exception=True)

        assert "Aircall returned HTTP 403 for https://api.aircall.io/v1/trackers." in _config_error(output).message


def test_sms_templates_use_per_page_100() -> None:
    with HttpMocker() as http_mocker:
        first = _request("/sms/templates", {"per_page": "100"})
        second = _request("/sms/templates", {"per_page": "100", "page": "2"})
        http_mocker.get(first, _json({"templates": [{"id": index, "name": "t"} for index in range(100)]}))
        http_mocker.get(second, _json({"templates": [{"id": 100, "name": "last", "body": "Hi"}]}))

        output = _read("sms_templates")

        assert output.errors == []
        assert len(output.records) == 101
        http_mocker.assert_number_of_calls(first, 1)
        http_mocker.assert_number_of_calls(second, 1)


def _numbers_request() -> HttpRequest:
    return _request("/numbers", {"per_page": "50"})


@pytest.mark.parametrize(
    "troubleshoot",
    [
        pytest.param("Forbidden access: line is not configured to use whatsapp.", id="not-configured"),
        pytest.param("Forbidden access: line does not have WhatsApp capability.", id="no-capability"),
        pytest.param("Forbidden access: line does not belong to the company.", id="deleted-number"),
        pytest.param(None, id="live-no-capability"),
    ],
)
def test_whatsapp_templates_page_by_token_and_skip_numbers_without_whatsapp(troubleshoot: str | None) -> None:
    with HttpMocker() as http_mocker:
        http_mocker.get(_numbers_request(), _json({"numbers": [{"id": 1}, {"id": 2}]}))
        first = _request("/numbers/1/templates")
        second = _request("/numbers/1/templates", {"token": "10"})
        last = _request("/numbers/1/templates", {"token": "20"})
        not_whatsapp = _request("/numbers/2/templates")
        page_info = {"currentToken": 0, "nextToken": 10, "totalCount": 2}
        # Template bodies are free text; one that quotes a gating sentence is still a record.
        quoting = {"id": 1, "name": "a", "template": {"body": "Your line does not belong to the company anymore."}}
        http_mocker.get(first, _json({"templates": [quoting], "pageInfo": page_info}))
        http_mocker.get(
            second, _json({"templates": [{"id": 2, "name": "b"}], "pageInfo": {**page_info, "currentToken": 10, "nextToken": 20}})
        )
        # A last page that still carries a token but no templates ends the partition.
        http_mocker.get(last, _json({"templates": [], "pageInfo": {**page_info, "currentToken": 20, "nextToken": 30}}))
        not_whatsapp_response = (
            _app_error(403, troubleshoot)
            if troubleshoot
            else HttpResponse(body=json.dumps({"message": "Line 2 doesn't have WhatsApp capability", "key": "Forbidden"}), status_code=403)
        )
        http_mocker.get(not_whatsapp, not_whatsapp_response)

        output = _read("whatsapp_templates")

        assert output.errors == []
        assert [(record.record.data["number_id"], record.record.data["id"]) for record in output.records] == [(1, 1), (1, 2)]
        assert (
            "Ignoring https://api.aircall.io/v1/numbers/2/templates: this number is not registered for WhatsApp "
            "or no longer belongs to the company (HTTP 403)." in _logs(output)
        )
        for request in (first, second, last, not_whatsapp):
            http_mocker.assert_number_of_calls(request, 1)


def test_whatsapp_templates_gateway_403_stays_a_config_error() -> None:
    with HttpMocker() as http_mocker:
        http_mocker.get(_numbers_request(), _json({"numbers": [{"id": 1}]}))
        http_mocker.get(_request("/numbers/1/templates"), HttpResponse(body=_FORBIDDEN_GATEWAY_BODY, status_code=403))

        output = _read("whatsapp_templates", expecting_exception=True)

        assert "Aircall returned HTTP 403 for https://api.aircall.io/v1/numbers/1/templates." in _config_error(output).message
