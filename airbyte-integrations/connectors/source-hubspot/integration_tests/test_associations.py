#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging

import pytest
from source_hubspot.source import SourceHubspot

from airbyte_cdk.models import ConfiguredAirbyteCatalog, Type


@pytest.fixture
def source():
    return SourceHubspot()


@pytest.fixture
def associations(config, source):
    streams = source.streams(config)
    return {stream.name: getattr(stream, "associations", []) for stream in streams}


@pytest.fixture
def configured_catalog(config, source):
    streams = source.streams(config)
    return {
        "streams": [
            {
                "stream": stream.as_airbyte_stream(),
                "sync_mode": "incremental",
                "cursor_field": [stream.cursor_field],
                "destination_sync_mode": "append",
            }
            for stream in streams
            if stream.supports_incremental and getattr(stream, "associations", [])
        ]
    }


def test_incremental_read_fetches_associations(config, configured_catalog, source, associations):
    messages = source.read(logging.getLogger("airbyte"), config, ConfiguredAirbyteCatalog.parse_obj(configured_catalog), {})

    association_found = False
    for message in messages:
        if message and message.type != Type.RECORD:
            continue
        record = message.record
        stream, data = record.stream, record.data
        # assume at least one association id is present
        stream_associations = associations[stream]
        for association in stream_associations:
            if data.get(association):
                association_found = True
                break
    assert association_found
