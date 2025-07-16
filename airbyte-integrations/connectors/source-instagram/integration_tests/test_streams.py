#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from datetime import timedelta
from typing import Any, List, MutableMapping, Tuple

import pytest

from airbyte_cdk.models import (
    AirbyteMessage,
    AirbyteStateBlob,
    AirbyteStateMessage,
    AirbyteStateType,
    AirbyteStreamState,
    StreamDescriptor,
    Type,
)
from airbyte_cdk.test.catalog_builder import CatalogBuilder, ConfiguredAirbyteStreamBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.utils.datetime_helpers import ab_datetime_now

from .conftest import get_source


@pytest.fixture(name="state")
def state_fixture() -> MutableMapping[str, Any]:
    initial_state = {
        "17841408147298757": {"date": (ab_datetime_now() - timedelta(days=10)).strftime("%Y-%m-%dT%H:%M:%S+00:00")},
        "17841403112736866": {"date": (ab_datetime_now() - timedelta(days=5)).strftime("%Y-%m-%dT%H:%M:%S+00:00")},
    }
    return [
        AirbyteStateMessage(
            type=AirbyteStateType.STREAM,
            stream=AirbyteStreamState(
                stream_descriptor=StreamDescriptor(name="user_insights", namespace=None),
                stream_state=AirbyteStateBlob(initial_state),
            ),
        )
    ]


class TestInstagramSource:
    """Custom integration tests should test incremental with nested state"""

    def test_incremental_streams(self, config, state):
        records, states = self._read_records(config, "user_insights")
        assert len(records) == 30, "UserInsights for two accounts over last 30 day should return 30 records when empty STATE provided"

        records, states = self._read_records(config, "user_insights", state)
        assert len(records) <= 60 - 10 - 5, "UserInsights should have less records returned when non empty STATE provided"

        assert states, "insights should produce states"
        for state_msg in states:
            stream_name, stream_state, state_keys_count = (
                state_msg.state.stream.stream_descriptor.name,
                state_msg.state.stream.stream_state,
                len(state_msg.state.stream.stream_state.__dict__.get("states", {})),
            )

            assert stream_name == "user_insights", f"each state message should reference 'user_insights' stream, got {stream_name} instead"
            assert isinstance(
                stream_state, AirbyteStateBlob
            ), f"Stream state should be type AirbyteStateBlob, got {type(stream_state)} instead"
            assert state_keys_count == 2, f"Stream state should contain 2 partition keys, got {state_keys_count} instead"

    @staticmethod
    def _read_records(conf, stream_name, state=None) -> Tuple[List[AirbyteMessage], List[AirbyteMessage]]:
        records = []
        states = []
        output = read(
            get_source(config=conf, state=state),
            conf,
            CatalogBuilder().with_stream(ConfiguredAirbyteStreamBuilder().with_name(stream_name)).build(),
            state=state,
        )
        for message in output.records_and_state_messages:
            if message.type == Type.RECORD:
                records.append(message)
            elif message.type == Type.STATE:
                print(message.state.stream.stream_state.__dict__)
                states.append(message)

        return records, states
