#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock, patch

from source_iterable.source import SourceIterable
from source_iterable.streams import Lists


def test_source_streams(config):
    streams = SourceIterable().streams(config=config)
    assert len(streams) == 44


def test_source_check_connection_ok(config):
    with patch.object(Lists, "read_records", return_value=iter([1])):
        assert SourceIterable().check_connection(MagicMock(), config=config) == (True, None)


def test_source_check_connection_failed(config):
    with patch.object(Lists, "read_records", return_value=0):
        assert SourceIterable().check_connection(MagicMock(), config=config)[0] is False
