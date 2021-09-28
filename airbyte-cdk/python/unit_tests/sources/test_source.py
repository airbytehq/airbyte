#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import json
import tempfile
from typing import Any, Mapping, MutableMapping
from unittest.mock import MagicMock

import pytest
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import ConfiguredAirbyteCatalog, SyncMode, Type
from airbyte_cdk.sources import AbstractSource, Source
from airbyte_cdk.sources.streams.core import Stream
from airbyte_cdk.sources.streams.http.http import HttpStream
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer


class MockSource(Source):
    def read(
        self, logger: AirbyteLogger, config: Mapping[str, Any], catalog: ConfiguredAirbyteCatalog, state: MutableMapping[str, Any] = None
    ):
        pass

    def check(self, logger: AirbyteLogger, config: Mapping[str, Any]):
        pass

    def discover(self, logger: AirbyteLogger, config: Mapping[str, Any]):
        pass


@pytest.fixture
def source():
    return MockSource()


@pytest.fixture
def catalog():
    configured_catalog = {
        "streams": [
            {
                "stream": {"name": "mock_http_stream", "json_schema": {}},
                "destination_sync_mode": "overwrite",
                "sync_mode": "full_refresh",
            },
            {
                "stream": {"name": "mock_stream", "json_schema": {}},
                "destination_sync_mode": "overwrite",
                "sync_mode": "full_refresh",
            },
        ]
    }
    return ConfiguredAirbyteCatalog.parse_obj(configured_catalog)


@pytest.fixture
def abstract_source(mocker):
    mocker.patch.multiple(HttpStream, __abstractmethods__=set())
    mocker.patch.multiple(Stream, __abstractmethods__=set())

    class MockHttpStream(MagicMock, HttpStream):
        url_base = "http://example.com"
        path = "/dummy/path"
        get_json_schema = MagicMock()

        def supports_incremental(self):
            return True

        def __init__(self, *args, **kvargs):
            MagicMock.__init__(self)
            HttpStream.__init__(self, *args, kvargs)
            self.read_records = MagicMock()

    class MockStream(MagicMock, Stream):
        page_size = None
        get_json_schema = MagicMock()

        def __init__(self, *args, **kvargs):
            MagicMock.__init__(self)
            self.read_records = MagicMock()

    streams = [MockHttpStream(), MockStream()]

    class MockAbstractSource(AbstractSource):
        def check_connection(self):
            return True, None

        def streams(self, config):
            self.streams_config = config
            return streams

    return MockAbstractSource()


def test_read_state(source):
    state = {"updated_at": "yesterday"}

    with tempfile.NamedTemporaryFile("w") as state_file:
        state_file.write(json.dumps(state))
        state_file.flush()
        actual = source.read_state(state_file.name)
        assert state == actual


def test_read_state_nonexistent(source):
    assert {} == source.read_state("")


def test_read_catalog(source):
    configured_catalog = {
        "streams": [
            {
                "stream": {"name": "mystream", "json_schema": {"type": "object", "properties": {"k": "v"}}},
                "destination_sync_mode": "overwrite",
                "sync_mode": "full_refresh",
            }
        ]
    }
    expected = ConfiguredAirbyteCatalog.parse_obj(configured_catalog)
    with tempfile.NamedTemporaryFile("w") as catalog_file:
        catalog_file.write(expected.json(exclude_unset=True))
        catalog_file.flush()
        actual = source.read_catalog(catalog_file.name)
        assert actual == expected


def test_internal_config(abstract_source, catalog):
    streams = abstract_source.streams(None)
    assert len(streams) == 2
    http_stream, non_http_stream = streams
    assert isinstance(http_stream, HttpStream)
    assert not isinstance(non_http_stream, HttpStream)
    http_stream.read_records.return_value = [{}] * 3
    non_http_stream.read_records.return_value = [{}] * 3

    # Test with empty config
    records = [r for r in abstract_source.read(logger=MagicMock(), config={}, catalog=catalog, state={})]
    # 3 for http stream and 3 for non http stream
    assert len(records) == 3 + 3
    assert http_stream.read_records.called
    assert non_http_stream.read_records.called
    # Make sure page_size havent been set
    assert not http_stream.page_size
    assert not non_http_stream.page_size
    # Test with records limit set to 1
    internal_config = {"some_config": 100, "_limit": 1}
    records = [r for r in abstract_source.read(logger=MagicMock(), config=internal_config, catalog=catalog, state={})]
    # 1 from http stream + 1 from non http stream
    assert len(records) == 1 + 1
    assert "_limit" not in abstract_source.streams_config
    assert "some_config" in abstract_source.streams_config
    # Test with records limit set to number that exceeds expceted records
    internal_config = {"some_config": 100, "_limit": 20}
    records = [r for r in abstract_source.read(logger=MagicMock(), config=internal_config, catalog=catalog, state={})]
    assert len(records) == 3 + 3

    # Check if page_size paramter is set to http instance only
    internal_config = {"some_config": 100, "_page_size": 2}
    records = [r for r in abstract_source.read(logger=MagicMock(), config=internal_config, catalog=catalog, state={})]
    assert "_page_size" not in abstract_source.streams_config
    assert "some_config" in abstract_source.streams_config
    assert len(records) == 3 + 3
    assert http_stream.page_size == 2
    # Make sure page_size havent been set for non http streams
    assert not non_http_stream.page_size


def test_internal_config_limit(abstract_source, catalog):
    logger_mock = MagicMock()
    del catalog.streams[1]
    STREAM_LIMIT = 2
    FULL_RECORDS_NUMBER = 3
    streams = abstract_source.streams(None)
    http_stream = streams[0]
    http_stream.read_records.return_value = [{}] * FULL_RECORDS_NUMBER
    internal_config = {"some_config": 100, "_limit": STREAM_LIMIT}

    catalog.streams[0].sync_mode = SyncMode.full_refresh
    records = [r for r in abstract_source.read(logger=logger_mock, config=internal_config, catalog=catalog, state={})]
    assert len(records) == STREAM_LIMIT
    logger_info_args = [call[0][0] for call in logger_mock.info.call_args_list]
    # Check if log line matches number of limit
    read_log_record = [_l for _l in logger_info_args if _l.startswith("Read")]
    assert read_log_record[0].startswith(f"Read {STREAM_LIMIT} ")

    # No limit, check if state record produced for incremental stream
    catalog.streams[0].sync_mode = SyncMode.incremental
    records = [r for r in abstract_source.read(logger=logger_mock, config={}, catalog=catalog, state={})]
    assert len(records) == FULL_RECORDS_NUMBER + 1
    assert records[-1].type == Type.STATE

    # Set limit and check if state is produced when limit is set for incremental stream
    logger_mock.reset_mock()
    records = [r for r in abstract_source.read(logger=logger_mock, config=internal_config, catalog=catalog, state={})]
    assert len(records) == STREAM_LIMIT + 1
    assert records[-1].type == Type.STATE
    logger_info_args = [call[0][0] for call in logger_mock.info.call_args_list]
    read_log_record = [_l for _l in logger_info_args if _l.startswith("Read")]
    assert read_log_record[0].startswith(f"Read {STREAM_LIMIT} ")


SCHEMA = {"type": "object", "properties": {"value": {"type": "string"}}}


def test_source_config_no_transform(abstract_source, catalog):
    logger_mock = MagicMock()
    streams = abstract_source.streams(None)
    http_stream, non_http_stream = streams
    http_stream.get_json_schema.return_value = non_http_stream.get_json_schema.return_value = SCHEMA
    http_stream.read_records.return_value, non_http_stream.read_records.return_value = [[{"value": 23}] * 5] * 2
    records = [r for r in abstract_source.read(logger=logger_mock, config={}, catalog=catalog, state={})]
    assert len(records) == 2 * 5
    assert [r.record.data for r in records] == [{"value": 23}] * 2 * 5
    assert http_stream.get_json_schema.call_count == 1
    assert non_http_stream.get_json_schema.call_count == 1


def test_source_config_transform(abstract_source, catalog):
    logger_mock = MagicMock()
    streams = abstract_source.streams(None)
    http_stream, non_http_stream = streams
    http_stream.transformer = TypeTransformer(TransformConfig.DefaultSchemaNormalization)
    non_http_stream.transformer = TypeTransformer(TransformConfig.DefaultSchemaNormalization)
    http_stream.get_json_schema.return_value = non_http_stream.get_json_schema.return_value = SCHEMA
    http_stream.read_records.return_value, non_http_stream.read_records.return_value = [{"value": 23}], [{"value": 23}]
    records = [r for r in abstract_source.read(logger=logger_mock, config={}, catalog=catalog, state={})]
    assert len(records) == 2
    assert [r.record.data for r in records] == [{"value": "23"}] * 2


def test_source_config_transform_and_no_transform(abstract_source, catalog):
    logger_mock = MagicMock()
    streams = abstract_source.streams(None)
    http_stream, non_http_stream = streams
    http_stream.transformer = TypeTransformer(TransformConfig.DefaultSchemaNormalization)
    http_stream.get_json_schema.return_value = non_http_stream.get_json_schema.return_value = SCHEMA
    http_stream.read_records.return_value, non_http_stream.read_records.return_value = [{"value": 23}], [{"value": 23}]
    records = [r for r in abstract_source.read(logger=logger_mock, config={}, catalog=catalog, state={})]
    assert len(records) == 2
    assert [r.record.data for r in records] == [{"value": "23"}, {"value": 23}]
