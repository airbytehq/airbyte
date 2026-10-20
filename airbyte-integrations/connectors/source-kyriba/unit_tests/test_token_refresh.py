#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
from source_kyriba.source import Accounts, KyribaClient

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.utils.traced_exception import AirbyteTracedException


GATEWAY_URL = "https://demo.kyriba.com/gateway"
TOKEN_URL = f"{GATEWAY_URL}/oauth/token"
ACCOUNTS_URL = f"{GATEWAY_URL}/api/v1/accounts"
ACCOUNTS_PAGE = {
    "metadata": {"links": {}, "pageOffset": 0, "pageLimit": 100},
    "results": [{"uuid": "account-1"}],
}


@pytest.fixture(autouse=True)
def disable_cache_and_sleep(mocker):
    # Accounts uses the requests cache; disable it so a response cached by another test is not replayed
    mocker.patch.object(Accounts, "use_cache", False)
    mocker.patch("time.sleep")


def _accounts_stream() -> Accounts:
    client = KyribaClient("username", "password", GATEWAY_URL)
    return Accounts(gateway_url=GATEWAY_URL, client=client, start_date="2022-01-01")


def _mock_token_endpoint(requests_mock):
    return requests_mock.post(
        TOKEN_URL,
        [
            {"json": {"access_token": "expired-token"}, "status_code": 200},
            {"json": {"access_token": "fresh-token"}, "status_code": 200},
        ],
    )


def test_expired_token_is_refreshed_and_request_retried(requests_mock):
    token_endpoint = _mock_token_endpoint(requests_mock)
    sent_auth_headers = []

    def accounts_response(request, context):
        # the CDK re-applies auth to the same PreparedRequest on retry, so capture the header at call time
        sent_auth_headers.append(request.headers["Authorization"])
        if request.headers["Authorization"] == "Bearer expired-token":
            context.status_code = 401
            return {"error": "invalid_token"}
        return ACCOUNTS_PAGE

    requests_mock.get(ACCOUNTS_URL, json=accounts_response)

    records = list(_accounts_stream().read_records(sync_mode=SyncMode.full_refresh))

    assert records == [{"uuid": "account-1"}]
    assert token_endpoint.call_count == 2
    assert sent_auth_headers == ["Bearer expired-token", "Bearer fresh-token"]


def test_unauthorized_after_token_refresh_fails_as_config_error(requests_mock):
    token_endpoint = _mock_token_endpoint(requests_mock)
    requests_mock.get(ACCOUNTS_URL, status_code=401, json={"error": "invalid_token"})

    with pytest.raises(AirbyteTracedException) as exc_info:
        list(_accounts_stream().read_records(sync_mode=SyncMode.full_refresh))

    assert exc_info.value.failure_type == FailureType.config_error
    assert token_endpoint.call_count == 2
