# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from datetime import datetime

import pytest
from freezegun import freeze_time
from jsonschema import Draft7Validator
from unit_tests.conftest import get_source

from airbyte_cdk.models import AirbyteStreamStatus, FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder


_BASE_URL = "https://api.aircall.io/v1"
# One 365-day calls window, so a read makes a single calls request.
_CONFIG = {"api_id": "test-id", "api_token": "test-token", "window_in_days": 365}
_CI_CONFIG = {**_CONFIG, "include_conversation_intelligence": True}
_NOW = "2026-11-03T00:00:00Z"
_DAY = 86400

# Response bodies from the reference samples, keyed by stream: (path suffix, extra query, body, primary key).
_STREAMS = {
    "call_transcriptions": (
        "transcription",
        {},
        {
            "transcription": {
                "id": 68271,
                "call_id": 812,
                "call_created_at": "2024-07-26T13:30:54.000Z",
                "type": "call",
                "content": {
                    "language": "en",
                    "utterances": [
                        {
                            "start_time": 12.54,
                            "end_time": 13.8,
                            "text": "Okay,",
                            "participant_type": "external",
                            "phone_number": "+33679198915",
                        },
                        {"start_time": 238.08, "end_time": 239.48, "text": "Okay.", "participant_type": "internal", "user_id": 123},
                    ],
                },
            }
        },
        [["id"]],
    ),
    "call_sentiments": (
        "sentiments",
        {},
        {
            "sentiment": {
                "id": 812,
                "call_id": 812,
                "participants": [{"phone_number": "+33679198915", "value": "POSITIVE", "type": "external"}],
            }
        },
        [["id"]],
    ),
    "call_topics": (
        "topics",
        {},
        {"topic": {"id": 786, "call_id": 812, "created_at": "2024-08-27T10:54:16.000Z", "content": ["payment", "billing"]}},
        [["id"]],
    ),
    "call_summaries": (
        "summary",
        {},
        {"summary": {"id": 974, "call_id": 812, "created_at": "2024-08-27T10:54:16.000Z", "content": "Short summary of the call"}},
        [["id"]],
    ),
    "call_action_items": (
        "action_items",
        {},
        {
            "call_id": 812,
            "action_items": [
                {
                    "ai_generated": False,
                    "content": "Send email to customer next week with updated offer details.",
                    "created_at": "2024-08-28T12:32:16.000Z",
                    "created_by": 74550,
                    "id": 1,
                    "updated_at": "2024-08-28T12:49:12.000Z",
                    "updated_by": 74550,
                },
                {"ai_generated": True, "content": "Schedule meeting for next monday.", "created_at": "2024-08-27T10:54:16.000Z", "id": 2},
            ],
        },
        [["call_id"], ["id"]],
    ),
    "call_playbook_results": (
        "playbook_result",
        {"fetch_playbook": "true"},
        {
            "id": 1,
            "call_id": 812,
            "user_id": 786,
            "number_id": 35550,
            "adherence_score": 0,
            "playbook_result_topics": [{"name": "Budget", "result": "content"}, {"name": "Need", "result": "content"}],
            "created_at": 1753095768,
            "playbook": {"id": 2, "name": "BANT", "language": "en"},
        },
        [["id"]],
    ),
}
_STREAM_NAMES = list(_STREAMS)
_CI_403_MESSAGE = (
    "Aircall returned HTTP 403 for {url}. Conversation intelligence needs the AI Assist or AI Assist Pro package and an "
    "active, verified Aircall company. Add the package to your Aircall plan, or deselect this stream. To drop all six "
    "conversation intelligence streams, turn off Sync conversation intelligence (AI Assist) and refresh the source schema."
)
# Playbook results need AI Assist Pro: a company with AI Assist only must deselect this stream, not turn the option off.
_PLAYBOOK_403_MESSAGE = (
    "Aircall returned HTTP 403 for {url}. Playbook results need the AI Assist Pro package and an active, verified "
    "Aircall company. Add AI Assist Pro to your Aircall plan, or deselect the call_playbook_results stream."
)


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("time.sleep", lambda *_args, **_kwargs: None)


def _epoch(value: str) -> int:
    return int(datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp())


def _json(body: dict, status_code: int = 200) -> HttpResponse:
    return HttpResponse(body=json.dumps(body), status_code=status_code)


def _calls_request(start: int, end: int) -> HttpRequest:
    query = {"from": str(start), "to": str(end), "per_page": "50", "fetch_call_timeline": "true"}
    return HttpRequest(f"{_BASE_URL}/calls", query_params=query)


def _child_request(stream_name: str, call_id: int) -> HttpRequest:
    suffix, query, _, _ = _STREAMS[stream_name]
    return HttpRequest(f"{_BASE_URL}/calls/{call_id}/{suffix}", query_params=query)


def _read(stream_name: str, sync_mode: SyncMode = SyncMode.full_refresh, state=None, expecting_exception: bool = False) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(stream_name, sync_mode).build()
    return read(
        get_source(_CI_CONFIG, state=state), config=_CI_CONFIG, catalog=catalog, state=state, expecting_exception=expecting_exception
    )


def _mock_calls(http_mocker: HttpMocker, calls: list[dict]) -> None:
    end = _epoch(_NOW)
    http_mocker.get(_calls_request(end - 365 * _DAY, end), _json({"calls": calls}))


def _app_error(status_code: int, troubleshoot: str) -> HttpResponse:
    error = {403: "Forbidden", 404: "Not Found"}[status_code]
    return _json({"error": error, "message": error.upper().replace(" ", "_"), "troubleshoot": troubleshoot, "success": False}, status_code)


def test_option_off_hides_the_streams_and_sends_no_request() -> None:
    names = {stream.name for stream in get_source(_CONFIG).discover(None, _CONFIG).streams}
    assert names.isdisjoint(_STREAM_NAMES)
    assert "calls" in names

    # A connection that selected the streams before turning the option off: nothing is mocked, so any request fails.
    with freeze_time(_NOW), HttpMocker():
        catalog = CatalogBuilder()
        for name in _STREAM_NAMES:
            catalog = catalog.with_stream(name, SyncMode.incremental)
        output = read(get_source(_CONFIG), config=_CONFIG, catalog=catalog.build())

    assert output.errors == []
    assert output.records == []


def test_option_off_reports_a_still_selected_stream_as_incomplete() -> None:
    # The usual case after turning the option off without refreshing the schema: calls is selected too.
    with freeze_time(_NOW), HttpMocker() as http_mocker:
        _mock_calls(http_mocker, [{"id": 812, "started_at": _epoch(_NOW) - _DAY}])
        catalog = CatalogBuilder().with_stream("calls", SyncMode.incremental).with_stream("call_summaries", SyncMode.incremental)
        output = read(get_source(_CONFIG), config=_CONFIG, catalog=catalog.build())

    assert output.errors == []
    assert [record.record.stream for record in output.records] == ["calls"]
    assert output.get_stream_statuses("call_summaries") == [AirbyteStreamStatus.INCOMPLETE]
    assert output.get_stream_statuses("calls")[-1] == AirbyteStreamStatus.COMPLETE


def test_option_on_discovers_the_streams_with_keys_and_cursor() -> None:
    streams = {stream.name: stream for stream in get_source(_CI_CONFIG).discover(None, _CI_CONFIG).streams}

    for name, (_, _, _, primary_key) in _STREAMS.items():
        stream = streams[name]
        assert stream.source_defined_primary_key == primary_key, name
        assert stream.default_cursor_field == ["call_started_at"], name
        assert [mode.value for mode in stream.supported_sync_modes] == ["full_refresh", "incremental"], name
        properties = stream.json_schema["properties"]
        assert "integer" in properties["call_id"]["type"], name
        assert "number" in properties["call_started_at"]["type"], name


@pytest.mark.parametrize("stream_name", _STREAM_NAMES)
def test_reads_the_reference_sample_with_call_id_and_call_started_at(stream_name: str) -> None:
    started_at = _epoch(_NOW) - 2 * _DAY
    with freeze_time(_NOW), HttpMocker() as http_mocker:
        _mock_calls(http_mocker, [{"id": 812, "started_at": started_at}])
        request = _child_request(stream_name, 812)
        http_mocker.get(request, _json(_STREAMS[stream_name][2]))

        output = _read(stream_name)

        assert output.errors == []
        assert output.records
        schema = get_source(_CI_CONFIG).discover(None, _CI_CONFIG)
        json_schema = next(stream.json_schema for stream in schema.streams if stream.name == stream_name)
        for record in output.records:
            data = record.record.data
            assert data["call_id"] == 812
            assert data["call_started_at"] == started_at
            assert [error.message for error in Draft7Validator(json_schema).iter_errors(data)] == []
        http_mocker.assert_number_of_calls(request, 1)
    if stream_name == "call_action_items":
        assert [(record.record.data["call_id"], record.record.data["id"]) for record in output.records] == [(812, 1), (812, 2)]
    if stream_name == "call_transcriptions":
        assert output.records[0].record.data["content"]["utterances"][1]["user_id"] == 123


@pytest.mark.parametrize("stream_name", _STREAM_NAMES)
def test_404_for_a_call_is_ignored_with_the_url(stream_name: str) -> None:
    started_at = _epoch(_NOW) - 2 * _DAY
    with freeze_time(_NOW), HttpMocker() as http_mocker:
        _mock_calls(http_mocker, [{"id": 811, "started_at": started_at}, {"id": 812, "started_at": started_at + 1}])
        missed = _child_request(stream_name, 811)
        # The body Aircall returns for a call without a result (live, 2026-11-11).
        http_mocker.get(missed, _json({"error": "NotFound", "troubleshoot": "Summary not found"}, 404))
        http_mocker.get(_child_request(stream_name, 812), _json(_STREAMS[stream_name][2]))

        output = _read(stream_name)

        assert output.errors == []
        assert {record.record.data["call_id"] for record in output.records} == {812}
        url = f"{_BASE_URL}/calls/811/{_STREAMS[stream_name][0]}"
        assert f"Ignoring {url}: Aircall has no result of this type for this call (HTTP 404)." in [log.log.message for log in output.logs]
        http_mocker.assert_number_of_calls(missed, 1)


@pytest.mark.parametrize("stream_name", _STREAM_NAMES)
@pytest.mark.parametrize(
    "response",
    [_json({"message": "Not Found"}, 404), _app_error(404, "call_id not found")],
    ids=["gateway_body", "spaced_not_found_body"],
)
def test_404_with_another_body_fails_instead_of_skipping_the_call(stream_name: str, response: HttpResponse) -> None:
    # A retired or renamed route answers 404 without Aircall's NotFound body; skipping it would hide the outage.
    with freeze_time(_NOW), HttpMocker() as http_mocker:
        _mock_calls(http_mocker, [{"id": 812, "started_at": _epoch(_NOW) - _DAY}])
        child_request = _child_request(stream_name, 812)
        http_mocker.get(child_request, response)

        output = _read(stream_name, expecting_exception=True)

        http_mocker.assert_number_of_calls(child_request, 1)
        assert output.records == []
        error = output.errors[0].trace.error
        assert error.failure_type == FailureType.system_error
        assert "404" in error.message


@pytest.mark.parametrize("stream_name", _STREAM_NAMES)
def test_403_without_ai_assist_is_a_config_error_naming_the_option(stream_name: str) -> None:
    with freeze_time(_NOW), HttpMocker() as http_mocker:
        _mock_calls(http_mocker, [{"id": 812, "started_at": _epoch(_NOW) - _DAY}])
        http_mocker.get(_child_request(stream_name, 812), _app_error(403, "Forbidden access: company cannot access this feature."))

        output = _read(stream_name, expecting_exception=True)

        assert output.errors
        error = output.errors[0].trace.error
        assert error.failure_type == FailureType.config_error
        message = _PLAYBOOK_403_MESSAGE if stream_name == "call_playbook_results" else _CI_403_MESSAGE
        assert error.message == message.format(url=f"{_BASE_URL}/calls/812/{_STREAMS[stream_name][0]}")


@pytest.mark.parametrize("stream_name", _STREAM_NAMES)
def test_401_keeps_the_api_key_message(stream_name: str) -> None:
    with freeze_time(_NOW), HttpMocker() as http_mocker:
        _mock_calls(http_mocker, [{"id": 812, "started_at": _epoch(_NOW) - _DAY}])
        http_mocker.get(_child_request(stream_name, 812), _json({"message": "Unauthorized"}, 401))

        output = _read(stream_name, expecting_exception=True)

        error = output.errors[0].trace.error
        assert error.failure_type == FailureType.config_error
        assert error.message.startswith("Aircall rejected the API ID and API token (HTTP 401).")


@pytest.mark.parametrize("stream_name", _STREAM_NAMES)
def test_gateway_403_keeps_the_credentials_message(stream_name: str) -> None:
    with freeze_time(_NOW), HttpMocker() as http_mocker:
        _mock_calls(http_mocker, [{"id": 812, "started_at": _epoch(_NOW) - _DAY}])
        http_mocker.get(_child_request(stream_name, 812), _json({"message": "Forbidden"}, 403))

        output = _read(stream_name, expecting_exception=True)

        error = output.errors[0].trace.error
        assert error.failure_type == FailureType.config_error
        url = f"{_BASE_URL}/calls/812/{_STREAMS[stream_name][0]}"
        assert error.message.startswith(f"Aircall returned HTTP 403 for {url}. Check that the API ID and API token")


def _summary(call_id: int) -> HttpResponse:
    return _json({"summary": {"id": call_id * 10, "call_id": call_id, "content": f"Summary {call_id}"}})


def test_a_call_without_started_at_still_gives_a_valid_record() -> None:
    with freeze_time(_NOW), HttpMocker() as http_mocker:
        _mock_calls(http_mocker, [{"id": 1, "started_at": None}, {"id": 2}, {"id": 3, "started_at": _epoch(_NOW) - _DAY}])
        for call_id in (1, 2, 3):
            http_mocker.get(_child_request("call_summaries", call_id), _summary(call_id))

        output = _read("call_summaries", SyncMode.incremental)

    assert output.errors == []
    records = {record.record.data["call_id"]: record.record.data for record in output.records}
    assert sorted(records) == [1, 2, 3]
    assert records[3]["call_started_at"] == _epoch(_NOW) - _DAY
    schema = next(
        stream.json_schema for stream in get_source(_CI_CONFIG).discover(None, _CI_CONFIG).streams if stream.name == "call_summaries"
    )
    for data in records.values():
        assert [error.message for error in Draft7Validator(schema).iter_errors(data)] == []


def test_next_sync_requests_only_children_of_calls_in_the_new_calls_window() -> None:
    first_sync, second_sync = "2026-11-02T00:00:00Z", "2026-11-02T01:00:00Z"
    # Call 2 is dated after the first sync (clock skew); it must not leave the next sync without child requests.
    old_call, future_call, new_call = _epoch(first_sync) - 10 * _DAY, _epoch(first_sync) + 7200, _epoch(first_sync) + 1800
    with freeze_time(first_sync), HttpMocker() as http_mocker:
        end = _epoch(first_sync)
        http_mocker.get(
            _calls_request(end - 365 * _DAY, end),
            _json({"calls": [{"id": 1, "started_at": old_call}, {"id": 2, "started_at": future_call}]}),
        )
        http_mocker.get(_child_request("call_summaries", 1), _summary(1))
        http_mocker.get(_child_request("call_summaries", 2), _summary(2))

        output = _read("call_summaries", SyncMode.incremental)

        assert output.errors == []
        assert sorted(record.record.data["call_id"] for record in output.records) == [1, 2]
        state = output.most_recent_state.stream_state
        assert state.use_global_cursor is True
        assert state.parent_state["calls"]["started_at"] == str(future_call)

    with freeze_time(second_sync), HttpMocker() as http_mocker:
        # The calls read restarts three days before its saved cursor; call 1 is outside it and is not requested.
        calls = _calls_request(future_call - 3 * _DAY, _epoch(second_sync))
        http_mocker.get(calls, _json({"calls": [{"id": 2, "started_at": future_call}, {"id": 3, "started_at": new_call}]}))
        reread, new = _child_request("call_summaries", 2), _child_request("call_summaries", 3)
        http_mocker.get(reread, _summary(2))
        http_mocker.get(new, _summary(3))

        output = _read(
            "call_summaries",
            SyncMode.incremental,
            state=StateBuilder().with_stream_state("call_summaries", state.__dict__).build(),
        )

        assert output.errors == []
        assert sorted(record.record.data["call_id"] for record in output.records) == [2, 3]
        for request in (calls, reread, new):
            http_mocker.assert_number_of_calls(request, 1)
        state = output.most_recent_state.stream_state
        assert state.parent_state["calls"]["started_at"] == str(future_call)
        assert state.state["call_started_at"] == str(future_call)
