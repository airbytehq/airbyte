# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from collections.abc import Callable

import jsonschema
import pytest

from airbyte_cdk.models import ConfiguredAirbyteCatalog, SyncMode
from airbyte_cdk.sources.declarative.concurrent_declarative_source import ConcurrentDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import discover, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


CONFIG = {"key": "test-key", "token": "test-token", "start_date": "2024-01-01T00:00:00Z", "board_ids": []}
SourceFactory = Callable[[dict, ConfiguredAirbyteCatalog], ConcurrentDeclarativeSource]


def cards_request(board_id: str, before: str | None = None) -> HttpRequest:
    params = {
        "list": "true",
        "sort": "-id",
        "since": CONFIG["start_date"],
        "members": "true",
        "pluginData": "true",
        "actions_display": "true",
        "customFieldItems": "true",
        "limit": "500",
    }
    if before:
        params["before"] = before
    return HttpRequest(url=f"https://api.trello.com/1/boards/{board_id}/cards/all", query_params=params)


def cards_catalog() -> ConfiguredAirbyteCatalog:
    return CatalogBuilder().with_stream("cards", SyncMode.full_refresh).build()


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
@HttpMocker()
def test_read_cards_conforms_to_discovered_schema(source_factory: SourceFactory, http_mocker: HttpMocker, cards: list[dict]) -> None:
    http_mocker.clear_all_matchers()
    board_id = "0123456789abcdef01234567"
    config = {**CONFIG, "board_ids": [board_id]}
    catalog = cards_catalog()
    http_mocker.get(cards_request(board_id), HttpResponse(json.dumps(cards), 200))
    if cards:
        http_mocker.get(cards_request(board_id, cards[-1]["id"]), HttpResponse("[]", 200))

    discovery = discover(source_factory(config, catalog), config)
    schema = next(stream.json_schema for stream in discovery.catalog.catalog.streams if stream.name == "cards")
    assert schema["properties"]["address"]["type"] == ["null", "string"]
    assert schema["properties"]["locationName"]["type"] == ["null", "string"]

    output = read(source_factory(config, catalog), config, catalog)
    records = [message.record.data for message in output.records]
    assert records == cards
    assert not output.errors
    for record in records:
        jsonschema.validate(record, schema)


@HttpMocker()
def test_read_cards_deduplicates_boards_and_organizations(source_factory: SourceFactory, http_mocker: HttpMocker) -> None:
    for endpoint, records in [
        ("boards", [{"id": "board-1"}, {"id": "board-2"}]),
        ("organizations", [{"id": "org-1", "idBoards": ["board-2", "board-3", "board-1"]}]),
    ]:
        http_mocker.get(
            HttpRequest(f"https://api.trello.com/1/members/me/{endpoint}", query_params={"since": CONFIG["start_date"]}),
            HttpResponse(json.dumps(records), 200),
        )
    expected = []
    for board_id in ["board-1", "board-2", "board-3"]:
        card = {"id": f"card-{board_id}", "idBoard": board_id}
        expected.append(card)
        http_mocker.get(cards_request(board_id), HttpResponse(json.dumps([card]), 200))
        http_mocker.get(cards_request(board_id, card["id"]), HttpResponse("[]", 200))

    catalog = cards_catalog()
    output = read(source_factory(CONFIG, catalog), CONFIG, catalog)

    assert sorted((message.record.data for message in output.records), key=lambda record: record["id"]) == expected
    assert not output.errors
