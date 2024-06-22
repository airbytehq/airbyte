#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import logging
from typing import Any, Mapping

import pytest
from airbyte_cdk.models import AirbyteStream, ConfiguredAirbyteCatalog, ConfiguredAirbyteStream, DestinationSyncMode, Status, SyncMode
from destination_amazon_sqs import DestinationAmazonSqs


@pytest.fixture(name="config")
def config_fixture() -> Mapping[str, Any]:
    with open("secrets/config.json", "r") as f:
        return json.loads(f.read())


@pytest.fixture(name="configured_catalog")
def configured_catalog_fixture() -> ConfiguredAirbyteCatalog:
    stream_schema = {"type": "object", "properties": {"string_col": {"type": "str"}, "int_col": {"type": "integer"}}}

    append_stream = ConfiguredAirbyteStream(
        stream=AirbyteStream(name="append_stream", json_schema=stream_schema, supported_sync_modes=[SyncMode.incremental]),
        sync_mode=SyncMode.incremental,
        destination_sync_mode=DestinationSyncMode.append,
    )

    overwrite_stream = ConfiguredAirbyteStream(
        stream=AirbyteStream(name="overwrite_stream", json_schema=stream_schema, supported_sync_modes=[SyncMode.incremental]),
        sync_mode=SyncMode.incremental,
        destination_sync_mode=DestinationSyncMode.overwrite,
    )

    return ConfiguredAirbyteCatalog(streams=[append_stream, overwrite_stream])


def test_check_valid_config(config: Mapping):
    outcome = DestinationAmazonSqs().check(logging.getLogger("airbyte"), config)
    assert outcome.status == Status.SUCCEEDED


def test_check_invalid_config():
    outcome = DestinationAmazonSqs().check(logging.getLogger("airbyte"), {"secret_key": "not_a_real_secret"})
    assert outcome.status == Status.FAILED
