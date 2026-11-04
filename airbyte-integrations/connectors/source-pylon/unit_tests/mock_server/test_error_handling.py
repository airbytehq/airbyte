# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest
from freezegun import freeze_time

from airbyte_cdk.models import FailureType, Status
from airbyte_cdk.test.mock_http import HttpMocker
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
        (403, "wrong_region_token", "EU tokens starting with pylon_api_eu_"),
        (401, "invalid_api_token", "Settings > Integrations & dev > API tokens"),
        (401, "invalid_authorization_header", "without a 'Bearer ' prefix or spaces"),
        (403, "organization_deactivated", "Contact Pylon support"),
        (403, "organization_suspended", "Contact Pylon support"),
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
@freeze_time(NOW)
def test_missing_parent_is_a_failure(stream: str, suffix: str) -> None:
    parent = fixture_record("issues")
    with HttpMocker() as mocker:
        mocker.post(search_request(), page([parent]))
        request = list_request(f"issues/{parent['id']}/{suffix}")
        mocker.get(request, error(404, "not_found"))
        output = run(stream, expecting_exception=True)
        mocker.assert_number_of_calls(request, 1)
    assert output.records == []
    assert output.errors
