# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest
from components import CustomAuthenticator
from requests.exceptions import ConnectionError, Timeout
from requests_mock import Mocker

from airbyte_cdk.models import FailureType
from airbyte_cdk.utils.traced_exception import AirbyteTracedException


@pytest.fixture(
    params=[("generate_access_token", "login", "login"), ("_get_refresh_access_token_response", "refresh", "access token refresh")]
)
def token_request(request):
    method, endpoint, operation = request.param
    authenticator = CustomAuthenticator(config={}, email="test-email", password="test-password", parameters={})
    authenticator._access_token = "old-access-token"
    authenticator._refreshToken = "old-refresh-token"
    return getattr(authenticator, method), f"https://api2.myhours.com/api/tokens/{endpoint}", operation


@pytest.mark.parametrize(
    "status,failure_type",
    [
        (400, FailureType.config_error),
        (401, FailureType.config_error),
        (403, FailureType.config_error),
        (429, FailureType.transient_error),
        (500, FailureType.transient_error),
        (503, FailureType.transient_error),
        (404, FailureType.system_error),
    ],
)
def test_http_error(token_request, requests_mock: Mocker, status: int, failure_type: FailureType) -> None:
    request_token, url, operation = token_request
    body = '{"message":"You don\'t have permissions to execute this action."}'
    requests_mock.post(url, status_code=status, text=body)

    with pytest.raises(AirbyteTracedException) as raised:
        request_token()

    assert raised.value.failure_type == failure_type
    expected_message = (
        f"My Hours rejected the {operation} for the configured email. "
        "Check the email and password, and confirm the user has permission to use the My Hours API."
        if failure_type == FailureType.config_error
        else f"My Hours access token request failed with HTTP {status}."
    )
    assert raised.value.message == expected_message
    assert raised.value.internal_message == f"HTTP {status}: {body}"
    assert requests_mock.call_count == 1


@pytest.mark.parametrize("error", [ConnectionError, Timeout])
def test_network_error(token_request, requests_mock: Mocker, error: type[Exception]) -> None:
    request_token, url, _ = token_request
    requests_mock.post(url, exc=error)

    with pytest.raises(AirbyteTracedException) as raised:
        request_token()

    assert raised.value.failure_type == FailureType.transient_error
    assert raised.value.message == "Connection to the My Hours API failed."
    assert requests_mock.call_count == 1


def test_success(token_request, requests_mock: Mocker) -> None:
    request_token, url, operation = token_request
    requests_mock.post(url, json={"accessToken": "new-access-token", "refreshToken": "new-refresh-token", "expiresIn": 3600})

    result = request_token()

    if operation == "login":
        assert result == ("new-access-token", "new-refresh-token")
    else:
        assert result == {"access_token": "new-access-token", "refresh_token": "new-refresh-token", "expires_in": 3600}
    assert requests_mock.call_count == 1
