#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import json
from typing import Any, Dict, Mapping
from logging import getLogger

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
from destination_planhat_analytics.client import PlanHatClient
from destination_planhat_analytics import DestinationPlanhatAnalytics

logger = getLogger("airbyte")


@pytest.fixture(name="config")
def config_fixture() -> Mapping[str, Any]:
    with open("secrets/config.json", "r") as f:
        return json.load(f)
    
@pytest.fixture(name="client")
def client_fixture(config) -> PlanHatClient:
    return PlanHatClient(**config)
    
@pytest.fixture(name="configured_catalog")
def configured_catalog_fixture() -> ConfiguredAirbyteCatalog:
    stream_schema = {"type": "object", "properties": {"dimensionId": {"type": "str"}, "value": {"type": "str"}, "externalId": {"type": "str"}}}

    append_stream = ConfiguredAirbyteStream(
        stream=AirbyteStream(name="stream_metrics", json_schema=stream_schema, supported_sync_modes=[SyncMode.incremental]),
        sync_mode=SyncMode.incremental,
        destination_sync_mode=DestinationSyncMode.append,
    )
    return ConfiguredAirbyteCatalog(streams=[append_stream])

def test_check_valid_config(config: Mapping):
    print(type(config))
    outcome = DestinationPlanhatAnalytics().check(logger, config)
    assert outcome.status == Status.SUCCEEDED

def _state(data: Dict[str, Any]) -> AirbyteMessage:
    return AirbyteMessage(type=Type.STATE, state=AirbyteStateMessage(data=data))

def _record(stream: str, dimensionId_value: str, value: str, externalId_value: str) -> AirbyteMessage:
    return AirbyteMessage(
        type=Type.RECORD, record=AirbyteRecordMessage(stream=stream, data={"dimensionId": dimensionId_value, "value": value, "externalId": externalId_value}, emitted_at=0)
    )

def test_write(config: Mapping, configured_catalog: ConfiguredAirbyteCatalog, client: PlanHatClient):
    stream_metrics = configured_catalog.streams[0].stream.name
    state_message = _state({"state": "1"})
    record_chunk = [_record(stream_metrics, str(i), str(i), str(i)) for i in range(5)]

    destination = DestinationPlanhatAnalytics()

    expected_states = [state_message]
    output_states = list(
        destination.write(
            config, configured_catalog, [*record_chunk, state_message]
        )
    )
    assert expected_states == output_states, "Checkpoint state messages were expected from the destination"

