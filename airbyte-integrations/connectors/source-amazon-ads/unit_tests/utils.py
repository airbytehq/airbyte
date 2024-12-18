#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Iterator, MutableMapping
from unittest import mock
from urllib.parse import urlparse, urlunparse

from source_amazon_ads.config_migrations import MigrateStartDate

from airbyte_cdk.models import SyncMode
from airbyte_cdk.models.airbyte_protocol import ConnectorSpecification
from airbyte_cdk.sources import Source
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.utils.schema_helpers import check_config_against_spec_or_exit, split_config


def read_incremental(stream_instance: Stream, stream_state: MutableMapping[str, Any]) -> Iterator[dict]:
    if stream_state and "state" in dir(stream_instance):
        stream_instance.state = stream_state

    slices = stream_instance.stream_slices(sync_mode=SyncMode.incremental, stream_state=stream_state)
    for _slice in slices:
        records = stream_instance.read_records(sync_mode=SyncMode.incremental, stream_slice=_slice, stream_state=stream_state)
        for record in records:
            stream_state.clear()
            stream_state.update(stream_instance.get_updated_state(stream_state, record))
            yield record

        if hasattr(stream_instance, "state"):
            stream_state.clear()
            stream_state.update(stream_instance.state)


def read_full_refresh(stream_instance: Stream):
    slices = stream_instance.stream_slices(sync_mode=SyncMode.full_refresh)
    for _slice in slices:
        records = stream_instance.read_records(stream_slice=_slice, sync_mode=SyncMode.full_refresh)
        for record in records:
            yield record


def command_check(source: Source, config):
    logger = mock.MagicMock()
    connector_config, _ = split_config(config)
    connector_config = MigrateStartDate.modify_and_save("unit_tests/config.json", source, connector_config)
    if source.check_config_against_spec:
        source_spec: ConnectorSpecification = source.spec(logger)
        check_config_against_spec_or_exit(connector_config, source_spec)
    return source.check(logger, config)


def url_strip_query(url):
    parsed_result = urlparse(url)
    parsed_result = parsed_result._replace(query="")
    return urlunparse(parsed_result)
