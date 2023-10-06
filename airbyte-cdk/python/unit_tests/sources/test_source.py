#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import logging
import tempfile
from collections import defaultdict
from contextlib import nullcontext as does_not_raise
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import pytest
import requests
from airbyte_cdk.models import (
    AirbyteGlobalState,
    AirbyteStateBlob,
    AirbyteStateMessage,
    AirbyteStateType,
    AirbyteStreamState,
    ConfiguredAirbyteCatalog,
    StreamDescriptor,
    SyncMode,
    Type,
)
from airbyte_cdk.sources import AbstractSource, Source
from airbyte_cdk.sources.streams.core import Stream
from airbyte_cdk.sources.streams.http.availability_strategy import HttpAvailabilityStrategy
from airbyte_cdk.sources.streams.http.http import HttpStream, HttpSubStream
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer
from pydantic import ValidationError


class MockSource(Source):
    def read(
        self, logger: logging.Logger, config: Mapping[str, Any], catalog: ConfiguredAirbyteCatalog, state: MutableMapping[str, Any] = None
    ):
        pass

    def check(self, logger: logging.Logger, config: Mapping[str, Any]):
        pass

    def discover(self, logger: logging.Logger, config: Mapping[str, Any]):
        pass


class MockAbstractSource(AbstractSource):
    def __init__(self, streams: Optional[List[Stream]] = None):
        self._streams = streams

    def check_connection(self, *args, **kwargs) -> Tuple[bool, Optional[Any]]:
        return True, ""

    def streams(self, *args, **kwargs) -> List[Stream]:
        if self._streams:
            return self._streams
        return []


@pytest.fixture
def source():
    return MockSource()


@pytest.fixture
def catalog():
    configured_catalog = {
        "streams": [
            {
                "stream": {"name": "mock_http_stream", "json_schema": {}, "supported_sync_modes": ["full_refresh"]},
                "destination_sync_mode": "overwrite",
                "sync_mode": "full_refresh",
            },
            {
                "stream": {"name": "mock_stream", "json_schema": {}, "supported_sync_modes": ["full_refresh"]},
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

    class MockHttpStream(mocker.MagicMock, HttpStream):
        url_base = "http://example.com"
        path = "/dummy/path"
        get_json_schema = mocker.MagicMock()

        def supports_incremental(self):
            return True

        def __init__(self, *args, **kvargs):
            mocker.MagicMock.__init__(self)
            HttpStream.__init__(self, *args, kvargs)
            self.read_records = mocker.MagicMock()

        @property
        def availability_strategy(self):
            return None

    class MockStream(mocker.MagicMock, Stream):
        page_size = None
        get_json_schema = mocker.MagicMock()

        def __init__(self, **kwargs):
            mocker.MagicMock.__init__(self)
            self.read_records = mocker.MagicMock()

    streams = [MockHttpStream(), MockStream()]

    class MockAbstractSource(AbstractSource):
        def check_connection(self):
            return True, None

        def streams(self, config):
            self.streams_config = config
            return streams

    return MockAbstractSource()


@pytest.mark.parametrize(
    "incoming_state, expected_state, expected_error",
    [
        pytest.param(
            [
                {
                    "type": "STREAM",
                    "stream": {
                        "stream_state": {"created_at": "2009-07-19"},
                        "stream_descriptor": {"name": "movies", "namespace": "public"},
                    },
                }
            ],
            [
                AirbyteStateMessage(
                    type=AirbyteStateType.STREAM,
                    stream=AirbyteStreamState(
                        stream_descriptor=StreamDescriptor(name="movies", namespace="public"),
                        stream_state=AirbyteStateBlob.parse_obj({"created_at": "2009-07-19"}),
                    ),
                )
            ],
            does_not_raise(),
            id="test_incoming_stream_state",
        ),
        pytest.param(
            [
                {
                    "type": "STREAM",
                    "stream": {
                        "stream_state": {"created_at": "2009-07-19"},
                        "stream_descriptor": {"name": "movies", "namespace": "public"},
                    },
                },
                {
                    "type": "STREAM",
                    "stream": {
                        "stream_state": {"id": "villeneuve_denis"},
                        "stream_descriptor": {"name": "directors", "namespace": "public"},
                    },
                },
                {
                    "type": "STREAM",
                    "stream": {
                        "stream_state": {"created_at": "1995-12-27"},
                        "stream_descriptor": {"name": "actors", "namespace": "public"},
                    },
                },
            ],
            [
                AirbyteStateMessage(
                    type=AirbyteStateType.STREAM,
                    stream=AirbyteStreamState(
                        stream_descriptor=StreamDescriptor(name="movies", namespace="public"),
                        stream_state=AirbyteStateBlob.parse_obj({"created_at": "2009-07-19"}),
                    ),
                ),
                AirbyteStateMessage(
                    type=AirbyteStateType.STREAM,
                    stream=AirbyteStreamState(
                        stream_descriptor=StreamDescriptor(name="directors", namespace="public"),
                        stream_state=AirbyteStateBlob.parse_obj({"id": "villeneuve_denis"}),
                    ),
                ),
                AirbyteStateMessage(
                    type=AirbyteStateType.STREAM,
                    stream=AirbyteStreamState(
                        stream_descriptor=StreamDescriptor(name="actors", namespace="public"),
                        stream_state=AirbyteStateBlob.parse_obj({"created_at": "1995-12-27"}),
                    ),
                ),
            ],
            does_not_raise(),
            id="test_incoming_multiple_stream_states",
        ),
        pytest.param(
            [
                {
                    "type": "GLOBAL",
                    "global": {
                        "shared_state": {"shared_key": "shared_val"},
                        "stream_states": [
                            {"stream_state": {"created_at": "2009-07-19"}, "stream_descriptor": {"name": "movies", "namespace": "public"}}
                        ],
                    },
                }
            ],
            [
                AirbyteStateMessage.parse_obj(
                    {
                        "type": AirbyteStateType.GLOBAL,
                        "global": AirbyteGlobalState(
                            shared_state=AirbyteStateBlob.parse_obj({"shared_key": "shared_val"}),
                            stream_states=[
                                AirbyteStreamState(
                                    stream_descriptor=StreamDescriptor(name="movies", namespace="public"),
                                    stream_state=AirbyteStateBlob.parse_obj({"created_at": "2009-07-19"}),
                                )
                            ],
                        ),
                    }
                ),
            ],
            does_not_raise(),
            id="test_incoming_global_state",
        ),
        pytest.param(
            {"movies": {"created_at": "2009-07-19"}, "directors": {"id": "villeneuve_denis"}},
            {"movies": {"created_at": "2009-07-19"}, "directors": {"id": "villeneuve_denis"}},
            does_not_raise(),
            id="test_incoming_legacy_state",
        ),
        pytest.param([], defaultdict(dict, {}), does_not_raise(), id="test_empty_incoming_stream_state"),
        pytest.param(None, defaultdict(dict, {}), does_not_raise(), id="test_none_incoming_state"),
        pytest.param({}, defaultdict(dict, {}), does_not_raise(), id="test_empty_incoming_legacy_state"),
        pytest.param(
            [
                {
                    "type": "NOT_REAL",
                    "stream": {
                        "stream_state": {"created_at": "2009-07-19"},
                        "stream_descriptor": {"name": "movies", "namespace": "public"},
                    },
                }
            ],
            None,
            pytest.raises(ValidationError),
            id="test_invalid_stream_state_invalid_type",
        ),
        pytest.param(
            [{"type": "STREAM", "stream": {"stream_state": {"created_at": "2009-07-19"}}}],
            None,
            pytest.raises(ValidationError),
            id="test_invalid_stream_state_missing_descriptor",
        ),
        pytest.param(
            [{"type": "GLOBAL", "global": {"shared_state": {"shared_key": "shared_val"}}}],
            None,
            pytest.raises(ValidationError),
            id="test_invalid_global_state_missing_streams",
        ),
        pytest.param(
            [
                {
                    "type": "GLOBAL",
                    "global": {
                        "shared_state": {"shared_key": "shared_val"},
                        "stream_states": {
                            "stream_state": {"created_at": "2009-07-19"},
                            "stream_descriptor": {"name": "movies", "namespace": "public"},
                        },
                    },
                }
            ],
            None,
            pytest.raises(ValidationError),
            id="test_invalid_global_state_streams_not_list",
        ),
        pytest.param(
            [{"type": "LEGACY", "not": "something"}],
            None,
            pytest.raises(ValueError),
            id="test_invalid_state_message_has_no_stream_global_or_data",
        ),
    ],
)
def test_read_state(source, incoming_state, expected_state, expected_error):
    with tempfile.NamedTemporaryFile("w") as state_file:
        state_file.write(json.dumps(incoming_state))
        state_file.flush()
        with expected_error:
            actual = source.read_state(state_file.name)
            assert actual == expected_state


def test_read_invalid_state(source):
    with tempfile.NamedTemporaryFile("w") as state_file:
        state_file.write("invalid json content")
        state_file.flush()
        with pytest.raises(ValueError, match="Could not read json file"):
            source.read_state(state_file.name)


def test_read_state_sends_new_legacy_format_if_source_does_not_implement_read():
    expected_state = [
        AirbyteStateMessage(
            type=AirbyteStateType.LEGACY, data={"movies": {"created_at": "2009-07-19"}, "directors": {"id": "villeneuve_denis"}}
        )
    ]
    source = MockAbstractSource()
    with tempfile.NamedTemporaryFile("w") as state_file:
        state_file.write(json.dumps({"movies": {"created_at": "2009-07-19"}, "directors": {"id": "villeneuve_denis"}}))
        state_file.flush()
        actual = source.read_state(state_file.name)
        assert actual == expected_state


@pytest.mark.parametrize(
    "source, expected_state",
    [
        pytest.param(MockSource(), {}, id="test_source_implementing_read_returns_legacy_format"),
        pytest.param(MockAbstractSource(), [], id="test_source_not_implementing_read_returns_per_stream_format"),
    ],
)
def test_read_state_nonexistent(source, expected_state):
    assert source.read_state("") == expected_state


def test_read_catalog(source):
    configured_catalog = {
        "streams": [
            {
                "stream": {
                    "name": "mystream",
                    "json_schema": {"type": "object", "properties": {"k": "v"}},
                    "supported_sync_modes": ["full_refresh"],
                },
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
    logger = logging.getLogger(f"airbyte.{getattr(abstract_source, 'name', '')}")
    records = [r for r in abstract_source.read(logger=logger, config={}, catalog=catalog, state={})]
    # 3 for http stream, 3 for non http stream and 3 for stream status messages for each stream (2x)
    assert len(records) == 3 + 3 + 3 + 3
    assert http_stream.read_records.called
    assert non_http_stream.read_records.called
    # Make sure page_size havent been set
    assert not http_stream.page_size
    assert not non_http_stream.page_size
    # Test with records limit set to 1
    internal_config = {"some_config": 100, "_limit": 1}
    records = [r for r in abstract_source.read(logger=logger, config=internal_config, catalog=catalog, state={})]
    # 1 from http stream + 1 from non http stream and 3 for stream status messages for each stream (2x)
    assert len(records) == 1 + 1 + 3 + 3
    assert "_limit" not in abstract_source.streams_config
    assert "some_config" in abstract_source.streams_config
    # Test with records limit set to number that exceeds expceted records
    internal_config = {"some_config": 100, "_limit": 20}
    records = [r for r in abstract_source.read(logger=logger, config=internal_config, catalog=catalog, state={})]
    assert len(records) == 3 + 3 + 3 + 3

    # Check if page_size paramter is set to http instance only
    internal_config = {"some_config": 100, "_page_size": 2}
    records = [r for r in abstract_source.read(logger=logger, config=internal_config, catalog=catalog, state={})]
    assert "_page_size" not in abstract_source.streams_config
    assert "some_config" in abstract_source.streams_config
    assert len(records) == 3 + 3 + 3 + 3
    assert http_stream.page_size == 2
    # Make sure page_size havent been set for non http streams
    assert not non_http_stream.page_size


def test_internal_config_limit(mocker, abstract_source, catalog):
    logger_mock = mocker.MagicMock()
    logger_mock.level = logging.DEBUG
    del catalog.streams[1]
    STREAM_LIMIT = 2
    SLICE_DEBUG_LOG_COUNT = 1
    FULL_RECORDS_NUMBER = 3
    TRACE_STATUS_COUNT = 3
    streams = abstract_source.streams(None)
    http_stream = streams[0]
    http_stream.read_records.return_value = [{}] * FULL_RECORDS_NUMBER
    internal_config = {"some_config": 100, "_limit": STREAM_LIMIT}

    catalog.streams[0].sync_mode = SyncMode.full_refresh
    records = [r for r in abstract_source.read(logger=logger_mock, config=internal_config, catalog=catalog, state={})]
    assert len(records) == STREAM_LIMIT + SLICE_DEBUG_LOG_COUNT + TRACE_STATUS_COUNT
    logger_info_args = [call[0][0] for call in logger_mock.info.call_args_list]
    # Check if log line matches number of limit
    read_log_record = [_l for _l in logger_info_args if _l.startswith("Read")]
    assert read_log_record[0].startswith(f"Read {STREAM_LIMIT} ")

    # No limit, check if state record produced for incremental stream
    catalog.streams[0].sync_mode = SyncMode.incremental
    records = [r for r in abstract_source.read(logger=logger_mock, config={}, catalog=catalog, state={})]
    assert len(records) == FULL_RECORDS_NUMBER + SLICE_DEBUG_LOG_COUNT + TRACE_STATUS_COUNT + 1
    assert records[-2].type == Type.STATE
    assert records[-1].type == Type.TRACE

    # Set limit and check if state is produced when limit is set for incremental stream
    logger_mock.reset_mock()
    records = [r for r in abstract_source.read(logger=logger_mock, config=internal_config, catalog=catalog, state={})]
    assert len(records) == STREAM_LIMIT + SLICE_DEBUG_LOG_COUNT + TRACE_STATUS_COUNT + 1
    assert records[-2].type == Type.STATE
    assert records[-1].type == Type.TRACE
    logger_info_args = [call[0][0] for call in logger_mock.info.call_args_list]
    read_log_record = [_l for _l in logger_info_args if _l.startswith("Read")]
    assert read_log_record[0].startswith(f"Read {STREAM_LIMIT} ")


SCHEMA = {"type": "object", "properties": {"value": {"type": "string"}}}


def test_source_config_no_transform(mocker, abstract_source, catalog):
    SLICE_DEBUG_LOG_COUNT = 1
    TRACE_STATUS_COUNT = 3
    logger_mock = mocker.MagicMock()
    logger_mock.level = logging.DEBUG
    streams = abstract_source.streams(None)
    http_stream, non_http_stream = streams
    http_stream.get_json_schema.return_value = non_http_stream.get_json_schema.return_value = SCHEMA
    http_stream.read_records.return_value, non_http_stream.read_records.return_value = [[{"value": 23}] * 5] * 2
    records = [r for r in abstract_source.read(logger=logger_mock, config={}, catalog=catalog, state={})]
    assert len(records) == 2 * (5 + SLICE_DEBUG_LOG_COUNT + TRACE_STATUS_COUNT)
    assert [r.record.data for r in records if r.type == Type.RECORD] == [{"value": 23}] * 2 * 5
    assert http_stream.get_json_schema.call_count == 5
    assert non_http_stream.get_json_schema.call_count == 5


def test_source_config_transform(mocker, abstract_source, catalog):
    logger_mock = mocker.MagicMock()
    logger_mock.level = logging.DEBUG
    SLICE_DEBUG_LOG_COUNT = 2
    TRACE_STATUS_COUNT = 6
    streams = abstract_source.streams(None)
    http_stream, non_http_stream = streams
    http_stream.transformer = TypeTransformer(TransformConfig.DefaultSchemaNormalization)
    non_http_stream.transformer = TypeTransformer(TransformConfig.DefaultSchemaNormalization)
    http_stream.get_json_schema.return_value = non_http_stream.get_json_schema.return_value = SCHEMA
    http_stream.read_records.return_value, non_http_stream.read_records.return_value = [{"value": 23}], [{"value": 23}]
    records = [r for r in abstract_source.read(logger=logger_mock, config={}, catalog=catalog, state={})]
    assert len(records) == 2 + SLICE_DEBUG_LOG_COUNT + TRACE_STATUS_COUNT
    assert [r.record.data for r in records if r.type == Type.RECORD] == [{"value": "23"}] * 2


def test_source_config_transform_and_no_transform(mocker, abstract_source, catalog):
    logger_mock = mocker.MagicMock()
    logger_mock.level = logging.DEBUG
    SLICE_DEBUG_LOG_COUNT = 2
    TRACE_STATUS_COUNT = 6
    streams = abstract_source.streams(None)
    http_stream, non_http_stream = streams
    http_stream.transformer = TypeTransformer(TransformConfig.DefaultSchemaNormalization)
    http_stream.get_json_schema.return_value = non_http_stream.get_json_schema.return_value = SCHEMA
    http_stream.read_records.return_value, non_http_stream.read_records.return_value = [{"value": 23}], [{"value": 23}]
    records = [r for r in abstract_source.read(logger=logger_mock, config={}, catalog=catalog, state={})]
    assert len(records) == 2 + SLICE_DEBUG_LOG_COUNT + TRACE_STATUS_COUNT
    assert [r.record.data for r in records if r.type == Type.RECORD] == [{"value": "23"}, {"value": 23}]


def test_read_default_http_availability_strategy_stream_available(catalog, mocker):
    mocker.patch.multiple(HttpStream, __abstractmethods__=set())
    mocker.patch.multiple(Stream, __abstractmethods__=set())

    class MockHttpStream(mocker.MagicMock, HttpStream):
        url_base = "http://example.com"
        path = "/dummy/path"
        get_json_schema = mocker.MagicMock()

        def supports_incremental(self):
            return True

        def __init__(self, *args, **kvargs):
            mocker.MagicMock.__init__(self)
            HttpStream.__init__(self, *args, kvargs)
            self.read_records = mocker.MagicMock()

    class MockStream(mocker.MagicMock, Stream):
        page_size = None
        get_json_schema = mocker.MagicMock()

        def __init__(self, *args, **kvargs):
            mocker.MagicMock.__init__(self)
            self.read_records = mocker.MagicMock()

    streams = [MockHttpStream(), MockStream()]
    http_stream, non_http_stream = streams
    assert isinstance(http_stream, HttpStream)
    assert not isinstance(non_http_stream, HttpStream)

    assert isinstance(http_stream.availability_strategy, HttpAvailabilityStrategy)
    assert non_http_stream.availability_strategy is None

    # Add an extra record for the default HttpAvailabilityStrategy to pull from
    # during the try: next(records) check, since we are mocking the return value
    # and not re-creating the generator like we would during actual reading
    http_stream.read_records.return_value = iter([{"value": "test"}] + [{}] * 3)
    non_http_stream.read_records.return_value = iter([{}] * 3)

    source = MockAbstractSource(streams=streams)
    logger = logging.getLogger(f"airbyte.{getattr(abstract_source, 'name', '')}")
    records = [r for r in source.read(logger=logger, config={}, catalog=catalog, state={})]
    # 3 for http stream, 3 for non http stream and 3 for stream status messages for each stream (2x)
    assert len(records) == 3 + 3 + 3 + 3
    assert http_stream.read_records.called
    assert non_http_stream.read_records.called


def test_read_default_http_availability_strategy_stream_unavailable(catalog, mocker, caplog):
    mocker.patch.multiple(Stream, __abstractmethods__=set())

    class MockHttpStream(HttpStream):
        url_base = "https://test_base_url.com"
        primary_key = ""

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.resp_counter = 1

        def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
            return None

        def path(self, **kwargs) -> str:
            return ""

        def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
            stub_response = {"data": self.resp_counter}
            self.resp_counter += 1
            yield stub_response

    class MockStream(mocker.MagicMock, Stream):
        page_size = None
        get_json_schema = mocker.MagicMock()

        def __init__(self, *args, **kvargs):
            mocker.MagicMock.__init__(self)
            self.read_records = mocker.MagicMock()

    streams = [MockHttpStream(), MockStream()]
    http_stream, non_http_stream = streams
    assert isinstance(http_stream, HttpStream)
    assert not isinstance(non_http_stream, HttpStream)

    assert isinstance(http_stream.availability_strategy, HttpAvailabilityStrategy)
    assert non_http_stream.availability_strategy is None

    # Don't set anything for read_records return value for HttpStream, since
    # it should be skipped due to the stream being unavailable
    non_http_stream.read_records.return_value = iter([{}] * 3)

    # Patch HTTP request to stream endpoint to make it unavailable
    req = requests.Response()
    req.status_code = 403
    mocker.patch.object(requests.Session, "send", return_value=req)

    source = MockAbstractSource(streams=streams)
    logger = logging.getLogger("test_read_default_http_availability_strategy_stream_unavailable")
    with caplog.at_level(logging.WARNING):
        records = [r for r in source.read(logger=logger, config={}, catalog=catalog, state={})]

    # 0 for http stream, 3 for non http stream and 3 status trace messages
    assert len(records) == 0 + 3 + 3
    assert non_http_stream.read_records.called
    expected_logs = [
        f"Skipped syncing stream '{http_stream.name}' because it was unavailable.",
        f"Unable to read {http_stream.name} stream.",
        "This is most likely due to insufficient permissions on the credentials in use.",
        f"Please visit https://docs.airbyte.com/integrations/sources/{source.name} to learn more.",
    ]
    for message in expected_logs:
        assert message in caplog.text


def test_read_default_http_availability_strategy_parent_stream_unavailable(catalog, mocker, caplog):
    """Test default availability strategy if error happens during slice extraction (reading of parent stream)"""
    mocker.patch.multiple(Stream, __abstractmethods__=set())

    class MockHttpParentStream(HttpStream):
        url_base = "https://test_base_url.com"
        primary_key = ""

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.resp_counter = 1

        def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
            return None

        def path(self, **kwargs) -> str:
            return ""

        def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
            stub_response = {"data": self.resp_counter}
            self.resp_counter += 1
            yield stub_response

    class MockHttpStream(HttpSubStream):
        url_base = "https://test_base_url.com"
        primary_key = ""

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.resp_counter = 1

        def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
            return None

        def path(self, **kwargs) -> str:
            return ""

        def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
            stub_response = {"data": self.resp_counter}
            self.resp_counter += 1
            yield stub_response

    http_stream = MockHttpStream(parent=MockHttpParentStream())
    streams = [http_stream]
    assert isinstance(http_stream, HttpSubStream)
    assert isinstance(http_stream.availability_strategy, HttpAvailabilityStrategy)

    # Patch HTTP request to stream endpoint to make it unavailable
    req = requests.Response()
    req.status_code = 403
    mocker.patch.object(requests.Session, "send", return_value=req)

    source = MockAbstractSource(streams=streams)
    logger = logging.getLogger("test_read_default_http_availability_strategy_parent_stream_unavailable")
    configured_catalog = {
        "streams": [
            {
                "stream": {
                    "name": "mock_http_stream",
                    "json_schema": {"type": "object", "properties": {"k": "v"}},
                    "supported_sync_modes": ["full_refresh"],
                },
                "destination_sync_mode": "overwrite",
                "sync_mode": "full_refresh",
            }
        ]
    }
    catalog = ConfiguredAirbyteCatalog.parse_obj(configured_catalog)
    with caplog.at_level(logging.WARNING):
        records = [r for r in source.read(logger=logger, config={}, catalog=catalog, state={})]

    # 0 for http stream, 3 for non http stream and 3 status trace messages
    assert len(records) == 0
    expected_logs = [
        f"Skipped syncing stream '{http_stream.name}' because it was unavailable.",
        f"Unable to get slices for {http_stream.name} stream, because of error in parent stream",
        "This is most likely due to insufficient permissions on the credentials in use.",
        f"Please visit https://docs.airbyte.com/integrations/sources/{source.name} to learn more.",
    ]
    for message in expected_logs:
        assert message in caplog.text
