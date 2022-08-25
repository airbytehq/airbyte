#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from source_iterable.source import SourceIterable


def test_source_streams():
    config = {"start_date": "2021-01-01", "api_key": "api_key"}
    streams = SourceIterable().streams(config=config)
    assert len(streams) == 18
