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

from destination_planhat import DestinationPlanhat

logger = getLogger("airbyte")

@pytest.fixture(name="config")
def config_fixture() -> Mapping[str, Any]:
    with open("secrets/config.json", "r") as f:
        return json.loads(f.read())
    
@pytest.fixture(name="configured_catalog")
def configured_catalog_fixture() -> ConfiguredAirbyteCatalog:
    stream_schema = {
        "type": "object",
        "properties": {"email": {"type": "str"}, "companyId": {"type": "str"}, "firstName": {"type": "str"}},
    }
    append_stream = ConfiguredAirbyteStream(
        stream=AirbyteStream(name="stream_endusers", json_schema=stream_schema, supported_sync_modes=[SyncMode.incremental]),
        sync_mode=SyncMode.full_refresh,
        destination_sync_mode=DestinationSyncMode.append,
    )
    return ConfiguredAirbyteCatalog(streams=[append_stream])

def test_check_valid_config(config: Mapping):
    outcome = DestinationPlanhat().check(logger, config)
    assert outcome.status == Status.SUCCEEDED


def test_check_invalid_config():
    outcome = DestinationPlanhat().check(
        logger, 
        {
            "api_token": "XXXX",
            "pobject": {"endpoint": "endusers"}}
    )
    assert outcome.status == Status.FAILED

def _state(data: Dict[str, Any]) -> AirbyteMessage:
    return AirbyteMessage(type=Type.STATE, state=AirbyteStateMessage(data=data))


def _record(stream: str, email_value: str, company_value: str, name_value: str) -> AirbyteMessage:
    return AirbyteMessage(
        type=Type.RECORD,
        record=AirbyteRecordMessage(
            stream=stream, data={"email": email_value, "companyId": company_value, "firstName": name_value}, emitted_at=0
        )
    )


def test_write(config: Mapping, configured_catalog: ConfiguredAirbyteCatalog):
    stream_metric = configured_catalog.streams[0].stream.name
    state_message = _state({"state": "1"})
    record_chunk = [_record(stream_metric, str(i), str(i), str(i)) for i in range(2)]

    destination = DestinationPlanhat()

    expected_states = [state_message]
    output_states = list(destination.write(config, configured_catalog, [*record_chunk, state_message]))

    assert expected_states == output_states, "Checkpoint state messages were expected from the destination"
