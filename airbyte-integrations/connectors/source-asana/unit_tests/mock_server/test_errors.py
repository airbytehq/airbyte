# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest

from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from unit_tests.mock_server.helpers import read_streams, request


@pytest.mark.parametrize("status", [402, 403, 404, 412, 451])
def test_ignored_errors_emit_no_records_or_error_logs(status: int) -> None:
    with HttpMocker() as http:
        target = request("workspaces")
        http.get(target, HttpResponse('{"errors":[{"message":"unavailable"}]}', status))
        output = read_streams("workspaces")
        assert not output.errors
        assert output.records == []
        assert not any(log.log.level == "ERROR" for log in output.logs)
        http.assert_number_of_calls(target, 1)
