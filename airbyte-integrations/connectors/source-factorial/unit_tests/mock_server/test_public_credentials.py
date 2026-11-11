# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest
from conftest import get_source

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_CONFIG = {"api_key": "test-api-key", "start_date": "2024-01-01T00:00:00Z"}
_REQUEST = HttpRequest(
    url="https://api.factorialhr.com/api/v2/resources/api_public/credentials",
    query_params={"page": "1", "limit": "2"},
    headers={"X-API-KEY": "test-api-key"},
)


@pytest.mark.parametrize("recovers", [True, False], ids=["429_then_success", "429_exhausts_retries"])
def test_rate_limit_retry_contract(monkeypatch: pytest.MonkeyPatch, recovers: bool) -> None:
    monkeypatch.setattr("time.sleep", lambda seconds: None)
    rate_limited = HttpResponse(body=json.dumps({"error": "Too Many Requests"}), status_code=429)
    responses = (
        [rate_limited, HttpResponse(body=json.dumps({"data": [{"id": 101}]}), status_code=200)]
        if recovers
        else rate_limited
    )
    catalog = CatalogBuilder().with_stream("public_credentials", SyncMode.full_refresh).build()

    with HttpMocker() as http_mocker:
        http_mocker.get(_REQUEST, responses)
        output = read(get_source(_CONFIG), _CONFIG, catalog, expecting_exception=not recovers)
        http_mocker.assert_number_of_calls(_REQUEST, 2 if recovers else 4)

    if recovers:
        assert [record.record.data["id"] for record in output.records] == [101]
        assert not output.errors
    else:
        assert not output.records
        assert output.errors
        error = output.errors[0].trace.error
        assert error.failure_type == FailureType.transient_error
        assert error.message == "API rate limit exceeded."
        assert error.internal_message == "Rate limit retry budget exhausted. Last exception: Rate limits hit"
