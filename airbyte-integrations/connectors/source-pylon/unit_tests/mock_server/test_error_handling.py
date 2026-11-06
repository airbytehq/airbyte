# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from unittest.mock import patch

import pytest
from freezegun import freeze_time

from airbyte_cdk.models import FailureType, Status
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from mock_server.helpers import NOW, check, error, fixture_record, list_request, page, run, search_request


@pytest.mark.parametrize("status", [400, 401, 403, 404])
@freeze_time(NOW)
def test_http_failures_are_not_silently_ignored(status):
    with HttpMocker() as mocker:
        request = list_request("tags")
        mocker.get(request, error(status))
        output = run("tags", expecting_exception=True)
        mocker.assert_number_of_calls(request, 1)
    assert output.records == []
    assert output.errors
    assert any(str(status) in message.trace.error.internal_message for message in output.errors)


@freeze_time(NOW)
def test_check_rejects_invalid_token():
    with HttpMocker() as mocker:
        mocker.get(list_request("tags"), error(401, "invalid_api_token"))
        output = check()
    assert output.connection_status_messages[0].connectionStatus.status == Status.FAILED


@pytest.mark.parametrize(
    "status,code,expected",
    [
        (
            401,
            "wrong_region_token",
            "Set Region to match the token: pylon_api_eu_ means EU, pylon_api_ means US, and older unprefixed tokens use the region where the Pylon tenant is hosted.",
        ),
        (401, "invalid_api_token", "Settings > Integrations & dev > API tokens"),
        (401, "invalid_authorization_header", "without a 'Bearer ' prefix or spaces"),
        (401, "organization_deactivated", "Contact Pylon support"),
        (401, "organization_suspended", "Contact Pylon support"),
        (401, "unrecognized_code", "update the token in your Airbyte source settings"),
        (403, "permission_denied", "https://api.usepylon.com/tags"),
    ],
)
@freeze_time(NOW)
def test_actionable_config_errors(status: int, code: str, expected: str) -> None:
    with HttpMocker() as mocker:
        request = list_request("tags")
        mocker.get(request, error(status, code))
        output = run("tags", expecting_exception=True)
        mocker.assert_number_of_calls(request, 1)
    assert output.records == []
    failures = [message.trace.error for message in output.errors]
    assert any(failure.failure_type == FailureType.config_error and expected in failure.message for failure in failures)


@pytest.mark.parametrize("stream,suffix", [("issue_messages", "messages"), ("issue_threads", "threads")])
@pytest.mark.parametrize("body", [{"code": "not_found"}, {}])
@freeze_time(NOW)
def test_missing_parent_is_a_failure(stream: str, suffix: str, body) -> None:
    parent = fixture_record("issues")
    with HttpMocker() as mocker:
        mocker.post(search_request(), page([parent]))
        request = list_request(f"issues/{parent['id']}/{suffix}")
        mocker.get(request, HttpResponse(json.dumps(body), status_code=404))
        output = run(stream, expecting_exception=True)
        mocker.assert_number_of_calls(request, 1)
    assert output.records == []
    assert output.errors


@pytest.mark.parametrize("body", [{"message": "Unable to fetch issue!"}, {"message": "Synthetic unrelated failure"}, {}])
@pytest.mark.parametrize("recover", [True, False])
@freeze_time(NOW)
def test_uncoded_thread_400_retries_are_bounded(body, recover) -> None:
    parent = fixture_record("issues")
    child = fixture_record("issue_threads")
    with patch("time.sleep") as sleep, patch("airbyte_cdk.sources.streams.call_rate.APIBudget.acquire_call"), HttpMocker() as mocker:
        mocker.post(search_request(), page([parent]))
        request = list_request(f"issues/{parent['id']}/threads")
        response = HttpResponse(json.dumps(body), status_code=400)
        mocker.get(request, [response, page([child])] if recover else response)
        output = run("issue_threads", expecting_exception=not recover)
        mocker.assert_number_of_calls(request, 2 if recover else 6)
        assert [call.args[0] for call in sleep.call_args_list if call.args[0] > 0] == ([11] if recover else [11, 21, 41, 81, 161])
    assert bool(output.errors) is not recover
    assert len(output.records) == (1 if recover else 0)


@pytest.mark.parametrize("code", ["invalid_request_body", None])
@freeze_time(NOW)
def test_thread_400_with_code_is_not_retried(code) -> None:
    parent = fixture_record("issues")
    with HttpMocker() as mocker:
        mocker.post(search_request(), page([parent]))
        request = list_request(f"issues/{parent['id']}/threads")
        mocker.get(request, error(400, code))
        output = run("issue_threads", expecting_exception=True)
        mocker.assert_number_of_calls(request, 1)
    assert output.errors
    assert output.records == []


@pytest.mark.parametrize("stream", ["tags", "issue_messages"])
@freeze_time(NOW)
def test_other_stream_uncoded_400_is_not_retried(stream) -> None:
    parent = fixture_record("issues")
    with HttpMocker() as mocker:
        if stream == "issue_messages":
            mocker.post(search_request(), page([parent]))
        request = list_request(f"issues/{parent['id']}/messages" if stream == "issue_messages" else "tags")
        mocker.get(request, HttpResponse(json.dumps({"message": "Unable to fetch issue!"}), status_code=400))
        output = run(stream, expecting_exception=True)
        mocker.assert_number_of_calls(request, 1)
    assert output.errors
    assert output.records == []


@pytest.mark.parametrize(
    "body,headers,wait",
    [
        ({"code": "rate_limited"}, {}, 11),
        ({}, {"Retry-After": "7"}, 8),
        ({"code": "rate_limited"}, {"X-Retry-After": "13"}, 14),
        ({"code": "rate_limited"}, {"Retry-After": "7", "X-Retry-After": "13"}, 8),
    ],
)
@pytest.mark.parametrize("stream,suffix", [("issue_threads", "threads"), ("issue_messages", "messages")])
@freeze_time(NOW)
def test_child_429_uses_shared_backoff(body, headers, wait, stream, suffix) -> None:
    parent = fixture_record("issues")
    with patch("time.sleep") as sleep, patch("airbyte_cdk.sources.streams.call_rate.APIBudget.acquire_call"), HttpMocker() as mocker:
        mocker.post(search_request(), page([parent]))
        request = list_request(f"issues/{parent['id']}/{suffix}")
        mocker.get(request, [HttpResponse(json.dumps(body), status_code=429, headers=headers), page([fixture_record(stream)])])
        output = run(stream)
        mocker.assert_number_of_calls(request, 2)
        assert [call.args[0] for call in sleep.call_args_list if call.args[0] > 0] == [wait]
    assert output.errors == []
    assert len(output.records) == 1
