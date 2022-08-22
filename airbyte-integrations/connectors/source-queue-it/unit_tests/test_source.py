import requests_mock
from unittest.mock import MagicMock

from source_queue_it.source import SourceQueueIt


def test_streams():
    config = {
        "token": "test_token",
        "url_base": "test_url_base"
    }
    source = SourceQueueIt()
    streams = source.streams(config)
    expected_streams_number = 1
    assert len(streams) == expected_streams_number
