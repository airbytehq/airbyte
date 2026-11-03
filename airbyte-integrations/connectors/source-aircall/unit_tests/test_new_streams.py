# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from datetime import datetime

import pytest
from freezegun import freeze_time
from unit_tests.conftest import get_source

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder


_BASE_URL = "https://api.aircall.io/v1"
_CONFIG = {"api_id": "test-id", "api_token": "test-token"}
_NOW = "2026-11-03T00:00:00Z"
_DAY = 86400
_CONVERSATIONS_EPOCH = 1388534400
_FORBIDDEN_GATEWAY_BODY = json.dumps({"message": "Forbidden"})
_NEW_STREAMS = [
    "conversations",
    "conversation_engagements",
    "campaigns",
    "campaign_outcomes",
    "trackers",
    "sms_templates",
    "whatsapp_templates",
]


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("time.sleep", lambda *_args, **_kwargs: None)


def _epoch(value: str) -> int:
    return int(datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp())


def _iso(epoch: int) -> str:
    return datetime.utcfromtimestamp(epoch).strftime("%Y-%m-%dT%H:%M:%S.000Z")


def _request(path: str, query_params: dict[str, str] | None = None) -> HttpRequest:
    return HttpRequest(f"{_BASE_URL}{path}", query_params=query_params or {})


def _json(body: dict, status_code: int = 200) -> HttpResponse:
    return HttpResponse(body=json.dumps(body), status_code=status_code)


def _app_error(status_code: int, troubleshoot: str) -> HttpResponse:
    return _json(
        {
            "error": "Forbidden",
            "message": "FORBIDDEN",
            "errors": [{"status": status_code, "title": "Forbidden", "detail": "FORBIDDEN"}],
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


def _info_logs(output: EntrypointOutput) -> list[str]:
    return [log.log.message for log in output.logs]


def _config_error(output: EntrypointOutput):
    assert output.errors
    error = output.errors[0].trace.error
    assert error.failure_type == FailureType.config_error
    return error


def test_new_streams_are_declared_with_expected_sync_modes() -> None:
    catalog = get_source(_CONFIG).discover(None, _CONFIG)
    streams = {stream.name: stream for stream in catalog.streams}

    assert set(_NEW_STREAMS) <= set(streams)
    assert streams["conversations"].default_cursor_field == ["last_engagement_at"]
    assert [mode.value for mode in streams["conversations"].supported_sync_modes] == ["full_refresh", "incremental"]
    for name in _NEW_STREAMS[1:]:
        assert [mode.value for mode in streams[name].supported_sync_modes] == ["full_refresh"]
    assert streams["whatsapp_templates"].source_defined_primary_key == [["number_id"], ["id"]]


def test_conversations_incremental_uses_last_engagement_windows_pagination_and_state() -> None:
    with freeze_time(_NOW), HttpMocker() as http_mocker:
        state_time = _epoch("2026-10-31T00:00:00Z")
        windows = _windows(state_time - 3 * _DAY, _epoch(_NOW), 1)
        state = StateBuilder().with_stream_state("conversations", {"last_engagement_at": str(state_time)}).build()
        requests = []
        for index, window in enumerate(windows):
            first_page = (
                [_conversation(record_id, window[0] + 1) for record_id in range(1, 51)]
                if index == 0
                else [_conversation(1000 + index, window[0] + 1)]
            )
            requests.append(_conversation_request(window))
            http_mocker.get(requests[-1], _json({"conversations": first_page}))
            if index == 0:
                requests.append(_conversation_request(window, page=2))
                http_mocker.get(requests[-1], _json({"conversations": [_conversation(51, window[0] + 2)]}))

        output = _read("conversations", SyncMode.incremental, config={**_CONFIG, "window_in_days": 1}, state=state)

        assert output.errors == []
        assert len(windows) == 6
        assert len(output.records) == 51 + len(windows) - 1
        assert output.most_recent_state.stream_state.last_engagement_at == str(windows[-1][0] + 1)
        for request in requests:
            http_mocker.assert_number_of_calls(request, 1)


def test_conversations_full_refresh_uses_thirty_day_windows_from_2014() -> None:
    with freeze_time("2014-03-01T00:00:00Z"), HttpMocker() as http_mocker:
        windows = _windows(_CONVERSATIONS_EPOCH, _epoch("2014-03-01T00:00:00Z"), 30)
        for index, window in enumerate(windows):
            http_mocker.get(_conversation_request(window), _json({"conversations": [_conversation(index + 1, window[0])]}))

        output = _read("conversations")

        assert output.errors == []
        assert windows == [
            (_CONVERSATIONS_EPOCH, _CONVERSATIONS_EPOCH + 30 * _DAY - 1),
            (_CONVERSATIONS_EPOCH + 30 * _DAY, _epoch("2014-03-01T00:00:00Z")),
        ]
        assert sorted(record.record.data["id"] for record in output.records) == [1, 2]


def test_conversations_not_enabled_403_skips_stream_with_message() -> None:
    with freeze_time(_NOW), HttpMocker() as http_mocker:
        window = _windows(_epoch(_NOW) - _DAY, _epoch(_NOW), 1)[0]
        state = StateBuilder().with_stream_state("conversations", {"last_engagement_at": str(window[0] + 3 * _DAY)}).build()
        request = _conversation_request(window)
        http_mocker.get(request, _app_error(403, "The Conversations API is not enabled for this Company."))

        output = _read("conversations", SyncMode.incremental, config={**_CONFIG, "window_in_days": 1}, state=state)

        assert output.errors == []
        assert output.records == []
        assert any("Conversations API is not enabled" in message for message in _info_logs(output))
        http_mocker.assert_number_of_calls(request, 1)


def test_conversations_gateway_403_stays_a_config_error() -> None:
    with freeze_time("2014-01-02T00:00:00Z"), HttpMocker() as http_mocker:
        request = _conversation_request((_CONVERSATIONS_EPOCH, _CONVERSATIONS_EPOCH + _DAY))
        http_mocker.get(request, HttpResponse(body=_FORBIDDEN_GATEWAY_BODY, status_code=403))

        output = _read("conversations", expecting_exception=True)

        assert "Aircall returned HTTP 403 for https://api.aircall.io/v1/conversations." in _config_error(output).message


def test_conversations_ten_thousand_result_error_is_a_config_error() -> None:
    with freeze_time("2014-01-02T00:00:00Z"), HttpMocker() as http_mocker:
        request = _conversation_request((_CONVERSATIONS_EPOCH, _CONVERSATIONS_EPOCH + _DAY))
        http_mocker.get(request, _app_error(400, "page * per_page must not exceed 10000"))

        output = _read("conversations", expecting_exception=True)

        assert _config_error(output).message.startswith("Aircall returns at most 10,000 conversations per request window.")


def test_conversation_engagements_read_each_parent_and_paginate() -> None:
    with freeze_time("2014-01-02T00:00:00Z"), HttpMocker() as http_mocker:
        http_mocker.get(
            _conversation_request((_CONVERSATIONS_EPOCH, _CONVERSATIONS_EPOCH + _DAY)),
            _json({"conversations": [_conversation(11, _CONVERSATIONS_EPOCH), _conversation(12, _CONVERSATIONS_EPOCH)]}),
        )
        first = _request("/conversations/11/engagements", {"per_page": "50"})
        second = _request("/conversations/11/engagements", {"per_page": "50", "page": "2"})
        other = _request("/conversations/12/engagements", {"per_page": "50"})
        http_mocker.get(first, _json({"engagements": [{"id": index, "type": "call"} for index in range(50)]}))
        http_mocker.get(second, _json({"engagements": [{"id": 50, "type": "assignment"}]}))
        http_mocker.get(other, _json({"engagements": [{"id": 99, "type": "conversation_closed"}]}))

        output = _read("conversation_engagements")

        assert output.errors == []
        assert len(output.records) == 52
        by_parent = {}
        for record in output.records:
            by_parent.setdefault(record.record.data["conversation_id"], []).append(record.record.data)
        assert {parent: len(records) for parent, records in by_parent.items()} == {11: 51, 12: 1}
        assert by_parent[12] == [{"id": 99, "type": "conversation_closed", "conversation_id": 12}]
        for request in (first, second, other):
            http_mocker.assert_number_of_calls(request, 1)


@pytest.mark.parametrize("stream_name", ["campaigns", "campaign_outcomes"])
def test_campaign_streams_follow_meta_next_cursor(stream_name: str) -> None:
    with HttpMocker() as http_mocker:
        first = _request(f"/{stream_name}", {"per_page": "50"})
        second = _request(f"/{stream_name}", {"per_page": "50", "cursor": "next-cursor"})
        http_mocker.get(first, _json({stream_name: [{"id": "a"}], "meta": {"next_cursor": "next-cursor"}}))
        http_mocker.get(second, _json({stream_name: [{"id": "b"}], "meta": {"next_cursor": None}}))

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
        assert any("AI Assist" in message for message in _info_logs(output))
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


def test_whatsapp_templates_page_by_token_and_skip_numbers_without_whatsapp() -> None:
    with HttpMocker() as http_mocker:
        http_mocker.get(_numbers_request(), _json({"numbers": [{"id": 1}, {"id": 2}]}))
        first = _request("/numbers/1/templates")
        second = _request("/numbers/1/templates", {"token": "10"})
        not_whatsapp = _request("/numbers/2/templates")
        http_mocker.get(
            first,
            _json({"templates": [{"id": 1, "name": "a"}], "pageInfo": {"currentToken": 0, "nextToken": 10, "totalCount": 2}}),
        )
        http_mocker.get(
            second,
            _json({"templates": [{"id": 2, "name": "b"}], "pageInfo": {"currentToken": 10, "nextToken": None, "totalCount": 2}}),
        )
        http_mocker.get(not_whatsapp, _app_error(403, "Forbidden access: line is not configured to use whatsapp."))

        output = _read("whatsapp_templates")

        assert output.errors == []
        assert [(record.record.data["number_id"], record.record.data["id"]) for record in output.records] == [(1, 1), (1, 2)]
        assert any("not registered for WhatsApp" in message for message in _info_logs(output))
        for request in (first, second, not_whatsapp):
            http_mocker.assert_number_of_calls(request, 1)


def test_whatsapp_templates_gateway_403_stays_a_config_error() -> None:
    with HttpMocker() as http_mocker:
        http_mocker.get(_numbers_request(), _json({"numbers": [{"id": 1}]}))
        http_mocker.get(_request("/numbers/1/templates"), HttpResponse(body=_FORBIDDEN_GATEWAY_BODY, status_code=403))

        output = _read("whatsapp_templates", expecting_exception=True)

        assert "Aircall returned HTTP 403 for https://api.aircall.io/v1/numbers/1/templates." in _config_error(output).message
