#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from source_notion.source import SourceNotion


def test_streams():
    source = SourceNotion()
    config_mock = {"start_date": "2020-01-01T00:00:00.000Z", "credentials": {"auth_type": "token", "token": "abcd"}}
    streams = source.streams(config_mock)
    # Expecting 5 streams: users, databases, pages, comments, blocks
    expected_streams_number = 5
    assert len(streams) == expected_streams_number
