#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from itertools import cycle
from unittest.mock import MagicMock

from airbyte_cdk.sources.streams.http.auth.core import NoAuth
from pytest import fixture
from source_trello.source import Boards, Cards, TrelloStream
from source_trello.utils import read_full_refresh

from .helpers import NO_SLEEP_HEADERS


@fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(TrelloStream, "path", "v0/example_endpoint")
    mocker.patch.object(TrelloStream, "primary_key", "test_primary_key")
    mocker.patch.object(TrelloStream, "__abstractmethods__", set())


def test_request_params(patch_base_class, config):
    stream = TrelloStream(config)
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": {"before": "id"}}
    expected_params = {"limit": None, "since": "start_date", "before": "id"}
    assert stream.request_params(**inputs) == expected_params


def test_next_page_token(patch_base_class, config):
    stream = TrelloStream(config)
    inputs = {"response": MagicMock()}
    expected_token = None
    assert stream.next_page_token(**inputs) == expected_token


def test_boards_stream(requests_mock):
    mock_boards_request = requests_mock.get(
        "https://api.trello.com/1/members/me/boards",
        headers=NO_SLEEP_HEADERS,
        json=[{"id": "b11111111111111111111111", "name": "board_1"}, {"id": "b22222222222222222222222", "name": "board_2"}],
    )

    config = {"authenticator": NoAuth(), "start_date": "2021-02-11T08:35:49.540Z"}
    stream1 = Boards(config=config)
    records = list(read_full_refresh(stream1))
    assert records == [{"id": "b11111111111111111111111", "name": "board_1"}, {"id": "b22222222222222222222222", "name": "board_2"}]

    stream2 = Boards(config={**config, "board_ids": ["b22222222222222222222222"]})
    records = list(read_full_refresh(stream2))
    assert records == [{"id": "b22222222222222222222222", "name": "board_2"}]

    stream3 = Boards(config={**config, "board_ids": ["not-found"]})
    records = list(read_full_refresh(stream3))
    assert records == []

    assert mock_boards_request.call_count == 3


def test_cards_stream(requests_mock):
    mock_boards_request = requests_mock.get(
        "https://api.trello.com/1/members/me/boards",
        headers=NO_SLEEP_HEADERS,
        json=[{"id": "b11111111111111111111111", "name": "board_1"}, {"id": "b22222222222222222222222", "name": "board_2"}],
    )

    mock_organizations_request = requests_mock.get(
        "https://api.trello.com/1/members/me/organizations",
        headers=NO_SLEEP_HEADERS,
        json=[{"id": "org111111111111111111111", "idBoards": ["b11111111111111111111111", "b22222222222222222222222"]}],
    )

    json_responses1 = cycle([
        [{"id": "c11111111111111111111111", "name": "card_1"}, {"id": "c22222222222222222222222", "name": "card_2"}],
        [],
    ])

    mock_cards_request_1 = requests_mock.get(
        "https://api.trello.com/1/boards/b11111111111111111111111/cards/all",
        headers=NO_SLEEP_HEADERS,
        json=lambda request, context: next(json_responses1),
    )

    json_responses2 = cycle([
        [{"id": "c33333333333333333333333", "name": "card_3"}, {"id": "c44444444444444444444444", "name": "card_4"}],
        [],
    ])

    mock_cards_request_2 = requests_mock.get(
        "https://api.trello.com/1/boards/b22222222222222222222222/cards/all",
        headers=NO_SLEEP_HEADERS,
        json=lambda request, context: next(json_responses2),
    )

    config = {"authenticator": NoAuth(), "start_date": "2021-02-11T08:35:49.540Z"}
    stream1 = Cards(config=config)
    records = list(read_full_refresh(stream1))
    assert records == [
        {"id": "c11111111111111111111111", "name": "card_1"},
        {"id": "c22222222222222222222222", "name": "card_2"},
        {"id": "c33333333333333333333333", "name": "card_3"},
        {"id": "c44444444444444444444444", "name": "card_4"},
    ]

    stream2 = Cards(config={**config, "board_ids": ["b22222222222222222222222"]})
    records = list(read_full_refresh(stream2))
    assert records == [{"id": "c33333333333333333333333", "name": "card_3"}, {"id": "c44444444444444444444444", "name": "card_4"}]

    stream3 = Cards(config={**config, "board_ids": ["not-found"]})
    records = list(read_full_refresh(stream3))
    assert records == []

    assert mock_boards_request.call_count == 3
    assert mock_organizations_request.call_count == 3
    assert mock_cards_request_1.call_count == 2
    assert mock_cards_request_2.call_count == 4
