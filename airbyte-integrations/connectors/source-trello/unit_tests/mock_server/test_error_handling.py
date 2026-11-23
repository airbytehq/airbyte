# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from airbyte_cdk.test.models.outcome import ExpectedOutcome
from mock_server.config import ConfigBuilder
from mock_server.request_builder import TrelloRequestBuilder
from mock_server.response_builder import TrelloResponseBuilder


BOARD_ID = "5f1e2d3c4b5a69788796a5b4"
UNAUTHORIZED_MESSAGE = (
    "Trello rejected the credentials (HTTP 401). If the source uses OAuth 2.0, re-authenticate with Trello in the source "
    "settings. If it uses an API key and token, generate a new token in Trello and update it in the source settings."
)


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


def test_rejected_api_token_is_retried_then_fails_as_a_config_error(source_factory, sleeps):
    # The 401 filter asks for a token refresh, which API key credentials don't support, so the CDK retries the
    # request with the same token until the retries run out.
    config = ConfigBuilder().with_api_key_credentials().build()
    requests = TrelloRequestBuilder(config)
    catalog = CatalogBuilder().with_stream("boards", SyncMode.full_refresh).build()

    with HttpMocker() as http_mocker:
        boards = requests.parent("boards")
        http_mocker.get(boards, HttpResponse(body="invalid token", status_code=401))

        output = read(source_factory(config, catalog), config=config, catalog=catalog, expected_outcome=ExpectedOutcome.EXPECT_EXCEPTION)

        http_mocker.assert_number_of_calls(boards, 6)
    error = output.errors[0].trace.error
    assert error.failure_type == FailureType.config_error
    assert error.message == f"Exhausted available request attempts. Please see logs for more details. Exception: {UNAUTHORIZED_MESSAGE}"
    assert [seconds for seconds in sleeps if seconds] == [11] * 5
