#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from typing import Any, Callable, List, MutableMapping, Tuple

import pendulum
import pytest
from airbyte_cdk.models import AirbyteMessage, AirbyteStateBlob, ConfiguredAirbyteCatalog, Type
from source_instagram.source import SourceInstagram


@pytest.fixture(name="state")
def state_fixture() -> MutableMapping[str, Any]:
    today = pendulum.today()
    return {
        "user_insights": {
            "17841408147298757": {"date": (today - pendulum.duration(days=10)).to_datetime_string()},
            "17841403112736866": {"date": (today - pendulum.duration(days=5)).to_datetime_string()},
        }
    }


class TestInstagramSource:
    """Custom integration tests should test incremental with nested state"""

    def test_incremental_streams(self, configured_catalog, config, state):
        catalog = self.slice_catalog(configured_catalog, lambda name: name == "user_insights")
        records, states = self._read_records(config, catalog)
        assert len(records) == 30, "UserInsights for two accounts over last 30 day should return 30 records when empty STATE provided"

        records, states = self._read_records(config, catalog, state)
        assert len(records) <= 60 - 10 - 5, "UserInsights should have less records returned when non empty STATE provided"

        assert states, "insights should produce states"
        for state_msg in states:
            stream_name, stream_state, state_keys_count = (state_msg.state.stream.stream_descriptor.name, 
                                                    state_msg.state.stream.stream_state, 
                                                    len(state_msg.state.stream.stream_state.dict()))

            assert stream_name == "user_insights", f"each state message should reference 'user_insights' stream, got {stream_name} instead"
            assert isinstance(stream_state, AirbyteStateBlob), f"Stream state should be type AirbyteStateBlob, got {type(stream_state)} instead"
            assert state_keys_count == 2, f"Stream state should contain 2 partition keys, got {state_keys_count} instead"

    @staticmethod
    def slice_catalog(catalog: ConfiguredAirbyteCatalog, predicate: Callable[[str], bool]) -> ConfiguredAirbyteCatalog:
        sliced_catalog = ConfiguredAirbyteCatalog(streams=[])
        for stream in catalog.streams:
            if predicate(stream.stream.name):
                sliced_catalog.streams.append(stream)
        return sliced_catalog

    @staticmethod
    def _read_records(conf, catalog, state=None) -> Tuple[List[AirbyteMessage], List[AirbyteMessage]]:
        records = []
        states = []
        for message in SourceInstagram().read(logging.getLogger("airbyte"), conf, catalog, state=state):
            if message.type == Type.RECORD:
                records.append(message)
            elif message.type == Type.STATE:
                states.append(message)

        return records, states
