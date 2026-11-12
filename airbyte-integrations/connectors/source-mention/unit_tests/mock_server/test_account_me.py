# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from mock_server.config import ConfigBuilder
from mock_server.request_builder import MentionRequestBuilder


@pytest.mark.parametrize("api_key", ["test-api-key", "another-api-key"])
def test_read_sends_bearer_token_and_emits_account(api_key):
    config = ConfigBuilder().with_api_key(api_key).build()
    catalog = CatalogBuilder().with_stream("account_me", SyncMode.full_refresh).build()
    with HttpMocker() as http_mocker:
        http_mocker.get(
            MentionRequestBuilder.account_me_endpoint(api_key).build(),
            HttpResponse(json.dumps({"account": {"id": "account-123"}}), 200),
        )
        output = read(get_source(config), config=config, catalog=catalog)

    assert len(output.records) == 1
    assert output.records[0].record.data["id"] == "account-123"


def test_empty_account():
    config = ConfigBuilder().build()
    catalog = CatalogBuilder().with_stream("account_me", SyncMode.full_refresh).build()
    with HttpMocker() as http_mocker:
        http_mocker.get(
            MentionRequestBuilder.account_me_endpoint(config["api_key"]).build(),
            HttpResponse(json.dumps({"account": []}), 200),
        )
        output = read(get_source(config), config=config, catalog=catalog)

    assert len(output.records) == 0
    assert not output.errors


def test_invalid_token_fails_read():
    config = ConfigBuilder().with_api_key("invalid-token").build()
    catalog = CatalogBuilder().with_stream("account_me", SyncMode.full_refresh).build()
    with HttpMocker() as http_mocker:
        http_mocker.get(
            MentionRequestBuilder.account_me_endpoint(config["api_key"]).build(),
            HttpResponse(json.dumps({"error": "invalid_token"}), 401),
        )
        output = read(get_source(config), config=config, catalog=catalog, expecting_exception=True)

    assert len(output.records) == 0
    assert output.errors
