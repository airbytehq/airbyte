# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpResponse
from mock_server.config import ConfigBuilder
from mock_server.request_builder import MentionRequestBuilder


@pytest.mark.parametrize("api_key", ["test-api-key", "another-token"])
def test_read_sends_exact_bearer_authorization(http_mocker, api_key):
    config = ConfigBuilder().with_api_key(api_key).build()
    request = MentionRequestBuilder.account_me().with_api_key(api_key).build()
    http_mocker.get(request, HttpResponse(body=json.dumps({"account": {"id": "account-1"}})))

    output = read(
        get_source(config),
        config=config,
        catalog=CatalogBuilder().with_stream("account_me", SyncMode.full_refresh).build(),
    )

    assert output.errors == []
    assert [message.record.data["id"] for message in output.records] == ["account-1"]
    http_mocker.assert_number_of_calls(request, 1)
