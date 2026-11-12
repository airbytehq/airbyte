# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from unittest import TestCase

from unit_tests.conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from mock_server.config import ConfigBuilder
from mock_server.request_builder import MentionRequestBuilder


_API_KEY = "test_api_key"
_ACCOUNT_ID = "acc_1"


def _account_me_response() -> HttpResponse:
    return HttpResponse(body=json.dumps({"account": {"id": _ACCOUNT_ID, "name": "Test Account"}}), status_code=200)


class TestBearerAuthentication(TestCase):
    """The Mention API only accepts the API key as an OAuth2 bearer token: `Authorization: Bearer <key>`."""

    @HttpMocker()
    def test_account_me_sends_api_key_as_bearer_token(self, http_mocker: HttpMocker) -> None:
        config = ConfigBuilder().with_api_key(_API_KEY).build()
        http_mocker.get(MentionRequestBuilder.account_me_endpoint(_API_KEY).build(), _account_me_response())

        output = read(
            get_source(config=config),
            config=config,
            catalog=CatalogBuilder().with_stream("account_me", SyncMode.full_refresh).build(),
        )

        assert [record.record.data["id"] for record in output.records] == [_ACCOUNT_ID]
        assert not output.errors

    @HttpMocker()
    def test_alert_sends_api_key_as_bearer_token_to_parent_and_child_requests(self, http_mocker: HttpMocker) -> None:
        config = ConfigBuilder().with_api_key(_API_KEY).build()
        http_mocker.get(MentionRequestBuilder.account_me_endpoint(_API_KEY).build(), _account_me_response())
        http_mocker.get(
            MentionRequestBuilder.alerts_endpoint(_API_KEY, _ACCOUNT_ID).with_query_param("limit", "100").build(),
            HttpResponse(
                body=json.dumps({"alerts": [{"id": "alert_1", "name": "Brand"}, {"id": "alert_2", "name": "Competitor"}], "_links": {}}),
                status_code=200,
            ),
        )

        output = read(
            get_source(config=config),
            config=config,
            catalog=CatalogBuilder().with_stream("alert", SyncMode.full_refresh).build(),
        )

        assert [record.record.data["id"] for record in output.records] == ["alert_1", "alert_2"]
        assert not output.errors
