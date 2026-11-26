# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker
from mock_server.config import ConfigBuilder
from mock_server.request_builder import CARDS_QUERY, TrelloRequestBuilder
from mock_server.response_builder import TrelloResponseBuilder


BOARD_ID = "5f1e2d3c4b5a69788796a5b4"
START_DATE = "2024-01-01T00:00:00Z"


@pytest.mark.parametrize(
    ("stream", "path", "query", "paginated"),
    [
        ("boards", "members/me/boards", {"since": START_DATE}, False),
        ("organizations", "members/me/organizations", {"since": START_DATE}, False),
        # The DatetimeBasedCursor sends its slice start in the cursor's microsecond format.
        ("actions", f"boards/{BOARD_ID}/actions", {"since": "2024-01-01T00:00:00.000000Z", "limit": "500"}, True),
        ("cards", f"boards/{BOARD_ID}/cards/all", {**CARDS_QUERY, "since": START_DATE}, True),
        ("checklists", f"boards/{BOARD_ID}/checklists", {"since": START_DATE, "fields": "all", "checkItem_fields": "all"}, False),
        ("lists", f"boards/{BOARD_ID}/lists", {"since": START_DATE}, False),
        ("users", f"boards/{BOARD_ID}/members", {"since": START_DATE}, False),
    ],
)
def test_each_stream_requests_its_endpoint_with_the_api_key_header(source_factory, stream, path, query, paginated):
    config = ConfigBuilder().with_board_ids([BOARD_ID]).build()
    requests = TrelloRequestBuilder(config)
    response = TrelloResponseBuilder.records
    catalog = CatalogBuilder().with_stream(stream, SyncMode.full_refresh).build()
    record = {"id": BOARD_ID if stream == "boards" else f"{stream}-1", "date": "2024-02-01T00:00:00.000Z"}

    with HttpMocker() as http_mocker:
        first_page = requests.get(path, query)
        http_mocker.get(first_page, response([record]))
        if paginated:
            second_page = requests.get(path, {**query, "before": record["id"]})
            http_mocker.get(second_page, response([]))

        output = read(source_factory(config, catalog), config=config, catalog=catalog)

        assert [message.record.data["id"] for message in output.records] == [record["id"]]
        http_mocker.assert_number_of_calls(first_page, 1)
        if paginated:
            http_mocker.assert_number_of_calls(second_page, 1)
