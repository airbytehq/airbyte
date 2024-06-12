#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import urllib.parse
from typing import Any, List, MutableMapping
from unittest import mock

from airbyte_cdk.models import SyncMode
from airbyte_cdk.models.airbyte_protocol import ConnectorSpecification
from airbyte_cdk.sources import Source
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.utils.schema_helpers import check_config_against_spec_or_exit, split_config


def setup_response(status, body):
    return [{"json": body, "status_code": status}]


def get_url_to_mock(stream):
    return urllib.parse.urljoin(stream.url_base, stream.path())


def command_check(source: Source, config):
    logger = mock.MagicMock()
    connector_config, _ = split_config(config)
    if source.check_config_against_spec:
        source_spec: ConnectorSpecification = source.spec(logger)
        check_config_against_spec_or_exit(connector_config, source_spec)
    return source.check(logger, config)


def read_incremental(stream_instance: Stream, stream_state: MutableMapping[str, Any], cursor_field: List[str] = None):
    res = []
    stream_instance.state = stream_state
    slices = stream_instance.stream_slices(sync_mode=SyncMode.incremental, cursor_field=cursor_field, stream_state=stream_state)
    for slice in slices:
        records = stream_instance.read_records(sync_mode=SyncMode.incremental,  cursor_field=cursor_field, stream_slice=slice, stream_state=stream_state)
        for record in records:
            stream_state = stream_instance.get_updated_state(stream_state, record)
            res.append(record)
    return res
