#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from unittest.mock import MagicMock

from airbyte_cdk.sources.streams.http.auth.core import NoAuth
from pytest import fixture
from source_trello.source import Boards, TrelloStream


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
    headers = {
        "x-rate-limit-api-token-max": "1",
        "x-rate-limit-api-token-remaining": "1",
        "x-rate-limit-api-key-max": "1",
        "x-rate-limit-api-key-remaining": "1",
    }

    mock_boards_request = requests_mock.get(
        "https://api.trello.com/1/members/me/boards",
        headers=headers,
        json=[{"name": "board_1", "id": "611aa0ef37acd675af67dc9b"}, {"name": "board_2", "id": "611aa586ef5f2c8e1deec8b6"}],
    )

    config = {"authenticator": NoAuth(), "start_date": "2021-02-11T08:35:49.540Z"}
    stream1 = Boards(config=config)
    records = list(stream1.read_records(sync_mode=None))
    assert [
        {"id": "611aa0ef37acd675af67dc9b", "name": "board_1"},
        {"id": "611aa586ef5f2c8e1deec8b6", "name": "board_2"},
    ] == records

    stream2 = Boards(config={**config, "board_ids": ["611aa586ef5f2c8e1deec8b6"]})
    records = list(stream2.read_records(sync_mode=None))
    assert [{"id": "611aa586ef5f2c8e1deec8b6", "name": "board_2"}] == records

    assert mock_boards_request.call_count == 2
