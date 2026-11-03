# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import logging

from _helpers import CONFIG, mock_user, request
from conftest import get_source

from airbyte_cdk.models import Status
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse


def test_check_only_reads_current_user() -> None:
    with HttpMocker() as http:
        target = mock_user(http)
        status = get_source(CONFIG).check(logging.getLogger("airbyte"), CONFIG)
        assert status.status == Status.SUCCEEDED
        http.assert_number_of_calls(target, 1)


def test_check_rejects_invalid_token() -> None:
    with HttpMocker() as http:
        target = request("users/me")
        http.get(target, HttpResponse(body='{"title":"Unauthenticated","message":"Token revoked"}', status_code=401))
        status = get_source(CONFIG).check(logging.getLogger("airbyte"), CONFIG)
        assert status.status == Status.FAILED
        assert "Create a new personal access token" in status.message
        http.assert_number_of_calls(target, 1)
