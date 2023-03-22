#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

from source_trello.source import SourceTrello

from .helpers import NO_SLEEP_HEADERS


def test_streams(mocker):
    source = SourceTrello()
    config_mock = MagicMock()
    streams = source.streams(config_mock)
    expected_streams_number = 7
    assert len(streams) == expected_streams_number


def test_check_connection(requests_mock):
    config = {
        "start_date": "2020-01-01T00:00:00Z",
        "key": "key",
        "token": "token",
    }

    logger = MagicMock()

    requests_mock.get(
        "https://api.trello.com/1/members/me/boards",
        headers=NO_SLEEP_HEADERS,
        json=[
            {"id": "b11111111111111111111111", "name": "board_1"},
            {"id": "b22222222222222222222222", "name": "board_2"}
        ],
    )

    requests_mock.get(
        "https://api.trello.com/1/members/me/organizations",
        headers=NO_SLEEP_HEADERS,
        json=[{"id": "org111111111111111111111", "idBoards": ["b11111111111111111111111", "b22222222222222222222222"]}],
    )

    source = SourceTrello()
    status, error = source.check_connection(logger, config)
    assert status is True
    assert error is None
    config["board_ids"] = ["b11111111111111111111111", "b33333333333333333333333", "b44444444444444444444444"]
    status, error = source.check_connection(logger, config)
    assert status is False
    assert error == 'Board ID(s): b33333333333333333333333, b44444444444444444444444 not found'
