#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from source_snapchat_marketing.source import SourceSnapchatMarketing


def find_stream(stream_name, config):
    streams = SourceSnapchatMarketing().streams(config=config)

    # cache should be disabled once this issue is fixed https://github.com/airbytehq/airbyte-internal-issues/issues/6513
    for stream in streams:
        stream.retriever.requester.use_cache = True

    # find by name
    for stream in streams:
        if stream.name == stream_name:
            return stream
    raise ValueError(f"Stream {stream_name} not found")
