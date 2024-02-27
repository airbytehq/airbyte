#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from source_recharge.source import SourceRecharge


def test_streams(config):
    streams = SourceRecharge().streams(config)
    assert len(streams) == 11
