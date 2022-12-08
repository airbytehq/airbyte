#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest import mock

from source_adjust.source import SourceAdjust

API_KEY = "API KEY"
CONFIG = {
    "api_token": API_KEY,
}


def test_check_connection():
    source = SourceAdjust()
    with mock.patch("requests.get") as http_get:
        assert source.check_connection(mock.MagicMock(), CONFIG) == (True, None)
        assert http_get.call_count == 1


def test_streams():
    source = SourceAdjust()
    streams = source.streams(CONFIG)
    expected_streams_number = 1
    assert len(streams) == expected_streams_number
