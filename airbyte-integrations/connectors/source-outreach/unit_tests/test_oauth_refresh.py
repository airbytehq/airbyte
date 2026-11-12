# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.models.outcome import ExpectedOutcome
from unit_tests.conftest import build_source


_CONFIG = {
    "client_id": "test-client-id",
    "client_secret": "test-client-secret",
    "refresh_token": "test-refresh-token",
    "redirect_uri": "https://example.com/callback",
    "start_date": "2020-11-16T00:00:00Z",
}
_TOKEN_URL = "https://api.outreach.io/oauth/token"
_MAILINGS_URL = "https://api.outreach.io/api/v2/mailings"


@pytest.mark.parametrize("result", ["record", "empty", "persistent_401", "429", "500"])
def test_read_refreshes_expired_access_token(requests_mock, monkeypatch, result):
    monkeypatch.setattr("time.sleep", lambda _: None)

    def token_response(request, context):
        return {"access_token": f"token_{tokens.call_count}", "expires_in": 7200}

    tokens = requests_mock.post(_TOKEN_URL, json=token_response)

    def mailings_response(request, context):
        if result == "persistent_401" or request.headers["Authorization"] == "Bearer token_1":
            context.status_code = int(result) if result in ("429", "500") else 401
            # Throttling/server errors should retry without refreshing the token.
            if result not in ("429", "500") or mailings.call_count == 1:
                return {"id": "expiredAccessToken", "message": "Access token has expired"}
        context.status_code = 200
        return {"data": [] if result == "empty" else [{"id": "mailing-1", "attributes": {"updatedAt": "2021-01-01T00:00:00.000Z"}}]}

    mailings = requests_mock.get(_MAILINGS_URL, json=mailings_response)
    catalog = CatalogBuilder().with_stream("mailings", SyncMode.full_refresh).build()
    output = read(
        build_source(_CONFIG),
        _CONFIG,
        catalog,
        expected_outcome=ExpectedOutcome.EXPECT_EXCEPTION if result == "persistent_401" else None,
    )

    if result == "persistent_401":
        assert not output.records
        assert output.errors
        assert any(error.trace.error.failure_type == FailureType.config_error for error in output.errors)
        assert tokens.call_count == 2
        assert mailings.call_count == 2
    else:
        assert [record.record.data["id"] for record in output.records] == ([] if result == "empty" else ["mailing-1"])
        assert not output.errors
        assert tokens.call_count == (1 if result in ("429", "500") else 2)
        assert mailings.call_count == 2
        assert mailings.last_request.headers["Authorization"] == ("Bearer token_1" if result in ("429", "500") else "Bearer token_2")
