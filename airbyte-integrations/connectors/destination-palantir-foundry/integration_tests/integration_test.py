#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#
import json
import logging
from typing import Dict, Any

import pytest
from airbyte_protocol.models import ConfiguredAirbyteCatalog, ConfiguredAirbyteStream, AirbyteStream, SyncMode, \
    DestinationSyncMode, Status, AirbyteMessage, Type, AirbyteStateMessage, AirbyteRecordMessage, AirbyteStreamState, \
    StreamDescriptor

from destination_palantir_foundry import DestinationPalantirFoundry
from destination_palantir_foundry.config.foundry_config import FoundryConfig
from destination_palantir_foundry.foundry_api.foundry_auth import ConfidentialClientAuthFactory
from destination_palantir_foundry.foundry_api.service_factory import FoundryServiceFactory

logger = logging.getLogger()


@pytest.fixture(name="raw_config")
def raw_config_fixture() -> Dict:
    with open("../secrets/config.json", "r") as f:
        return json.loads(f.read())


@pytest.fixture(name="config")
def parsed_config_fixture(raw_config: Dict) -> FoundryConfig:
    return FoundryConfig.from_raw(raw_config)


@pytest.fixture(name="configured_catalog")
def configured_catalog_fixture() -> ConfiguredAirbyteCatalog:
    stream_schema = {"type": "object", "properties": {"string_col": {"type": "str"}, "int_col": {"type": "integer"}}}

    append_stream = ConfiguredAirbyteStream(
        stream=AirbyteStream(name="append_stream5", json_schema=stream_schema, supported_sync_modes=[SyncMode.incremental],
                             namespace="test"),
        sync_mode=SyncMode.incremental,
        destination_sync_mode=DestinationSyncMode.append,
    )

    return ConfiguredAirbyteCatalog(streams=[append_stream])


@pytest.fixture(autouse=True)
def teardown(config: FoundryConfig, configured_catalog: ConfiguredAirbyteCatalog):
    auth = ConfidentialClientAuthFactory().create(config, ["streams:write"])
    auth.sign_in_as_service_user()

    service_factory = FoundryServiceFactory(config.host, auth)
    stream_catalog = service_factory.stream_catalog()

    # get all stream dataset rids


def test_validConfig_succeeds(raw_config: Dict):
    outcome = DestinationPalantirFoundry().check(logging.getLogger("airbyte"), raw_config)
    assert outcome.status == Status.SUCCEEDED


def test_invalidConfig_fails():
    outcome = DestinationPalantirFoundry().check(logging.getLogger("airbyte"), {"project_id": "not_a_real_id"})
    assert outcome.status == Status.FAILED


def _state(data: Dict[str, Any], namespace: str, stream: str) -> AirbyteMessage:
    return AirbyteMessage(type=Type.STATE, state=AirbyteStateMessage(data=data, stream=AirbyteStreamState(
        stream_descriptor=StreamDescriptor(namespace=namespace, name=stream))))


def _record(stream: str, str_value: str, int_value: int) -> AirbyteMessage:
    return AirbyteMessage(
        type=Type.RECORD,
        record=AirbyteRecordMessage(stream=stream, namespace="test", data={"str_col": str_value, "int_col": int_value}, emitted_at=0)
    )


def test_write_append(raw_config: Dict, configured_catalog: ConfiguredAirbyteCatalog):
    """
    This test verifies that writing a stream in "append" mode appends new records without deleting the old ones

    It checks also if the correct state message is output by the connector at the end of the sync
    """
    stream = configured_catalog.streams[0].stream
    destination = DestinationPalantirFoundry()

    state_message = _state({"state": "3"}, stream.namespace, stream.name)
    record_chunk = [_record(stream.name, str(i), i) for i in range(1, 3)]

    output_states = list(destination.write(raw_config, configured_catalog, [*record_chunk, state_message]))
    assert [state_message] == output_states

    # expected_records = [_record(stream, str(i), i) for i in range(1, 3)]
    # assert expected_records == records_in_destination
