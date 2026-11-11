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


@pytest.mark.parametrize("alerts", [[{"id": "alert-1"}, {"id": "alert-2"}], []])
def test_read_authenticates_parent_and_each_alert_page(http_mocker, alerts):
    config = ConfigBuilder().build()
    parent = MentionRequestBuilder.account_me().build()
    first_page = MentionRequestBuilder.alerts("account-1").build()
    http_mocker.get(parent, HttpResponse(body=json.dumps({"account": {"id": "account-1"}})))
    body = {"alerts": alerts, "_links": {}}
    if alerts:
        body["_links"] = {"more": {"params": {"cursor": "next-page"}}}
    http_mocker.get(first_page, HttpResponse(body=json.dumps(body)))
    next_page = MentionRequestBuilder.alerts("account-1").with_query_param("cursor", "next-page").build()
    if alerts:
        http_mocker.get(next_page, HttpResponse(body=json.dumps({"alerts": [{"id": "alert-3"}], "_links": {}})))

    output = read(
        get_source(config),
        config=config,
        catalog=CatalogBuilder().with_stream("alert", SyncMode.full_refresh).build(),
    )

    assert output.errors == []
    expected_ids = {"alert-1", "alert-2", "alert-3"} if alerts else set()
    assert {message.record.data["id"] for message in output.records} == expected_ids
    assert len(output.records) == len(expected_ids)
    http_mocker.assert_number_of_calls(parent, 1)
    http_mocker.assert_number_of_calls(first_page, 1)
    if alerts:
        http_mocker.assert_number_of_calls(next_page, 1)
