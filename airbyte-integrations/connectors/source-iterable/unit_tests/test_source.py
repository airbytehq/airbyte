#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import pytest
import responses
from source_iterable.source import SourceIterable


@responses.activate
@pytest.mark.parametrize("body, status, expected_streams", [(b"alpha@gmail.com\nbeta@gmail.com", 200, 44)])
def test_source_streams(config, body, status, expected_streams):
    responses.get("https://api.iterable.com/api/lists", json={"lists": [{"id": 1}]})
    responses.add(responses.GET, "https://api.iterable.com/api/lists/getUsers?listId=1", body=body, status=status)

    streams = SourceIterable().streams(config=config)

    assert len(streams) == expected_streams


@responses.activate
def test_source_check_connection_failed(config):
    responses.get("https://api.iterable.com/api/lists", json={}, status=401)

    assert SourceIterable().check_connection(MagicMock(), config=config)[0] is False


@responses.activate
def test_source_check_connection_ok(config):
    responses.get("https://api.iterable.com/api/lists", json={"lists": [{"id": 1}]})

    assert SourceIterable().check_connection(MagicMock(), config=config) == (True, None)
