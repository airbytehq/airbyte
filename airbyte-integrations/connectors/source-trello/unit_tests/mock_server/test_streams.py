# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker
from mock_server.config import ConfigBuilder
from mock_server.request_builder import PAGINATED_STREAMS, STREAM_ENDPOINTS, TrelloRequestBuilder
from mock_server.response_builder import TrelloResponseBuilder


BOARD_ID = "5f1e2d3c4b5a69788796a5b4"


@pytest.mark.parametrize("stream", STREAM_ENDPOINTS)
def test_each_stream_requests_its_endpoint_with_the_api_key_header(source_factory, stream):
    config = ConfigBuilder().with_api_key_credentials().with_board_ids([BOARD_ID]).build()
    requests = TrelloRequestBuilder(config)
    response = TrelloResponseBuilder.records
    catalog = CatalogBuilder().with_stream(stream, SyncMode.full_refresh).build()
    record = {"id": BOARD_ID if stream == "boards" else f"{stream}-1", "date": "2024-02-01T00:00:00.000Z"}

    with HttpMocker() as http_mocker:
        first_page = requests.stream(stream, BOARD_ID)
        http_mocker.get(first_page, response([record]))
        if stream in PAGINATED_STREAMS:
            second_page = requests.stream(stream, BOARD_ID, before=record["id"])
            http_mocker.get(second_page, response([]))

        output = read(source_factory(config, catalog), config=config, catalog=catalog)

        assert [message.record.data["id"] for message in output.records] == [record["id"]]
        http_mocker.assert_number_of_calls(first_page, 1)
        if stream in PAGINATED_STREAMS:
            http_mocker.assert_number_of_calls(second_page, 1)
