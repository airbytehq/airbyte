#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import copy
import logging
import tempfile
from typing import Any, List, MutableMapping, Set, Tuple

import pytest
from airbyte_cdk.models import AirbyteMessage, ConfiguredAirbyteCatalog, ConfiguredAirbyteStream, DestinationSyncMode, SyncMode, Type
from source_facebook_marketing.source import SourceFacebookMarketing


@pytest.fixture(scope="session", name="state")
def state_fixture() -> MutableMapping[str, MutableMapping[str, Any]]:
    cursor_value = "2021-02-19T10:42:40-0800"
    return {
        "ads": {"updated_time": cursor_value},
        "ad_sets": {"updated_time": cursor_value},
        "campaigns": {"updated_time": cursor_value},
    }


@pytest.fixture(scope="session", name="configured_catalog")
def configured_catalog_fixture(config) -> ConfiguredAirbyteCatalog:
    with tempfile.TemporaryDirectory() as temp_dir:
        source = SourceFacebookMarketing()
        config = source.configure(config, temp_dir)
        catalog = source.discover(logger=logging.getLogger("airbyte"), config=config)
        streams = []
        # Prefer incremental if available
        for stream in catalog.streams:
            sync_mode = SyncMode.incremental if SyncMode.incremental in stream.supported_sync_modes else SyncMode.full_refresh
            streams.append(ConfiguredAirbyteStream(stream=stream, sync_mode=sync_mode, destination_sync_mode=DestinationSyncMode.append))

        return ConfiguredAirbyteCatalog(streams=streams)


class TestFacebookMarketingSource:
    @pytest.mark.parametrize(
        "stream_name, deleted_id", [("ads", "23846756820320398"), ("campaigns", "23846541919710398"), ("ad_sets", "23846541706990398")]
    )
    def test_streams_with_include_deleted(self, stream_name, deleted_id, config_with_include_deleted, configured_catalog):
        catalog = self._slice_catalog(configured_catalog, {stream_name})
        records, states = self._read_records(config_with_include_deleted, catalog)
        deleted_records = list(filter(self._deleted_record, records))
        is_specific_deleted_pulled = deleted_id in list(map(self._object_id, records))

        assert states, "incremental read should produce states"
        for name, state in states[-1].state.data.items():
            assert "include_deleted" in state, f"State for {name} should include `include_deleted` flag"

        assert deleted_records, f"{stream_name} stream should have deleted records returned"
        assert is_specific_deleted_pulled, f"{stream_name} stream should have a deleted record with id={deleted_id}"

    @pytest.mark.parametrize(
        "stream_name, deleted_num, include_deleted_in_state",
        [
            ("ads", 2, False),
            ("campaigns", 3, False),
            ("ad_sets", 1, False),
            ("ads", 0, True),
            ("campaigns", 0, True),
            ("ad_sets", 0, True),
        ],
    )
    def test_streams_with_include_deleted_and_state(
        self, stream_name, deleted_num, include_deleted_in_state, config_with_include_deleted, configured_catalog, state
    ):
        """Should ignore state because of include_deleted enabled"""
        if include_deleted_in_state:
            state = copy.deepcopy(state)
            for value in state.values():
                value["include_deleted"] = True

        catalog = self._slice_catalog(configured_catalog, {stream_name})
        records, states = self._read_records(config_with_include_deleted, catalog, state=state)
        deleted_records = list(filter(self._deleted_record, records))

        assert len(deleted_records) == deleted_num, f"{stream_name} should have {deleted_num} deleted records returned"

    @staticmethod
    def _deleted_record(record: AirbyteMessage) -> bool:
        return record.record.data["effective_status"] == "ARCHIVED"

    @staticmethod
    def _object_id(record: AirbyteMessage) -> str:
        return str(record.record.data["id"])

    @staticmethod
    def _slice_catalog(catalog: ConfiguredAirbyteCatalog, streams: Set[str]) -> ConfiguredAirbyteCatalog:
        sliced_catalog = ConfiguredAirbyteCatalog(streams=[])
        for stream in catalog.streams:
            if stream.stream.name in streams:
                sliced_catalog.streams.append(stream)
        return sliced_catalog

    @staticmethod
    def _read_records(conf, catalog, state=None) -> Tuple[List[AirbyteMessage], List[AirbyteMessage]]:
        records = []
        states = []
        for message in SourceFacebookMarketing().read(logging.getLogger("airbyte"), conf, catalog, state=state):
            if message.type == Type.RECORD:
                records.append(message)
            elif message.type == Type.STATE:
                states.append(message)

        return records, states
