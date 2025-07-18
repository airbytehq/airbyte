#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging

import pytest
from source_hubspot.source import SourceHubspot

from airbyte_cdk.models import ConfiguredAirbyteCatalogSerializer, Type
from airbyte_cdk.sources.declarative.declarative_stream import DeclarativeStream


STREAM_TO_ASSOCIATIONS_MAP = {
    "companies": ["contacts"],
    "contacts": ["contacts", "companies"],
    "deals": ["companies", "contacts", "line_items"],
    "deals_archived": ["contacts", "companies", "line_items"],
    "engagements_calls": ["companies", "contacts", "deals", "tickets"],
    "engagements_emails": ["companies", "contacts", "deals", "tickets"],
    "engagements_meetings": ["companies", "contacts", "deals", "tickets"],
    "engagements_notes": ["companies", "contacts", "deals", "tickets"],
    "engagements_tasks": ["companies", "contacts", "deals", "tickets"],
    "leads": ["companies", "contacts"],
    "tickets": ["companies", "contacts", "deals"],
}


@pytest.fixture
def source(config):
    return SourceHubspot(config, None, None)


@pytest.fixture
def associations(config, source):
    streams = source.streams(config)
    return {stream.name: getattr(stream, "associations", []) for stream in streams}


@pytest.fixture
def configured_catalog(config, source):
    streams = source.streams(config)
    catalog = {"streams": []}
    for stream in streams:
        supports_incremental = stream.supports_incremental or (isinstance(stream, DeclarativeStream) and len(stream.cursor_field) > 0)
        if supports_incremental and STREAM_TO_ASSOCIATIONS_MAP.get(stream.name, []):
            stream_catalog = stream.as_airbyte_stream().__dict__
            stream_catalog["supported_sync_modes"] = [sync_mode.value for sync_mode in stream_catalog["supported_sync_modes"]]
            catalog["streams"].append(
                {
                    "stream": stream_catalog,
                    "sync_mode": "incremental",
                    "cursor_field": [stream.cursor_field],
                    "destination_sync_mode": "append",
                }
            )
    return ConfiguredAirbyteCatalogSerializer.load(catalog)


def test_incremental_read_fetches_associations(config, configured_catalog, source, associations):
    messages = source.read(logging.getLogger("airbyte"), config, configured_catalog, {})

    association_found = False
    for message in messages:
        if message and message.type != Type.RECORD:
            continue
        record = message.record
        stream, data = record.stream, record.data
        # assume at least one association id is present
        stream_associations = STREAM_TO_ASSOCIATIONS_MAP.get(stream)
        for association in stream_associations:
            if data.get(association):
                association_found = True
                break
    assert association_found
