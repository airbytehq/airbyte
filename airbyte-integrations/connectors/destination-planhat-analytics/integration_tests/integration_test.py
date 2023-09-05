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


@pytest.fixture(name="config_metric")
def config_metric_fixture() -> Mapping[str, Any]:
    with open("secrets/config_metric.json", "r") as f:
        return json.load(f)


@pytest.fixture(name="config_activity")
def config_activity_fixture() -> Mapping[str, Any]:
    with open("secrets/config_activity.json", "r") as f:
        return json.load(f)


@pytest.fixture(name="configured_catalog")
def configured_catalog_fixture() -> ConfiguredAirbyteCatalog:
    stream_schema_metric = {
        "type": "object",
        "properties": {"dimensionId": {"type": "str"}, "value": {"type": "str"}, "externalId": {"type": "str"}},
    }
    stream_schema_activity = {
        "type": "object",
        "properties": {"euExtId": {"type": "str"}, "action": {"type": "str"}, "count": {"type": "int"}},
    }

    append_stream_metric = ConfiguredAirbyteStream(
        stream=AirbyteStream(name="append_stream_metric", json_schema=stream_schema_metric, supported_sync_modes=[SyncMode.full_refresh]),
        sync_mode=SyncMode.full_refresh,
        destination_sync_mode=DestinationSyncMode.append,
    )
    append_stream_activity = ConfiguredAirbyteStream(
        stream=AirbyteStream(
            name="append_stream_activity", json_schema=stream_schema_activity, supported_sync_modes=[SyncMode.full_refresh]
        ),
        sync_mode=SyncMode.full_refresh,
        destination_sync_mode=DestinationSyncMode.append,
    )
    return ConfiguredAirbyteCatalog(streams=[append_stream_metric, append_stream_activity])


def test_check_valid_config_metric(config_metric: Mapping):
    outcome = DestinationPlanhatAnalytics().check(logger, config_metric)
    assert outcome.status == Status.SUCCEEDED


def test_check_valid_config_activity(config_activity: Mapping):
    outcome = DestinationPlanhatAnalytics().check(logger, config_activity)
    assert outcome.status == Status.SUCCEEDED


def test_check_invalid_config():
    f = open("integration_tests/invalid_config.json")
    invalid_config = json.load(f)
    outcome = DestinationPlanhatAnalytics().check(logger, invalid_config)
    assert outcome.status == Status.FAILED


def _state(data: Dict[str, Any]) -> AirbyteMessage:
    return AirbyteMessage(type=Type.STATE, state=AirbyteStateMessage(data=data))


def _record_metric(stream: str, dimensionId_value: str, value: str, externalId_value: str) -> AirbyteMessage:
    return AirbyteMessage(
        type=Type.RECORD,
        record=AirbyteRecordMessage(
            stream=stream, data={"dimensionId": dimensionId_value, "value": value, "externalId": externalId_value}, emitted_at=0
        ),
    )


def _record_activity(stream: str, id: str, action: str, count: str) -> AirbyteMessage:
    return AirbyteMessage(
        type=Type.RECORD, record=AirbyteRecordMessage(stream=stream, data={"euExtId": id, "action": action, "count": count}, emitted_at=0)
    )


def test_write_metric(config_metric: Mapping, configured_catalog: ConfiguredAirbyteCatalog):
    stream_metric = configured_catalog.streams[0].stream.name
    state_message = _state({"state": "1"})
    record_chunk = [_record_metric(stream_metric, str(i), str(i), str(i)) for i in range(5)]

    destination = DestinationPlanhatAnalytics()

    expected_states = [state_message]
    output_states = list(destination.write(config_metric, configured_catalog, [*record_chunk, state_message]))

    assert expected_states == output_states, "Checkpoint state messages were expected from the destination"


def test_write_activity(config_activity: Mapping, configured_catalog: ConfiguredAirbyteCatalog):
    stream_activity = configured_catalog.streams[1].stream.name
    state_message = _state({"state": "1"})
    record_chunk = [_record_activity(stream_activity, str(i), str(i), i) for i in range(5)]

    destination = DestinationPlanhatAnalytics()

    expected_states = [state_message]
    output_states = list(destination.write(config_activity, configured_catalog, [*record_chunk, state_message]))

    assert expected_states == output_states, "Checkpoint state messages were expected from the destination"
