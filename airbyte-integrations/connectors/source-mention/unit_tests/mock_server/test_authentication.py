# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse

from .config import ConfigBuilder
from .request_builder import MentionRequestBuilder


_ACCOUNT_ID = "acc_123"


@pytest.mark.parametrize(
    "api_key",
    [
        pytest.param("test-api-key", id="raw_key"),
        pytest.param("Bearer test-api-key", id="key_already_prefixed"),
    ],
)
def test_read_sends_api_key_as_bearer_token(api_key: str) -> None:
    config = ConfigBuilder().with_api_key(api_key).build()
    catalog = CatalogBuilder().with_stream("account_me", SyncMode.full_refresh).with_stream("alert", SyncMode.full_refresh).build()

    with HttpMocker() as http_mocker:
        http_mocker.get(
            MentionRequestBuilder.account_me_endpoint().with_authorization("Bearer test-api-key").build(),
            HttpResponse(body=json.dumps({"account": {"id": _ACCOUNT_ID, "name": "Acme"}}), status_code=200),
        )
        http_mocker.get(
            MentionRequestBuilder.alerts_endpoint(_ACCOUNT_ID)
            .with_query_param("limit", "100")
            .with_authorization("Bearer test-api-key")
            .build(),
            HttpResponse(body=json.dumps({"alerts": [{"id": "alert_1"}, {"id": "alert_2"}], "_links": {}}), status_code=200),
        )

        output = read(get_source(config=config), config, catalog)

    assert [r.record.data["id"] for r in output.records if r.record.stream == "account_me"] == [_ACCOUNT_ID]
    assert [r.record.data["id"] for r in output.records if r.record.stream == "alert"] == ["alert_1", "alert_2"]
    assert not output.errors
