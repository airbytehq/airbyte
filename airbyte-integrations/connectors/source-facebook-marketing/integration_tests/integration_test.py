"""
MIT License

Copyright (c) 2020 Airbyte

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import copy
import json
from typing import List, Set, Tuple

import pytest
from airbyte_protocol import AirbyteMessage, ConfiguredAirbyteCatalog, SyncMode, Type
from base_python import AirbyteLogger
from source_facebook_marketing.source import SourceFacebookMarketing


@pytest.fixture(scope="session", name="stream_config")
def config_fixture():
    with open("secrets/config.json", "r") as config_file:
        return json.load(config_file)


@pytest.fixture(scope="session", name="stream_config_with_include_deleted")
def config_with_include_deleted_fixture(stream_config):
    patched_config = copy.deepcopy(stream_config)
    patched_config["include_deleted"] = True
    return patched_config


@pytest.fixture(scope="session", name="state")
def state_fixture():
    return {
        "ads": {"updated_time": "2021-02-19T10:42:40-0800"},
        "adsets": {"updated_time": "2021-02-19T10:42:40-0800"},
        "campaigns": {"updated_time": "2021-02-19T10:42:40-0800"},
    }


@pytest.fixture(scope="session", name="state_with_include_deleted")
def state_with_include_deleted_fixture(state):
    result_state = copy.deepcopy(state)
    result_state["ads"]["include_deleted"] = True
    result_state["adsets"]["include_deleted"] = True
    result_state["campaigns"]["include_deleted"] = True

    return result_state


@pytest.fixture(scope="session", name="configured_catalog")
def configured_catalog_fixture():
    return ConfiguredAirbyteCatalog.parse_file("sample_files/configured_catalog.json")


class TestFacebookMarketingSource:
    @pytest.mark.parametrize(
        "catalog_path", ["sample_files/configured_catalog_adsinsights.json", "sample_files/configured_catalog_adcreatives.json"]
    )
    def test_streams_outputs_records(self, catalog_path, stream_config):
        configured_catalog = ConfiguredAirbyteCatalog.parse_file(catalog_path)
        records, states = self._read_records(stream_config, configured_catalog)

        assert records, "should have some records returned"
        if configured_catalog.streams[0].sync_mode == SyncMode.incremental:
            assert states, "should have some states returned"

    @pytest.mark.parametrize("stream_name, deleted_num", [("ads", 2), ("campaigns", 3), ("adsets", 1)])
    def test_streams_with_include_deleted(self, stream_name, deleted_num, stream_config_with_include_deleted, configured_catalog):
        catalog = self.slice_catalog(configured_catalog, {stream_name})
        records, states = self._read_records(stream_config_with_include_deleted, catalog)
        deleted_records = list(filter(self._deleted_record, records))

        assert states
        for name, state in states[0].state.data.items():
            assert "include_deleted" in state, f"State for {name} should include `include_deleted` flag"

        assert len(deleted_records) == deleted_num, f"{stream_name} should have {deleted_num} deleted records returned"

    @pytest.mark.parametrize("stream_name, deleted_num", [("ads", 2), ("campaigns", 3), ("adsets", 1)])
    def test_streams_with_include_deleted_and_state(
        self, stream_name, deleted_num, stream_config_with_include_deleted, configured_catalog, state
    ):
        """Should ignore state because of include_deleted enabled"""
        catalog = self.slice_catalog(configured_catalog, {stream_name})
        records, states = self._read_records(stream_config_with_include_deleted, catalog, state=state)
        deleted_records = list(filter(self._deleted_record, records))

        assert len(deleted_records) == deleted_num, f"{stream_name} should have {deleted_num} deleted records returned"

    @pytest.mark.parametrize("stream_name, deleted_num", [("ads", 0), ("campaigns", 0), ("adsets", 0)])
    def test_streams_with_include_deleted_and_state_with_included_deleted(
        self, stream_name, deleted_num, stream_config_with_include_deleted, configured_catalog, state_with_include_deleted
    ):
        """Should keep state because of include_deleted enabled previously"""
        catalog = self.slice_catalog(configured_catalog, {stream_name})
        records, states = self._read_records(stream_config_with_include_deleted, catalog, state=state_with_include_deleted)
        deleted_records = list(filter(self._deleted_record, records))

        assert len(deleted_records) == deleted_num, f"{stream_name} should have {deleted_num} deleted records returned"

    @staticmethod
    def _deleted_record(record: AirbyteMessage) -> bool:
        return record.record.data["effective_status"] == "ARCHIVED"

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
