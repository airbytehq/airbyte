# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Unit tests for the trimmed App API key, the 401/403 messages, `Retry-After` backoff, 30 retries, the 10 requests per second
`api_budget`, the `campaigns_actions` 404 skip, the Start Date cap at now and the one-hour lookback."""

import logging
import time
from unittest import mock

import pytest
import requests_mock
from _helpers import get_source
from test_pagination_region_incremental import _BASE_CONFIG, _action, _campaign, _newsletter, _read, _stream_state

from airbyte_cdk.models import AirbyteStreamStatus, FailureType, Status, SyncMode
from airbyte_cdk.test.state_builder import StateBuilder


_API = "https://api.customer.io/v1"
_UNAUTHORIZED_MESSAGE = (
    "Customer.io rejected the App API key. Enter a valid App API key (not a Track API key), "
    "select the Region your Customer.io account is hosted in (US or EU), and if your account "
    "restricts API access by IP address, add the Airbyte IP addresses to the allowlist."
)
_FORBIDDEN_MESSAGE = (
    "Customer.io denied this App API key access to the requested data. Use an App API key "
    "whose scope includes this data, and if your account restricts API access by IP address, "
    "add the Airbyte IP addresses to the allowlist."
)
_PRIOR_CURSOR = 1701390800  # 2023-12-01T00:33:20Z
_START_DATE, _START_EPOCH = "2023-12-01T00:00:00Z", 1701388800  # _PRIOR_CURSOR - 2000, inside the lookback
_RECORD = {
    "campaigns": _campaign,
    "newsletters": _newsletter,
    "campaigns_actions": lambda action_id, updated: _action(action_id, 7, updated),
}


def _errors(status_code: int, detail: str) -> dict:
    """Error body in the shape the vendor OpenAPI documents (`components.responses.Unauthorized`)."""
    return {"errors": [{"detail": detail, "status": str(status_code)}]}


def _assert_config_error(output, stream_name: str, message: str) -> None:
    """One stream error carries `message`; it and the sync summary error are config_errors."""
    errors = [error_message.trace.error for error_message in output.errors]
    assert {error.failure_type for error in errors} == {FailureType.config_error}
    assert [error.message for error in errors if error.stream_descriptor and error.stream_descriptor.name == stream_name] == [message]
    assert output.get_stream_statuses(stream_name)[-1] == AirbyteStreamStatus.INCOMPLETE
    assert not output.records


@pytest.mark.parametrize(
    "status_code, detail, message",
    [(401, "unauthorized", _UNAUTHORIZED_MESSAGE), (403, "forbidden", _FORBIDDEN_MESSAGE)],
    ids=["401", "403"],
)
def test_auth_error_fails_read_with_config_error_naming_the_fix(status_code, detail, message):
    """401 and 403 fail the stream with a config_error that names the fix, without retrying."""
    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_API}/campaigns", status_code=status_code, json=_errors(status_code, detail))
        output = _read("campaigns", _BASE_CONFIG, expecting_exception=True)

    _assert_config_error(output, "campaigns", message)
    assert mocker.call_count == 1


def test_401_on_campaigns_actions_parent_request_names_the_fix():
    """The inline `campaigns` parent of `campaigns_actions` inherits the 401 filter."""
    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_API}/campaigns", status_code=401, json=_errors(401, "unauthorized"))
        output = _read("campaigns_actions", _BASE_CONFIG, expecting_exception=True)

    _assert_config_error(output, "campaigns_actions", _UNAUTHORIZED_MESSAGE)
    assert [request.path for request in mocker.request_history] == ["/v1/campaigns"]


def test_check_fails_with_401_message():
    """The check fails with the 401 message, not the generic "Unauthorized" one."""
    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_API}/campaigns", status_code=401, json=_errors(401, "unauthorized"))
        status = get_source(_BASE_CONFIG).check(logging.getLogger("airbyte"), _BASE_CONFIG)

    assert status.status == Status.FAILED
    assert _UNAUTHORIZED_MESSAGE in status.message


def test_429_waits_for_retry_after_then_emits_records():
    """A 429 is retried after the `Retry-After` wait instead of the default exponential one."""
    # Patches only the backoff handler's sleep; the api_budget wait after a 429 stays real (under 1 s).
    with requests_mock.Mocker() as mocker, mock.patch("airbyte_cdk.sources.streams.http.rate_limiting.time") as patched_time:
        mocker.get(
            f"{_API}/campaigns",
            [
                {"status_code": 429, "headers": {"Retry-After": "7"}, "json": _errors(429, "rate limited to 10 requests per 1s")},
                {"status_code": 200, "json": {"campaigns": [_campaign(1, _PRIOR_CURSOR)]}},
            ],
        )
        output = _read("campaigns", _BASE_CONFIG)

    assert [record.record.data["id"] for record in output.records] == [1]
    assert not output.errors
    assert output.get_stream_statuses("campaigns")[-1] == AirbyteStreamStatus.COMPLETE
    assert mocker.call_count == 2
    waits = [call.args[0] for call in patched_time.sleep.call_args_list]
    assert waits and min(waits) >= 7, f"expected waits of at least the 7 s Retry-After, got {waits}"


def test_future_start_date_passes_check_and_reads_no_records():
    """A Start Date in the future is capped at now: the check reaches the API and passes, the read emits nothing."""
    config = {**_BASE_CONFIG, "start_date": "2099-01-01T00:00:00Z"}
    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_API}/campaigns", json={"campaigns": [_campaign(1, _PRIOR_CURSOR)]})
        status = get_source(config).check(logging.getLogger("airbyte"), config)
        output = _read("campaigns", config)

    assert status.status == Status.SUCCEEDED, status.message
    assert mocker.call_count == 2  # one request for the check, one for the read
    assert not output.records
    assert not output.errors
    assert output.get_stream_statuses("campaigns")[-1] == AirbyteStreamStatus.COMPLETE


def _incremental_ids(stream_name: str, records: list, config: dict = _BASE_CONFIG) -> list:
    """Serve `records`, read `stream_name` incrementally from `_PRIOR_CURSOR` and return the emitted ids."""
    with requests_mock.Mocker() as mocker:
        if stream_name == "campaigns_actions":
            mocker.get(f"{_API}/campaigns", json={"campaigns": [_campaign(7, _PRIOR_CURSOR)]})
            mocker.get(f"{_API}/campaigns/7/actions", json={"actions": records, "next": None})
            # Campaign 8 holds the global cursor a day ahead, so a kept record proves campaign 7 uses its own cursor.
            state = (
                StateBuilder()
                .with_stream_state(
                    stream_name,
                    {
                        "use_global_cursor": False,
                        "states": [
                            {"partition": {"parent_id": 7, "parent_slice": {}}, "cursor": {"updated": str(_PRIOR_CURSOR)}},
                            {"partition": {"parent_id": 8, "parent_slice": {}}, "cursor": {"updated": str(_PRIOR_CURSOR + 86400)}},
                        ],
                        "state": {"updated": str(_PRIOR_CURSOR + 86400)},
                    },
                )
                .build()
            )
        else:
            mocker.get(f"{_API}/{stream_name}", json={stream_name: records, "next": None})
            state = _stream_state(stream_name, str(_PRIOR_CURSOR))
        output = _read(stream_name, config, SyncMode.incremental, state)
    return sorted(record.record.data["id"] for record in output.records)


@pytest.mark.parametrize("stream_name", ["campaigns", "newsletters", "campaigns_actions"])
def test_lookback_reemits_records_updated_within_one_hour_below_state(stream_name):
    """A record exactly one hour below the saved cursor is emitted again; one second older is not."""
    build = _RECORD[stream_name]
    assert _incremental_ids(stream_name, [build(1, _PRIOR_CURSOR - 3600), build(2, _PRIOR_CURSOR - 3601)]) == [1]


@pytest.mark.parametrize("stream_name", ["campaigns", "newsletters", "campaigns_actions"])
def test_start_date_floors_the_lookback(stream_name):
    """A record inside the lookback but below the Start Date is never emitted."""
    build = _RECORD[stream_name]
    config = {**_BASE_CONFIG, "start_date": _START_DATE}
    assert _incremental_ids(stream_name, [build(1, _START_EPOCH - 1), build(2, _PRIOR_CURSOR - 1800)], config) == [2]


def _serve_two_campaigns(mocker, first_actions: list) -> None:
    """Serve campaigns 1 and 2: campaign 1's actions get `first_actions`, campaign 2 returns action 201."""
    mocker.get(f"{_API}/campaigns", json={"campaigns": [_campaign(1, _PRIOR_CURSOR), _campaign(2, _PRIOR_CURSOR)]})
    mocker.get(f"{_API}/campaigns/1/actions", first_actions)
    mocker.get(f"{_API}/campaigns/2/actions", json={"actions": [_action(201, 2, _PRIOR_CURSOR)], "next": None})


def test_404_on_deleted_automation_actions_is_skipped():
    """A 404 for one automation's actions (deleted after the automation list was read) skips it and the sync completes."""
    with requests_mock.Mocker() as mocker:
        _serve_two_campaigns(mocker, [{"status_code": 404, "json": _errors(404, "not found")}])
        output = _read("campaigns_actions", _BASE_CONFIG)

    assert [record.record.data["id"] for record in output.records] == [201]
    assert not output.errors
    assert output.get_stream_statuses("campaigns_actions")[-1] == AirbyteStreamStatus.COMPLETE


def test_401_on_campaigns_actions_child_request_names_the_fix():
    """The `campaigns_actions` composite handler still ends a 401 on the shared message."""
    with requests_mock.Mocker() as mocker:
        _serve_two_campaigns(mocker, [{"status_code": 401, "json": _errors(401, "unauthorized")}])
        output = _read("campaigns_actions", _BASE_CONFIG, expecting_exception=True)

    errors = [error_message.trace.error for error_message in output.errors]
    assert {error.failure_type for error in errors} == {FailureType.config_error}
    assert _UNAUTHORIZED_MESSAGE in [
        error.message for error in errors if error.stream_descriptor and error.stream_descriptor.name == "campaigns_actions"
    ]
    assert output.get_stream_statuses("campaigns_actions")[-1] == AirbyteStreamStatus.INCOMPLETE


def test_429_on_campaigns_actions_child_request_waits_for_retry_after():
    """Child requests keep the shared `Retry-After` backoff through the composite handler."""
    with requests_mock.Mocker() as mocker, mock.patch("airbyte_cdk.sources.streams.http.rate_limiting.time") as patched_time:
        _serve_two_campaigns(
            mocker,
            [
                {"status_code": 429, "headers": {"Retry-After": "7"}, "json": _errors(429, "rate limited to 10 requests per 1s")},
                {"status_code": 200, "json": {"actions": [_action(101, 1, _PRIOR_CURSOR)], "next": None}},
            ],
        )
        output = _read("campaigns_actions", _BASE_CONFIG)

    assert sorted(record.record.data["id"] for record in output.records) == [101, 201]
    assert not output.errors
    waits = [call.args[0] for call in patched_time.sleep.call_args_list]
    assert waits and min(waits) >= 7, f"expected waits of at least the 7 s Retry-After, got {waits}"


def test_campaigns_actions_child_request_keeps_30_retries():
    """The composite takes max_retries from its first handler, so six 503s in a row still end in records (the default allows 5)."""
    responses = [{"status_code": 503, "json": _errors(503, "unavailable")}] * 6
    responses.append({"status_code": 200, "json": {"actions": [_action(101, 1, _PRIOR_CURSOR)], "next": None}})
    with requests_mock.Mocker() as mocker, mock.patch("airbyte_cdk.sources.streams.http.rate_limiting.time"):
        _serve_two_campaigns(mocker, responses)
        output = _read("campaigns_actions", _BASE_CONFIG)

    assert sorted(record.record.data["id"] for record in output.records) == [101, 201]
    assert not output.errors


def test_lookback_applies_to_a_campaign_missing_from_state():
    """A campaign missing from the state (a new or duplicated automation) starts one hour below the stream-wide cursor."""
    state = (
        StateBuilder()
        .with_stream_state(
            "campaigns_actions",
            {
                "use_global_cursor": False,
                "states": [{"partition": {"parent_id": 8, "parent_slice": {}}, "cursor": {"updated": str(_PRIOR_CURSOR)}}],
                "state": {"updated": str(_PRIOR_CURSOR)},
            },
        )
        .build()
    )
    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_API}/campaigns", json={"campaigns": [_campaign(7, _PRIOR_CURSOR)]})
        mocker.get(
            f"{_API}/campaigns/7/actions",
            json={"actions": [_action(1, 7, _PRIOR_CURSOR - 3600), _action(2, 7, _PRIOR_CURSOR - 3601)], "next": None},
        )
        output = _read("campaigns_actions", _BASE_CONFIG, SyncMode.incremental, state)

    assert [record.record.data["id"] for record in output.records] == [1]


@pytest.mark.parametrize("stream_name", ["campaigns", "newsletters"])
def test_shared_handler_keeps_30_retries(stream_name):
    """`base_requester` allows 30 retries, so six 503s in a row still end in records (the default allows 5)."""
    responses = [{"status_code": 503, "json": _errors(503, "unavailable")}] * 6
    responses.append({"status_code": 200, "json": {stream_name: [_RECORD[stream_name](1, _PRIOR_CURSOR)], "next": None}})
    with requests_mock.Mocker() as mocker, mock.patch("airbyte_cdk.sources.streams.http.rate_limiting.time"):
        mocker.get(f"{_API}/{stream_name}", responses)
        output = _read(stream_name, _BASE_CONFIG)

    assert [record.record.data["id"] for record in output.records] == [1]
    assert output.get_stream_statuses(stream_name)[-1] == AirbyteStreamStatus.COMPLETE


@pytest.mark.parametrize("region, host", [("US", "api.customer.io"), ("EU", "api-eu.customer.io")])
def test_api_budget_holds_the_eleventh_request_of_a_second(region, host):
    """One 10 requests per second policy covers the parent and child requests on either Region host."""
    with requests_mock.Mocker() as mocker, mock.patch("airbyte_cdk.sources.streams.call_rate.time", wraps=time) as budget_time:
        mocker.get(f"https://{host}/v1/campaigns", json={"campaigns": [_campaign(i, _PRIOR_CURSOR) for i in range(1, 11)]})
        for i in range(1, 11):
            mocker.get(f"https://{host}/v1/campaigns/{i}/actions", json={"actions": [_action(100 + i, i, _PRIOR_CURSOR)], "next": None})
        output = _read("campaigns_actions", {**_BASE_CONFIG, "region": region})

    assert len(output.records) == 10
    assert mocker.call_count == 11
    assert budget_time.sleep.called, "expected the api_budget to hold the 11th request"


def test_pasted_key_with_whitespace_is_trimmed():
    """A key pasted with surrounding whitespace or a trailing newline is sent trimmed."""
    with requests_mock.Mocker() as mocker:
        mocker.get(f"{_API}/campaigns", json={"campaigns": [_campaign(1, _PRIOR_CURSOR)]})
        output = _read("campaigns", {"app_api_key": " test-api-key\n"})

    assert [record.record.data["id"] for record in output.records] == [1]
    assert mocker.request_history[0].headers["Authorization"] == "Bearer test-api-key"
