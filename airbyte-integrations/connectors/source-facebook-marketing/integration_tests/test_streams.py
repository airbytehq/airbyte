#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import copy
from typing import Any, List, MutableMapping, Set, Tuple

import pytest
from airbyte_cdk import AirbyteLogger
from airbyte_cdk.models import AirbyteMessage, ConfiguredAirbyteCatalog, Type
from source_facebook_marketing.source import SourceFacebookMarketing


@pytest.fixture(scope="session", name="state")
def state_fixture() -> MutableMapping[str, MutableMapping[str, Any]]:
    return {
        "ads": {"updated_time": "2021-02-19T10:42:40-0800"},
        "ad_sets": {"updated_time": "2021-02-19T10:42:40-0800"},
        "campaigns": {"updated_time": "2021-02-19T10:42:40-0800"},
    }


@pytest.fixture(scope="session", name="state_with_include_deleted")
def state_with_include_deleted_fixture(state):
    result_state = copy.deepcopy(state)
    for state in result_state.values():
        state["include_deleted"] = True

    return result_state


@pytest.fixture(scope="session", name="configured_catalog")
def configured_catalog_fixture():
    return ConfiguredAirbyteCatalog.parse_file("integration_tests/configured_catalog.json")


class TestFacebookMarketingSource:
    @pytest.mark.parametrize(
        "stream_name, deleted_id", [("ads", "23846756820320398"), ("campaigns", "23846541919710398"), ("ad_sets", "23846541706990398")]
    )
    def test_streams_with_include_deleted(self, stream_name, deleted_id, config_with_include_deleted, configured_catalog):
        catalog = self.slice_catalog(configured_catalog, {stream_name})
        records, states = self._read_records(config_with_include_deleted, catalog)
        deleted_records = list(filter(self._deleted_record, records))
        is_specific_deleted_pulled = deleted_id in list(map(self._object_id, records))

        assert states, "incremental read should produce states"
        for name, state in states[-1].state.data.items():
            assert "include_deleted" in state, f"State for {name} should include `include_deleted` flag"

        assert deleted_records, f"{stream_name} stream should have deleted records returned"
        assert is_specific_deleted_pulled, f"{stream_name} stream should have a deleted record with id={deleted_id}"

    @pytest.mark.parametrize("stream_name, deleted_num", [("ads", 2), ("campaigns", 3), ("ad_sets", 1)])
    def test_streams_with_include_deleted_and_state(self, stream_name, deleted_num, config_with_include_deleted, configured_catalog, state):
        """Should ignore state because of include_deleted enabled"""
        catalog = self.slice_catalog(configured_catalog, {stream_name})
        records, states = self._read_records(config_with_include_deleted, catalog, state=state)
        deleted_records = list(filter(self._deleted_record, records))

        assert len(deleted_records) == deleted_num, f"{stream_name} should have {deleted_num} deleted records returned"

    @pytest.mark.parametrize("stream_name, deleted_num", [("ads", 0), ("campaigns", 0), ("ad_sets", 0)])
    def test_streams_with_include_deleted_and_state_with_included_deleted(
        self, stream_name, deleted_num, config_with_include_deleted, configured_catalog, state_with_include_deleted
    ):
        """Should keep state because of include_deleted enabled previously"""
        catalog = self.slice_catalog(configured_catalog, {stream_name})
        records, states = self._read_records(config_with_include_deleted, catalog, state=state_with_include_deleted)
        deleted_records = list(filter(self._deleted_record, records))

        assert len(deleted_records) == deleted_num, f"{stream_name} should have {deleted_num} deleted records returned"

    @staticmethod
    def _deleted_record(record: AirbyteMessage) -> bool:
        return record.record.data["effective_status"] == "ARCHIVED"

    @staticmethod
    def _object_id(record: AirbyteMessage) -> str:
        return str(record.record.data["id"])

    @staticmethod
    def slice_catalog(catalog: ConfiguredAirbyteCatalog, streams: Set[str]) -> ConfiguredAirbyteCatalog:
        sliced_catalog = ConfiguredAirbyteCatalog(streams=[])
        for stream in catalog.streams:
            if stream.stream.name in streams:
                sliced_catalog.streams.append(stream)
        return sliced_catalog

    @staticmethod
    def _read_records(conf, catalog, state=None) -> Tuple[List[AirbyteMessage], List[AirbyteMessage]]:
        records = []
        states = []
        for message in SourceFacebookMarketing().read(AirbyteLogger(), conf, catalog, state=state):
            if message.type == Type.RECORD:
                records.append(message)
            elif message.type == Type.STATE:
                states.append(message)

        return records, states
