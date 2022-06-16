#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json

from source_metabase import SourceMetabase


def test_source_streams():
    with open("secrets/config.json") as f:
        config = json.load(f)
    streams = SourceMetabase().streams(config=config)
    assert len(streams) == 5
