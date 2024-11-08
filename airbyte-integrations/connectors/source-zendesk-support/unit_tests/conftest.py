# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import os

from source_zendesk_support.source import SourceZendeskSupport

os.environ["REQUEST_CACHE_PATH"] = "REQUEST_CACHE_PATH"


def find_stream(stream_name, config):
    streams = SourceZendeskSupport().streams(config=config)

    # find by name
    for stream in streams:
        if stream.name == stream_name:
            return stream
    raise ValueError(f"Stream {stream_name} not found")
