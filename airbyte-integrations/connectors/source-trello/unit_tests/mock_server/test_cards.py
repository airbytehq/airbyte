# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import jsonschema
import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import discover, read
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


@pytest.mark.parametrize(
    "cards",
    [
        [
            {"id": "card-with-location", "address": "123 Test Street", "locationName": "Test office"},
            {"id": "card-without-location"},
        ],
        [],
    ],
)
def test_cards_read_includes_location_fields_and_conforms_to_schema(source_factory, cards):
    config = ConfigBuilder().build()
    requests = TrelloRequestBuilder(config)
    response = TrelloResponseBuilder.records
    catalog = CatalogBuilder().with_stream("cards", SyncMode.full_refresh).build()

    discovery = discover(source_factory(config, catalog), config)
    schema = next(stream.json_schema for stream in discovery.catalog.catalog.streams if stream.name == "cards")
    assert schema["properties"]["address"]["type"] == ["null", "string"]
    assert schema["properties"]["locationName"]["type"] == ["null", "string"]

    with HttpMocker() as http_mocker:
        http_mocker.get(requests.parent("boards"), response([{"id": "b1"}]))
        http_mocker.get(requests.parent("organizations"), response([]))
        http_mocker.get(requests.cards("b1"), response(cards))
        if cards:
            http_mocker.get(requests.cards("b1", before=cards[-1]["id"]), response([]))

        output = read(source_factory(config, catalog), config=config, catalog=catalog)

    records = [message.record.data for message in output.records]
    assert records == cards
    assert not output.errors
    for record in records:
        jsonschema.validate(record, schema)
