# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest
from freezegun import freeze_time

from airbyte_cdk.models import Status
from airbyte_cdk.test.mock_http import HttpMocker
from mock_server.helpers import NOW, check, error, list_request, run


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
