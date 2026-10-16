# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest

from airbyte_cdk.utils.traced_exception import AirbyteTracedException
from unit_tests.conftest import get_source


def test_oauth_authenticator_raises_config_error_for_invalid_grant(
    requests_mock,
) -> None:
    config = {
        "client_id": "amzn.app-oa2-client.test",
        "client_secret": "test-secret",
        "refresh_token": "expired-refresh-token",
        "region": "NA",
        "access_token": "expired-access-token",
        "token_expiry_date": "",
    }
    requests_mock.post(
        "https://api.amazon.com/auth/o2/token",
        status_code=400,
        json={"error": "invalid_grant", "error_description": "refresh token expired"},
    )
    authenticator = get_source(config).streams(config)[0].retriever.requester.authenticator

    with pytest.raises(AirbyteTracedException) as exc_info:
        authenticator.get_access_token()

    assert exc_info.value.failure_type.name == "config_error"
    assert exc_info.value.message == "Refresh token is invalid or expired. Please re-authenticate from Sources/<your source>/Settings."
