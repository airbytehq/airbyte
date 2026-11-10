# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker
from mock_server.config import ConfigBuilder
from mock_server.request_builder import TrelloRequestBuilder
from mock_server.response_builder import TrelloResponseBuilder


def test_cards_read_deduplicates_boards_from_parent_streams(source_factory):
    config = ConfigBuilder().build()
    requests = TrelloRequestBuilder(config)
    response = TrelloResponseBuilder.records
    catalog = CatalogBuilder().with_stream("cards", SyncMode.full_refresh).build()

    with HttpMocker() as http_mocker:
        http_mocker.get(requests.parent("boards"), response([{"id": "b1"}, {"id": "b2"}]))
        http_mocker.get(requests.parent("organizations"), response([{"id": "org1", "idBoards": ["b2", "b3"]}]))
        board_requests = [requests.cards(board_id) for board_id in ("b1", "b2", "b3")]
        for board_id, request in zip(("b1", "b2", "b3"), board_requests):
            http_mocker.get(request, response([{"id": f"card-{board_id}"}]))
            http_mocker.get(requests.cards(board_id, before=f"card-{board_id}"), response([]))

        output = read(source_factory(config, catalog), config=config, catalog=catalog)

        assert sorted(record.record.data["id"] for record in output.records) == ["card-b1", "card-b2", "card-b3"]
        for request in board_requests:
            http_mocker.assert_number_of_calls(request, 1)
