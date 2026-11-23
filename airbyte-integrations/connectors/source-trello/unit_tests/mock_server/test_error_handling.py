# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import time

import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from mock_server.config import ConfigBuilder
from mock_server.request_builder import TrelloRequestBuilder
from mock_server.response_builder import TrelloResponseBuilder


BOARD_ID = "5f1e2d3c4b5a69788796a5b4"


@pytest.fixture
def sleeps(monkeypatch):
    calls = []
    monkeypatch.setattr(time, "sleep", calls.append)
    return calls


@pytest.mark.parametrize("status_code", [429, 500])
def test_retryable_error_is_retried_after_the_constant_backoff(source_factory, sleeps, status_code):
    config = ConfigBuilder().build()
    requests = TrelloRequestBuilder(config)
    catalog = CatalogBuilder().with_stream("boards", SyncMode.full_refresh).build()

    with HttpMocker() as http_mocker:
        boards = requests.parent("boards")
        http_mocker.get(boards, [HttpResponse(body="{}", status_code=status_code), TrelloResponseBuilder.records([{"id": BOARD_ID}])])

        output = read(source_factory(config, catalog), config=config, catalog=catalog)

        assert [message.record.data["id"] for message in output.records] == [BOARD_ID]
        http_mocker.assert_number_of_calls(boards, 2)
    # ConstantBackoffStrategy waits 10 s; the CDK adds 1 s to every backoff it computes.
    assert [seconds for seconds in sleeps if seconds] == [11]
