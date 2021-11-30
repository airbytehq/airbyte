#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from unittest.mock import MagicMock

from pytest import fixture
from source_trello.source import TrelloStream


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
