#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock, patch

import pytest
import responses
from source_iterable.source import SourceIterable
from source_iterable.streams import Lists


@responses.activate
@pytest.mark.parametrize("body, status, expected_streams", ((b"", 401, 7), (b"", 200, 44), (b"alpha@gmail.com\nbeta@gmail.com", 200, 44)))
def test_source_streams(mock_lists_resp, config, body, status, expected_streams):
    responses.add(responses.GET, "https://api.iterable.com/api/lists/getUsers?listId=1", body=body, status=status)
    streams = SourceIterable().streams(config=config)
    assert len(streams) == expected_streams


def test_source_check_connection_ok(config):
    with patch.object(Lists, "read_records", return_value=iter([{"id": 1}])):
        assert SourceIterable().check_connection(MagicMock(), config=config) == (True, None)


def test_source_check_connection_failed(config):
    with patch.object(Lists, "read_records", return_value=iter([])):
        assert SourceIterable().check_connection(MagicMock(), config=config)[0] is False
