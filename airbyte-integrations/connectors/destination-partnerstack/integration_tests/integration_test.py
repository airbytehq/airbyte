#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from logging import getLogger
from typing import Any, Dict, Mapping

import pytest
from airbyte_cdk.models import (
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStateMessage,
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    Status,
    SyncMode,
    Type,
)

from destination_partnerstack import DestinationPartnerstack
from destination_partnerstack.client import PartnerStackClient

logger = getLogger("airbyte")


@pytest.fixture(name="config")
def config_fixture() -> Mapping[str, Any]:
    with open("secrets/config.json", "r") as f:
        return json.loads(f.read())


@pytest.fixture(name="configured_catalog")
def configured_catalog_fixture() -> ConfiguredAirbyteCatalog:
    stream_schema = {
        "type": "object",
        "properties": {"customer_key": {"type": "str"}, "email": {"type": "str"}, "partner_key": {"type": "str"}},
    }

    append_stream = ConfiguredAirbyteStream(
        stream=AirbyteStream(name="append_stream", json_schema=stream_schema, supported_sync_modes=[SyncMode.full_refresh]),
        sync_mode=SyncMode.full_refresh,
        destination_sync_mode=DestinationSyncMode.append,
    )
    return ConfiguredAirbyteCatalog(streams=[append_stream])


def test_check_valid_config(config: Mapping):
    outcome = DestinationPartnerstack().check(logger, config)
    assert outcome.status == Status.SUCCEEDED


def test_check_invalid_config():
    outcome = DestinationPartnerstack().check(
        logger, {"public_key": "not_public_key", "private_key": "not_private_key", "endpoint": "transactions"}
    )
    assert outcome.status == Status.FAILED


def _state(data: Dict[str, Any]) -> AirbyteMessage:
    return AirbyteMessage(type=Type.STATE, state=AirbyteStateMessage(data=data))


def _record(stream: str, key_value: str, email_value: str, partner_value: str) -> AirbyteMessage:
    return AirbyteMessage(
        type=Type.RECORD,
        record=AirbyteRecordMessage(
            stream=stream, data={"customer_key": key_value, "email": email_value, "partner_key": partner_value}, emitted_at=0
        ),
    )


def test_write(config: Mapping, configured_catalog: ConfiguredAirbyteCatalog):
    stream_metric = configured_catalog.streams[0].stream.name
    state_message = _state({"state": "1"})
    record_chunk = [_record(stream_metric, str(i), str(i), str(i)) for i in range(3)]

    destination = DestinationPartnerstack()

    expected_states = [state_message]
    output_states = list(destination.write(config, configured_catalog, [*record_chunk, state_message]))

    assert expected_states == output_states, "Checkpoint state messages were expected from the destination"
