#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from functools import partial
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Union

import pytest as pytest
from airbyte_cdk.models import AirbyteMessage, AirbyteRecordMessage, SyncMode, Type
from airbyte_cdk.sources.declarative.declarative_stream import DeclarativeStream
from airbyte_cdk.sources.declarative.incremental import ChildPartitionResumableFullRefreshCursor, ResumableFullRefreshCursor
from airbyte_cdk.sources.declarative.incremental.per_partition_cursor import CursorFactory, PerPartitionCursor, StreamSlice
from airbyte_cdk.sources.declarative.interpolation import InterpolatedString
from airbyte_cdk.sources.declarative.partition_routers.substream_partition_router import ParentStreamConfig, SubstreamPartitionRouter
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOption, RequestOptionType
from airbyte_cdk.sources.streams.checkpoint import Cursor
from airbyte_cdk.sources.types import Record
from airbyte_cdk.utils import AirbyteTracedException

parent_records = [{"id": 1, "data": "data1"}, {"id": 2, "data": "data2"}]
more_records = [{"id": 10, "data": "data10", "slice": "second_parent"}, {"id": 20, "data": "data20", "slice": "second_parent"}]

data_first_parent_slice = [{"id": 0, "slice": "first", "data": "A"}, {"id": 1, "slice": "first", "data": "B"}]
data_second_parent_slice = [{"id": 2, "slice": "second", "data": "C"}]
data_third_parent_slice = []
all_parent_data = data_first_parent_slice + data_second_parent_slice + data_third_parent_slice
parent_slices = [{"slice": "first"}, {"slice": "second"}, {"slice": "third"}]
second_parent_stream_slice = [StreamSlice(partition={"slice": "second_parent"}, cursor_slice={})]

data_first_parent_slice_with_cursor = [
    {"id": 0, "slice": "first", "data": "A", "cursor": "first_cursor_0"},
    {"id": 1, "slice": "first", "data": "B", "cursor": "first_cursor_1"},
]
data_second_parent_slice_with_cursor = [{"id": 2, "slice": "second", "data": "C", "cursor": "second_cursor_2"}]
all_parent_data_with_cursor = data_first_parent_slice_with_cursor + data_second_parent_slice_with_cursor


class MockStream(DeclarativeStream):
    def __init__(self, slices, records, name, cursor_field="", cursor=None):
        self.config = {}
        self._slices = slices
        self._records = records
        self._stream_cursor_field = (
            InterpolatedString.create(cursor_field, parameters={}) if isinstance(cursor_field, str) else cursor_field
        )
        self._name = name
        self._state = {"states": []}
        self._cursor = cursor

    @property
    def name(self) -> str:
        return self._name

    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        return "id"

    @property
    def state(self) -> Mapping[str, Any]:
        return self._state

    @state.setter
    def state(self, value: Mapping[str, Any]) -> None:
        self._state = value

    @property
    def is_resumable(self) -> bool:
        return bool(self._cursor)

    def get_cursor(self) -> Optional[Cursor]:
        return self._cursor

    def stream_slices(
        self, *, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[StreamSlice]]:
        for s in self._slices:
            if isinstance(s, StreamSlice):
                yield s
            else:
                yield StreamSlice(partition=s, cursor_slice={})

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        # The parent stream's records should always be read as full refresh
        assert sync_mode == SyncMode.full_refresh

        if not stream_slice:
            result = self._records
        else:
            result = [Record(data=r, associated_slice=stream_slice) for r in self._records if r["slice"] == stream_slice["slice"]]

        yield from result

        # Update the state only after reading the full slice
        cursor_field = self._stream_cursor_field.eval(config=self.config)
        if stream_slice and cursor_field and result:
            self._state["states"].append({cursor_field: result[-1][cursor_field], "partition": stream_slice["slice"]})

    def get_json_schema(self) -> Mapping[str, Any]:
        return {}


class MockIncrementalStream(MockStream):
    def __init__(self, slices, records, name, cursor_field="", cursor=None, date_ranges=None):
        super().__init__(slices, records, name, cursor_field, cursor)
        if date_ranges is None:
            date_ranges = []
        self._date_ranges = date_ranges
        self._state = {}

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        results = [record for record in self._records if stream_slice["start_time"] <= record["updated_at"] <= stream_slice["end_time"]]
        print(f"about to emit {results}")
        yield from results
        print(f"setting state to {stream_slice}")
        self._state = stream_slice


class MockResumableFullRefreshStream(MockStream):
    def __init__(self, slices, name, cursor_field="", cursor=None, record_pages: Optional[List[List[Mapping[str, Any]]]] = None):
        super().__init__(slices, [], name, cursor_field, cursor)
        if record_pages:
            self._record_pages = record_pages
        else:
            self._record_pages = []
        self._state: MutableMapping[str, Any] = {}

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        page_number = self.state.get("next_page_token") or 1
        yield from self._record_pages[page_number - 1]

        cursor = self.get_cursor()
        if page_number < len(self._record_pages):
            cursor.close_slice(StreamSlice(cursor_slice={"next_page_token": page_number + 1}, partition={}))
        else:
            cursor.close_slice(StreamSlice(cursor_slice={"__ab_full_refresh_sync_complete": True}, partition={}))

    @property
    def state(self) -> Mapping[str, Any]:
        cursor = self.get_cursor()
        return cursor.get_stream_state() if cursor else {}

    @state.setter
    def state(self, value: Mapping[str, Any]) -> None:
        self._state = value


@pytest.mark.parametrize(
    "parent_stream_configs, expected_slices",
    [
        ([], None),
        (
            [
                ParentStreamConfig(
                    stream=MockStream([{}], [], "first_stream"),
                    parent_key="id",
                    partition_field="first_stream_id",
                    parameters={},
                    config={},
                )
            ],
            [],
        ),
        (
            [
                ParentStreamConfig(
                    stream=MockStream([{}], parent_records, "first_stream"),
                    parent_key="id",
                    partition_field="first_stream_id",
                    parameters={},
                    config={},
                )
            ],
            [{"first_stream_id": 1, "parent_slice": {}}, {"first_stream_id": 2, "parent_slice": {}}],
        ),
        (
            [
                ParentStreamConfig(
                    stream=MockStream(parent_slices, all_parent_data, "first_stream"),
                    parent_key="id",
                    partition_field="first_stream_id",
                    parameters={},
                    config={},
                )
            ],
            [
                {"parent_slice": {"slice": "first"}, "first_stream_id": 0},
                {"parent_slice": {"slice": "first"}, "first_stream_id": 1},
                {"parent_slice": {"slice": "second"}, "first_stream_id": 2},
            ],
        ),
        (
            [
                ParentStreamConfig(
                    stream=MockStream(
                        [StreamSlice(partition=p, cursor_slice={"start": 0, "end": 1}) for p in parent_slices],
                        all_parent_data,
                        "first_stream",
                    ),
                    parent_key="id",
                    partition_field="first_stream_id",
                    parameters={},
                    config={},
                )
            ],
            [
                {"parent_slice": {"slice": "first"}, "first_stream_id": 0},
                {"parent_slice": {"slice": "first"}, "first_stream_id": 1},
                {"parent_slice": {"slice": "second"}, "first_stream_id": 2},
            ],
        ),
        (
            [
                ParentStreamConfig(
                    stream=MockStream(parent_slices, data_first_parent_slice + data_second_parent_slice, "first_stream"),
                    parent_key="id",
                    partition_field="first_stream_id",
                    parameters={},
                    config={},
                ),
                ParentStreamConfig(
                    stream=MockStream(second_parent_stream_slice, more_records, "second_stream"),
                    parent_key="id",
                    partition_field="second_stream_id",
                    parameters={},
                    config={},
                ),
            ],
            [
                {"parent_slice": {"slice": "first"}, "first_stream_id": 0},
                {"parent_slice": {"slice": "first"}, "first_stream_id": 1},
                {"parent_slice": {"slice": "second"}, "first_stream_id": 2},
                {"parent_slice": {"slice": "second_parent"}, "second_stream_id": 10},
                {"parent_slice": {"slice": "second_parent"}, "second_stream_id": 20},
            ],
        ),
        (
            [
                ParentStreamConfig(
                    stream=MockStream([{}], [{"id": 0}, {"id": 1}, {"_id": 2}, {"id": 3}], "first_stream"),
                    parent_key="id",
                    partition_field="first_stream_id",
                    parameters={},
                    config={},
                )
            ],
            [
                {"first_stream_id": 0, "parent_slice": {}},
                {"first_stream_id": 1, "parent_slice": {}},
                {"first_stream_id": 3, "parent_slice": {}},
            ],
        ),
        (
            [
                ParentStreamConfig(
                    stream=MockStream([{}], [{"a": {"b": 0}}, {"a": {"b": 1}}, {"a": {"c": 2}}, {"a": {"b": 3}}], "first_stream"),
                    parent_key="a/b",
                    partition_field="first_stream_id",
                    parameters={},
                    config={},
                )
            ],
            [
                {"first_stream_id": 0, "parent_slice": {}},
                {"first_stream_id": 1, "parent_slice": {}},
                {"first_stream_id": 3, "parent_slice": {}},
            ],
        ),
    ],
    ids=[
        "test_no_parents",
        "test_single_parent_slices_no_records",
        "test_single_parent_slices_with_records",
        "test_with_parent_slices_and_records",
        "test_multiple_parent_streams",
        "test_cursor_values_are_removed_from_parent_slices",
        "test_missed_parent_key",
        "test_dpath_extraction",
    ],
)
def test_substream_partition_router(parent_stream_configs, expected_slices):
    if expected_slices is None:
        try:
            SubstreamPartitionRouter(parent_stream_configs=parent_stream_configs, parameters={}, config={})
            assert False
        except ValueError:
            return
    partition_router = SubstreamPartitionRouter(parent_stream_configs=parent_stream_configs, parameters={}, config={})
    slices = [s for s in partition_router.stream_slices()]
    assert slices == expected_slices


def test_substream_partition_router_invalid_parent_record_type():
    partition_router = SubstreamPartitionRouter(
        parent_stream_configs=[
            ParentStreamConfig(
                stream=MockStream([{}], [list()], "first_stream"),
                parent_key="id",
                partition_field="first_stream_id",
                parameters={},
                config={},
            )
        ],
        parameters={},
        config={},
    )

    with pytest.raises(AirbyteTracedException):
        _ = [s for s in partition_router.stream_slices()]


@pytest.mark.parametrize(
    "parent_stream_request_parameters, expected_req_params, expected_headers, expected_body_json, expected_body_data",
    [
        (
            [
                RequestOption(inject_into=RequestOptionType.request_parameter, parameters={}, field_name="first_stream"),
                RequestOption(inject_into=RequestOptionType.request_parameter, parameters={}, field_name="second_stream"),
            ],
            {"first_stream": "1234", "second_stream": "4567"},
            {},
            {},
            {},
        ),
        (
            [
                RequestOption(inject_into=RequestOptionType.header, parameters={}, field_name="first_stream"),
                RequestOption(inject_into=RequestOptionType.header, parameters={}, field_name="second_stream"),
            ],
            {},
            {"first_stream": "1234", "second_stream": "4567"},
            {},
            {},
        ),
        (
            [
                RequestOption(inject_into=RequestOptionType.request_parameter, parameters={}, field_name="first_stream"),
                RequestOption(inject_into=RequestOptionType.header, parameters={}, field_name="second_stream"),
            ],
            {"first_stream": "1234"},
            {"second_stream": "4567"},
            {},
            {},
        ),
        (
            [
                RequestOption(inject_into=RequestOptionType.body_json, parameters={}, field_name="first_stream"),
                RequestOption(inject_into=RequestOptionType.body_json, parameters={}, field_name="second_stream"),
            ],
            {},
            {},
            {"first_stream": "1234", "second_stream": "4567"},
            {},
        ),
        (
            [
                RequestOption(inject_into=RequestOptionType.body_data, parameters={}, field_name="first_stream"),
                RequestOption(inject_into=RequestOptionType.body_data, parameters={}, field_name="second_stream"),
            ],
            {},
            {},
            {},
            {"first_stream": "1234", "second_stream": "4567"},
        ),
    ],
    ids=[
        "test_request_option_in_request_param",
        "test_request_option_in_header",
        "test_request_option_in_param_and_header",
        "test_request_option_in_body_json",
        "test_request_option_in_body_data",
    ],
)
def test_request_option(
    parent_stream_request_parameters,
    expected_req_params,
    expected_headers,
    expected_body_json,
    expected_body_data,
):
    partition_router = SubstreamPartitionRouter(
        parent_stream_configs=[
            ParentStreamConfig(
                stream=MockStream(parent_slices, data_first_parent_slice + data_second_parent_slice, "first_stream"),
                parent_key="id",
                partition_field="first_stream_id",
                parameters={},
                config={},
                request_option=parent_stream_request_parameters[0],
            ),
            ParentStreamConfig(
                stream=MockStream(second_parent_stream_slice, more_records, "second_stream"),
                parent_key="id",
                partition_field="second_stream_id",
                parameters={},
                config={},
                request_option=parent_stream_request_parameters[1],
            ),
        ],
        parameters={},
        config={},
    )
    stream_slice = {"first_stream_id": "1234", "second_stream_id": "4567"}

    assert partition_router.get_request_params(stream_slice=stream_slice) == expected_req_params
    assert partition_router.get_request_headers(stream_slice=stream_slice) == expected_headers
    assert partition_router.get_request_body_json(stream_slice=stream_slice) == expected_body_json
    assert partition_router.get_request_body_data(stream_slice=stream_slice) == expected_body_data


@pytest.mark.parametrize(
    "parent_stream_config, expected_state",
    [
        (
            ParentStreamConfig(
                stream=MockStream(parent_slices, all_parent_data_with_cursor, "first_stream", cursor_field="cursor"),
                parent_key="id",
                partition_field="first_stream_id",
                parameters={},
                config={},
                incremental_dependency=True,
            ),
            {
                "first_stream": {
                    "states": [{"cursor": "first_cursor_1", "partition": "first"}, {"cursor": "second_cursor_2", "partition": "second"}]
                }
            },
        ),
    ],
    ids=[
        "test_incremental_dependency_state_update_with_cursor",
    ],
)
def test_substream_slicer_parent_state_update_with_cursor(parent_stream_config, expected_state):
    partition_router = SubstreamPartitionRouter(parent_stream_configs=[parent_stream_config], parameters={}, config={})

    # Simulate reading the records and updating the state
    for _ in partition_router.stream_slices():
        pass  # This will process the slices and should update the parent state

    # Check if the parent state has been updated correctly
    parent_state = partition_router.get_stream_state()
    assert parent_state == expected_state


@pytest.mark.parametrize(
    "field_name_first_stream, field_name_second_stream, expected_request_params",
    [
        (
            "{{parameters['field_name_first_stream']}}",
            "{{parameters['field_name_second_stream']}}",
            {"parameter_first_stream_id": "1234", "parameter_second_stream_id": "4567"},
        ),
        (
            "{{config['field_name_first_stream']}}",
            "{{config['field_name_second_stream']}}",
            {"config_first_stream_id": "1234", "config_second_stream_id": "4567"},
        ),
    ],
    ids=[
        "parameters_interpolation",
        "config_interpolation",
    ],
)
def test_request_params_interpolation_for_parent_stream(
    field_name_first_stream: str, field_name_second_stream: str, expected_request_params: dict
):
    config = {"field_name_first_stream": "config_first_stream_id", "field_name_second_stream": "config_second_stream_id"}
    parameters = {"field_name_first_stream": "parameter_first_stream_id", "field_name_second_stream": "parameter_second_stream_id"}
    partition_router = SubstreamPartitionRouter(
        parent_stream_configs=[
            ParentStreamConfig(
                stream=MockStream(parent_slices, data_first_parent_slice + data_second_parent_slice, "first_stream"),
                parent_key="id",
                partition_field="first_stream_id",
                parameters=parameters,
                config=config,
                request_option=RequestOption(
                    inject_into=RequestOptionType.request_parameter, parameters=parameters, field_name=field_name_first_stream
                ),
            ),
            ParentStreamConfig(
                stream=MockStream(second_parent_stream_slice, more_records, "second_stream"),
                parent_key="id",
                partition_field="second_stream_id",
                parameters=parameters,
                config=config,
                request_option=RequestOption(
                    inject_into=RequestOptionType.request_parameter, parameters=parameters, field_name=field_name_second_stream
                ),
            ),
        ],
        parameters=parameters,
        config=config,
    )
    stream_slice = {"first_stream_id": "1234", "second_stream_id": "4567"}

    assert partition_router.get_request_params(stream_slice=stream_slice) == expected_request_params


def test_given_record_is_airbyte_message_when_stream_slices_then_use_record_data():
    parent_slice = {}
    partition_router = SubstreamPartitionRouter(
        parent_stream_configs=[
            ParentStreamConfig(
                stream=MockStream(
                    [parent_slice],
                    [
                        AirbyteMessage(
                            type=Type.RECORD, record=AirbyteRecordMessage(data={"id": "record value"}, emitted_at=0, stream="stream")
                        )
                    ],
                    "first_stream",
                ),
                parent_key="id",
                partition_field="partition_field",
                parameters={},
                config={},
            )
        ],
        parameters={},
        config={},
    )

    slices = list(partition_router.stream_slices())
    assert slices == [{"partition_field": "record value", "parent_slice": parent_slice}]


def test_given_record_is_record_object_when_stream_slices_then_use_record_data():
    parent_slice = {}
    partition_router = SubstreamPartitionRouter(
        parent_stream_configs=[
            ParentStreamConfig(
                stream=MockStream([parent_slice], [Record({"id": "record value"}, {})], "first_stream"),
                parent_key="id",
                partition_field="partition_field",
                parameters={},
                config={},
            )
        ],
        parameters={},
        config={},
    )

    slices = list(partition_router.stream_slices())
    assert slices == [{"partition_field": "record value", "parent_slice": parent_slice}]


def test_substream_using_incremental_parent_stream():
    mock_slices = [
        StreamSlice(cursor_slice={"start_time": "2024-04-27", "end_time": "2024-05-27"}, partition={}),
        StreamSlice(cursor_slice={"start_time": "2024-05-27", "end_time": "2024-06-27"}, partition={}),
    ]

    expected_slices = [
        {"partition_field": "may_record_0", "parent_slice": {}},
        {"partition_field": "may_record_1", "parent_slice": {}},
        {"partition_field": "jun_record_0", "parent_slice": {}},
        {"partition_field": "jun_record_1", "parent_slice": {}},
    ]

    partition_router = SubstreamPartitionRouter(
        parent_stream_configs=[
            ParentStreamConfig(
                stream=MockIncrementalStream(
                    slices=mock_slices,
                    records=[
                        Record({"id": "may_record_0", "updated_at": "2024-05-15"}, mock_slices[0]),
                        Record({"id": "may_record_1", "updated_at": "2024-05-16"}, mock_slices[0]),
                        Record({"id": "jun_record_0", "updated_at": "2024-06-15"}, mock_slices[1]),
                        Record({"id": "jun_record_1", "updated_at": "2024-06-16"}, mock_slices[1]),
                    ],
                    name="first_stream",
                ),
                parent_key="id",
                partition_field="partition_field",
                parameters={},
                config={},
            )
        ],
        parameters={},
        config={},
    )

    actual_slices = list(partition_router.stream_slices())
    assert actual_slices == expected_slices


def test_substream_checkpoints_after_each_parent_partition():
    """
    This test validates the specific behavior that when getting all parent records for a substream,
    we are still updating state so that the parent stream's state is updated after we finish getting all
    parent records for the parent slice (not just the substream)
    """
    mock_slices = [
        StreamSlice(cursor_slice={"start_time": "2024-04-27", "end_time": "2024-05-27"}, partition={}),
        StreamSlice(cursor_slice={"start_time": "2024-05-27", "end_time": "2024-06-27"}, partition={}),
    ]

    expected_slices = [
        {"partition_field": "may_record_0", "parent_slice": {}},
        {"partition_field": "may_record_1", "parent_slice": {}},
        {"partition_field": "jun_record_0", "parent_slice": {}},
        {"partition_field": "jun_record_1", "parent_slice": {}},
    ]

    expected_parent_state = [
        {},
        {"first_stream": {}},
        {"first_stream": {}},
        {"first_stream": {"start_time": "2024-04-27", "end_time": "2024-05-27"}},
        {"first_stream": {"start_time": "2024-05-27", "end_time": "2024-06-27"}},
    ]

    partition_router = SubstreamPartitionRouter(
        parent_stream_configs=[
            ParentStreamConfig(
                stream=MockIncrementalStream(
                    slices=mock_slices,
                    records=[
                        Record({"id": "may_record_0", "updated_at": "2024-05-15"}, mock_slices[0]),
                        Record({"id": "may_record_1", "updated_at": "2024-05-16"}, mock_slices[0]),
                        Record({"id": "jun_record_0", "updated_at": "2024-06-15"}, mock_slices[1]),
                        Record({"id": "jun_record_1", "updated_at": "2024-06-16"}, mock_slices[1]),
                    ],
                    name="first_stream",
                ),
                incremental_dependency=True,
                parent_key="id",
                partition_field="partition_field",
                parameters={},
                config={},
            )
        ],
        parameters={},
        config={},
    )

    expected_counter = 0
    for actual_slice in partition_router.stream_slices():
        assert actual_slice == expected_slices[expected_counter]
        assert partition_router._parent_state == expected_parent_state[expected_counter]
        expected_counter += 1
    assert partition_router._parent_state == expected_parent_state[expected_counter]


@pytest.mark.parametrize(
    "use_incremental_dependency",
    [
        pytest.param(False, id="test_resumable_full_refresh_stream_without_parent_checkpoint"),
        pytest.param(True, id="test_resumable_full_refresh_stream_with_use_incremental_dependency_for_parent_checkpoint"),
    ],
)
def test_substream_using_resumable_full_refresh_parent_stream(use_incremental_dependency):
    mock_slices = [
        StreamSlice(cursor_slice={}, partition={}),
        StreamSlice(cursor_slice={"next_page_token": 2}, partition={}),
        StreamSlice(cursor_slice={"next_page_token": 3}, partition={}),
    ]

    expected_slices = [
        {"partition_field": "makoto_yuki", "parent_slice": {}},
        {"partition_field": "yukari_takeba", "parent_slice": {}},
        {"partition_field": "mitsuru_kirijo", "parent_slice": {}},
        {"partition_field": "akihiko_sanada", "parent_slice": {}},
        {"partition_field": "junpei_iori", "parent_slice": {}},
        {"partition_field": "fuuka_yamagishi", "parent_slice": {}},
    ]

    expected_parent_state = [
        {},
        {"persona_3_characters": {}},
        {"persona_3_characters": {}},
        {"persona_3_characters": {"next_page_token": 2}},
        {"persona_3_characters": {"next_page_token": 2}},
        {"persona_3_characters": {"next_page_token": 3}},
        {"persona_3_characters": {"__ab_full_refresh_sync_complete": True}},
    ]

    partition_router = SubstreamPartitionRouter(
        parent_stream_configs=[
            ParentStreamConfig(
                stream=MockResumableFullRefreshStream(
                    slices=[StreamSlice(partition={}, cursor_slice={})],
                    cursor=ResumableFullRefreshCursor(parameters={}),
                    record_pages=[
                        [
                            Record(data={"id": "makoto_yuki"}, associated_slice=mock_slices[0]),
                            Record(data={"id": "yukari_takeba"}, associated_slice=mock_slices[0]),
                        ],
                        [
                            Record(data={"id": "mitsuru_kirijo"}, associated_slice=mock_slices[1]),
                            Record(data={"id": "akihiko_sanada"}, associated_slice=mock_slices[1]),
                        ],
                        [
                            Record(data={"id": "junpei_iori"}, associated_slice=mock_slices[2]),
                            Record(data={"id": "fuuka_yamagishi"}, associated_slice=mock_slices[2]),
                        ],
                    ],
                    name="persona_3_characters",
                ),
                incremental_dependency=use_incremental_dependency,
                parent_key="id",
                partition_field="partition_field",
                parameters={},
                config={},
            )
        ],
        parameters={},
        config={},
    )

    expected_counter = 0
    for actual_slice in partition_router.stream_slices():
        assert actual_slice == expected_slices[expected_counter]
        if use_incremental_dependency:
            assert partition_router._parent_state == expected_parent_state[expected_counter]
        expected_counter += 1
    if use_incremental_dependency:
        assert partition_router._parent_state == expected_parent_state[expected_counter]


@pytest.mark.parametrize(
    "use_incremental_dependency",
    [
        pytest.param(False, id="test_substream_resumable_full_refresh_stream_without_parent_checkpoint"),
        pytest.param(True, id="test_substream_resumable_full_refresh_stream_with_use_incremental_dependency_for_parent_checkpoint"),
    ],
)
def test_substream_using_resumable_full_refresh_parent_stream_slices(use_incremental_dependency):
    mock_parent_slices = [
        StreamSlice(cursor_slice={}, partition={}),
        StreamSlice(cursor_slice={"next_page_token": 2}, partition={}),
        StreamSlice(cursor_slice={"next_page_token": 3}, partition={}),
    ]

    expected_parent_slices = [
        {"partition_field": "makoto_yuki", "parent_slice": {}},
        {"partition_field": "yukari_takeba", "parent_slice": {}},
        {"partition_field": "mitsuru_kirijo", "parent_slice": {}},
        {"partition_field": "akihiko_sanada", "parent_slice": {}},
        {"partition_field": "junpei_iori", "parent_slice": {}},
        {"partition_field": "fuuka_yamagishi", "parent_slice": {}},
    ]

    expected_parent_state = [
        {},
        {"persona_3_characters": {}},
        {"persona_3_characters": {}},
        {"persona_3_characters": {"next_page_token": 2}},
        {"persona_3_characters": {"next_page_token": 2}},
        {"persona_3_characters": {"next_page_token": 3}},
        {"persona_3_characters": {"__ab_full_refresh_sync_complete": True}},
    ]

    expected_substream_state = {
        "states": [
            {"partition": {"parent_slice": {}, "partition_field": "makoto_yuki"}, "cursor": {"__ab_full_refresh_sync_complete": True}},
            {"partition": {"parent_slice": {}, "partition_field": "yukari_takeba"}, "cursor": {"__ab_full_refresh_sync_complete": True}},
            {"partition": {"parent_slice": {}, "partition_field": "mitsuru_kirijo"}, "cursor": {"__ab_full_refresh_sync_complete": True}},
            {"partition": {"parent_slice": {}, "partition_field": "akihiko_sanada"}, "cursor": {"__ab_full_refresh_sync_complete": True}},
            {"partition": {"parent_slice": {}, "partition_field": "junpei_iori"}, "cursor": {"__ab_full_refresh_sync_complete": True}},
            {"partition": {"parent_slice": {}, "partition_field": "fuuka_yamagishi"}, "cursor": {"__ab_full_refresh_sync_complete": True}},
        ],
        "parent_state": {"persona_3_characters": {"__ab_full_refresh_sync_complete": True}},
    }

    partition_router = SubstreamPartitionRouter(
        parent_stream_configs=[
            ParentStreamConfig(
                stream=MockResumableFullRefreshStream(
                    slices=[StreamSlice(partition={}, cursor_slice={})],
                    cursor=ResumableFullRefreshCursor(parameters={}),
                    record_pages=[
                        [
                            Record(data={"id": "makoto_yuki"}, associated_slice=mock_parent_slices[0]),
                            Record(data={"id": "yukari_takeba"}, associated_slice=mock_parent_slices[0]),
                        ],
                        [
                            Record(data={"id": "mitsuru_kirijo"}, associated_slice=mock_parent_slices[1]),
                            Record(data={"id": "akihiko_sanada"}, associated_slice=mock_parent_slices[1]),
                        ],
                        [
                            Record(data={"id": "junpei_iori"}, associated_slice=mock_parent_slices[2]),
                            Record(data={"id": "fuuka_yamagishi"}, associated_slice=mock_parent_slices[2]),
                        ],
                    ],
                    name="persona_3_characters",
                ),
                incremental_dependency=use_incremental_dependency,
                parent_key="id",
                partition_field="partition_field",
                parameters={},
                config={},
            )
        ],
        parameters={},
        config={},
    )

    substream_cursor_slicer = PerPartitionCursor(
        cursor_factory=CursorFactory(create_function=partial(ChildPartitionResumableFullRefreshCursor, {})),
        partition_router=partition_router,
    )

    expected_counter = 0
    for actual_slice in substream_cursor_slicer.stream_slices():
        # close the substream slice
        substream_cursor_slicer.close_slice(actual_slice)
        # check the slice has been processed
        assert actual_slice == expected_parent_slices[expected_counter]
        # check for parent state
        if use_incremental_dependency:
            assert substream_cursor_slicer._partition_router._parent_state == expected_parent_state[expected_counter]
        expected_counter += 1
    if use_incremental_dependency:
        assert substream_cursor_slicer._partition_router._parent_state == expected_parent_state[expected_counter]

    # validate final state for closed substream slices
    final_state = substream_cursor_slicer.get_stream_state()
    if not use_incremental_dependency:
        assert final_state["states"] == expected_substream_state["states"], "State for substreams is not valid!"
    else:
        assert final_state == expected_substream_state, "State for substreams with incremental dependency is not valid!"


@pytest.mark.parametrize(
    "parent_stream_configs, expected_slices",
    [
        (
            [
                ParentStreamConfig(
                    stream=MockStream(
                        [{}],
                        [
                            {"id": 1, "field_1": "value_1", "field_2": {"nested_field": "nested_value_1"}},
                            {"id": 2, "field_1": "value_2", "field_2": {"nested_field": "nested_value_2"}},
                        ],
                        "first_stream",
                    ),
                    parent_key="id",
                    partition_field="first_stream_id",
                    extra_fields=[["field_1"], ["field_2", "nested_field"]],
                    parameters={},
                    config={},
                )
            ],
            [
                {"field_1": "value_1", "field_2.nested_field": "nested_value_1"},
                {"field_1": "value_2", "field_2.nested_field": "nested_value_2"},
            ],
        ),
        (
            [
                ParentStreamConfig(
                    stream=MockStream([{}], [{"id": 1, "field_1": "value_1"}, {"id": 2, "field_1": "value_2"}], "first_stream"),
                    parent_key="id",
                    partition_field="first_stream_id",
                    extra_fields=[["field_1"]],
                    parameters={},
                    config={},
                )
            ],
            [{"field_1": "value_1"}, {"field_1": "value_2"}],
        ),
    ],
    ids=[
        "test_with_nested_extra_keys",
        "test_with_single_extra_key",
    ],
)
def test_substream_partition_router_with_extra_keys(parent_stream_configs, expected_slices):
    partition_router = SubstreamPartitionRouter(parent_stream_configs=parent_stream_configs, parameters={}, config={})
    slices = [s.extra_fields for s in partition_router.stream_slices()]
    assert slices == expected_slices
