#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import json
import os
from typing import Any, Mapping

from source_linkedin_ads.source import SourceLinkedinAds

os.environ["REQUEST_CACHE_PATH"] = "REQUEST_CACHE_PATH"


def find_stream(stream_name, config):
    streams = SourceLinkedinAds().streams(config=config)

    # cache should be disabled once this issue is fixed https://github.com/airbytehq/airbyte-internal-issues/issues/6513
    for stream in streams:
        stream.retriever.requester.use_cache = True

    # find by name
    for stream in streams:
        if stream.name == stream_name:
            return stream
    raise ValueError(f"Stream {stream_name} not found")


def load_config(config_path: str) -> Mapping[str, Any]:
    with open(config_path, "r") as config:
        return json.load(config)
