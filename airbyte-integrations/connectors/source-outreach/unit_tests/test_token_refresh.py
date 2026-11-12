# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import build_source
from unit_tests.test_jsonapi_records import _BASE_URL, _CONFIG, _TOKEN_URL, _query_params, _resource, _response


_EXPIRED = HttpResponse(
    body=json.dumps(
        {"id": "expiredAccessToken", "title": "Expired Access Token", "detail": "Please get a new access token and try again."}
    ),
    status_code=401,
)


@pytest.mark.parametrize("stream_name", ["mailings", "accounts"])
@pytest.mark.parametrize("resources", [[_resource("1", {"updatedAt": "2021-01-01T00:00:00.000Z"})], []], ids=["record", "empty"])
@pytest.mark.parametrize("persistent_401", [False, True], ids=["recovered", "revoked"])
def test_refreshes_expired_token_and_retries(stream_name, resources, persistent_401):
    token_request = HttpRequest(
        _TOKEN_URL,
        body="grant_type=refresh_token&client_id=test-client-id&client_secret=test-client-secret&refresh_token=test-refresh-token",
    )
    with HttpMocker() as http_mocker:
        http_mocker.post(
            token_request,
            [HttpResponse(body=json.dumps({"access_token": token, "expires_in": 3600}), status_code=200) for token in ["A", "B"]],
        )
        for token, response in [("A", _EXPIRED), ("B", _EXPIRED if persistent_401 else _response(resources))]:
            http_mocker.get(
                HttpRequest(
                    f"{_BASE_URL}/{stream_name}",
                    query_params=_query_params(stream_name),
                    headers={"Authorization": f"Bearer {token}"},
                ),
                response,
            )
        state = StateBuilder().build()
        catalog = CatalogBuilder().with_stream(stream_name, SyncMode.incremental).build()
        output = read(build_source(_CONFIG, state), _CONFIG, catalog, state)

        if persistent_401:
            assert not output.records
            assert output.errors
            assert output.errors[0].trace.error.failure_type == FailureType.config_error
        else:
            assert [record.record.data["id"] for record in output.records] == [resource["id"] for resource in resources]
            assert not output.errors
        http_mocker.assert_number_of_calls(token_request, 2)
