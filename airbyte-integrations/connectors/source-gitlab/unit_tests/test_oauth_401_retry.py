#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#
import pytest

from components import should_retry_with_refreshed_token


@pytest.mark.parametrize(
    "status_code,expected",
    [
        pytest.param(401, True, id="unauthorized_is_retried"),
        pytest.param(403, False, id="forbidden_is_not_retried"),
        pytest.param(200, False, id="ok_is_not_retried"),
        pytest.param(500, False, id="server_error_is_not_retried"),
    ],
)
def test_should_retry_with_refreshed_token(status_code, expected):
    assert should_retry_with_refreshed_token(status_code) is expected
