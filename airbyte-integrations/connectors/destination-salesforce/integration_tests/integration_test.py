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

from destination_salesforce.client import SalesforceClient
from destination_salesforce import DestinationSalesforce

logger = getLogger("airbyte")


@pytest.fixture(name="config")
def config_fixture() -> Mapping[str, Any]:
    with open("secrets/config.json", "r") as f:
        return json.loads(f.read())


@pytest.fixture(name="configured_catalog")
def configured_catalog_fixture() -> ConfiguredAirbyteCatalog:
    stream_schema = {
        "type": "object",
        "properties": {"Id": {"type": "str"}, "Name": {"type": "str"}, "phone_number_4__c": {"type": "str"}},
    }

    append_stream = ConfiguredAirbyteStream(
        stream=AirbyteStream(name="append_stream", json_schema=stream_schema, supported_sync_modes=[SyncMode.full_refresh]),
        sync_mode=SyncMode.full_refresh,
        destination_sync_mode=DestinationSyncMode.append,
    )
    return ConfiguredAirbyteCatalog(streams=[append_stream])


def test_check_valid_config(config: Mapping):
    outcome = DestinationSalesforce().check(logger, config)
    assert outcome.status == Status.SUCCEEDED


def test_check_invalid_config():
    outcome = DestinationSalesforce().check(
        logger, {"client_id": "AAA", "client_secret": "XXX", "refresh_token": "xxx", "sobject": "Account"}
    )
    assert outcome.status == Status.FAILED

def _state(data: Dict[str, Any]) -> AirbyteMessage:
    return AirbyteMessage(type=Type.STATE, state=AirbyteStateMessage(data=data))


def _record(stream: str, id: str, name: str, phone: str) -> AirbyteMessage:
    return AirbyteMessage(
        type=Type.RECORD,
        record=AirbyteRecordMessage(
            stream=stream, data={"Id": id, "Name": name, "phone_number_4__c": phone}, emitted_at=0
        ),
    )

def test_write(config: Mapping, configured_catalog: ConfiguredAirbyteCatalog):
    stream_metric = configured_catalog.streams[0].stream.name
    state_message = _state({"state": "1"})
    record_chunk = [_record(stream_metric, None, 'test', '0101010101')]

    destination = DestinationSalesforce()

    expected_states = [state_message]
    output_states = list(destination.write(config, configured_catalog, [*record_chunk, state_message]))

    assert expected_states == output_states, "Checkpoint state messages were expected from the destination"