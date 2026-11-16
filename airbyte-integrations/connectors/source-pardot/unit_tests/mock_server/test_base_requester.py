# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from unittest import TestCase

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse

from .config import ConfigBuilder
from .request_builder import PardotRequestBuilder, login_request
from .response_builder import login_response, page_response
from .utils import read_stream, read_streams, record_ids


def _request(path: str = "v5/objects/campaigns") -> PardotRequestBuilder:
    return PardotRequestBuilder.endpoint(path).with_any_query_params()


def _page(record_id: int) -> HttpResponse:
    return page_response([{"id": record_id, "updatedAt": "2026-03-01T09:00:00-08:00"}])


class TestBaseRequester(TestCase):
    @HttpMocker()
    def test_production_config_logs_in_at_login_salesforce_com(self, http_mocker: HttpMocker) -> None:
        login = login_request("login.salesforce.com")
        http_mocker.post(login, login_response())
        http_mocker.get(_request().build(), _page(1))

        output = read_stream("campaigns", config=ConfigBuilder().with_is_sandbox(False).build())

        assert record_ids(output) == [1]
        http_mocker.assert_number_of_calls(login, 1)

    @HttpMocker()
    def test_sandbox_config_logs_in_at_test_salesforce_com(self, http_mocker: HttpMocker) -> None:
        login = login_request("test.salesforce.com")
        http_mocker.post(login, login_response())
        http_mocker.get(_request().build(), _page(1))

        output = read_stream("campaigns", config=ConfigBuilder().with_is_sandbox(True).build())

        assert record_ids(output) == [1]
        http_mocker.assert_number_of_calls(login, 1)

    @HttpMocker()
    def test_sandbox_config_reads_from_the_production_api_host(self, http_mocker: HttpMocker) -> None:
        # The vendor serves sandboxes from pi.demo.pardot.com.
        request = _request().with_host("pi.pardot.com").build()
        http_mocker.post(login_request("test.salesforce.com"), login_response())
        http_mocker.get(request, _page(1))

        output = read_stream("campaigns", config=ConfigBuilder().with_is_sandbox(True).build())

        assert record_ids(output) == [1]
        http_mocker.assert_number_of_calls(request, 1)

    @HttpMocker()
    def test_each_stream_logs_in_for_itself(self, http_mocker: HttpMocker) -> None:
        login = login_request()
        http_mocker.post(login, login_response())
        http_mocker.get(_request("v5/objects/campaigns").build(), _page(1))
        http_mocker.get(_request("v5/objects/lists").build(), _page(2))

        output = read_streams(["campaigns", "lists"], SyncMode.full_refresh)

        assert sorted(record_ids(output)) == [1, 2]
        http_mocker.assert_number_of_calls(login, 2)
