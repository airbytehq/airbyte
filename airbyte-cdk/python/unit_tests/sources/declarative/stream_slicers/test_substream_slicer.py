#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, Iterable, List, Mapping, Optional, Union

import pytest as pytest
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOption, RequestOptionType
from airbyte_cdk.sources.declarative.stream_slicers.substream_slicer import ParentStreamConfig, SubstreamSlicer
from airbyte_cdk.sources.streams.core import Stream

parent_records = [{"id": 1, "data": "data1"}, {"id": 2, "data": "data2"}]
more_records = [{"id": 10, "data": "data10", "slice": "second_parent"}, {"id": 20, "data": "data20", "slice": "second_parent"}]

data_first_parent_slice = [{"id": 0, "slice": "first", "data": "A"}, {"id": 1, "slice": "first", "data": "B"}]
data_second_parent_slice = [{"id": 2, "slice": "second", "data": "C"}]
data_third_parent_slice = []
all_parent_data = data_first_parent_slice + data_second_parent_slice + data_third_parent_slice
parent_slices = [{"slice": "first"}, {"slice": "second"}, {"slice": "third"}]
second_parent_stream_slice = [{"slice": "second_parent"}]


class MockStream(Stream):
    def __init__(self, slices, records, name):
        self._slices = slices
        self._records = records
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        return "id"

    def stream_slices(
        self, *, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        yield from self._slices

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
            yield from self._records
        else:
            yield from [r for r in self._records if r["slice"] == stream_slice["slice"]]


@pytest.mark.parametrize(
    "test_name, parent_stream_configs, expected_slices",
    [
        ("test_no_parents", [], None),
        (
            "test_single_parent_slices_no_records",
            [
                ParentStreamConfig(
                    stream=MockStream([{}], [], "first_stream"), parent_key="id", stream_slice_field="first_stream_id", options={}
                )
            ],
            [],
        ),
        (
            "test_single_parent_slices_with_records",
            [
                ParentStreamConfig(
                    stream=MockStream([{}], parent_records, "first_stream"),
                    parent_key="id",
                    stream_slice_field="first_stream_id",
                    options={},
                )
            ],
            [{"first_stream_id": 1, "parent_slice": {}}, {"first_stream_id": 2, "parent_slice": {}}],
        ),
        (
            "test_with_parent_slices_and_records",
            [
                ParentStreamConfig(
                    stream=MockStream(parent_slices, all_parent_data, "first_stream"),
                    parent_key="id",
                    stream_slice_field="first_stream_id",
                    options={},
                )
            ],
            [
                {"parent_slice": {"slice": "first"}, "first_stream_id": 0},
                {"parent_slice": {"slice": "first"}, "first_stream_id": 1},
                {"parent_slice": {"slice": "second"}, "first_stream_id": 2},
            ],
        ),
        (
            "test_multiple_parent_streams",
            [
                ParentStreamConfig(
                    stream=MockStream(parent_slices, data_first_parent_slice + data_second_parent_slice, "first_stream"),
                    parent_key="id",
                    stream_slice_field="first_stream_id",
                    options={},
                ),
                ParentStreamConfig(
                    stream=MockStream(second_parent_stream_slice, more_records, "second_stream"),
                    parent_key="id",
                    stream_slice_field="second_stream_id",
                    options={},
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
    ],
)
def test_substream_slicer(test_name, parent_stream_configs, expected_slices):
    if expected_slices is None:
        try:
            SubstreamSlicer(parent_stream_configs=parent_stream_configs, options={})
            assert False
        except ValueError:
            return
    slicer = SubstreamSlicer(parent_stream_configs=parent_stream_configs, options={})
    slices = [s for s in slicer.stream_slices(SyncMode.incremental, stream_state=None)]
    assert slices == expected_slices


@pytest.mark.parametrize(
    "test_name, stream_slice, expected_state",
    [
        ("test_update_cursor_no_state_no_record", {}, {}),
        ("test_update_cursor_with_state_single_parent", {"first_stream_id": "1234"}, {"first_stream_id": "1234"}),
        ("test_update_cursor_with_unknown_state_field", {"unknown_stream_id": "1234"}, {}),
        (
            "test_update_cursor_with_state_from_both_parents",
            {"first_stream_id": "1234", "second_stream_id": "4567"},
            {"first_stream_id": "1234", "second_stream_id": "4567"},
        ),
    ],
)
def test_update_cursor(test_name, stream_slice, expected_state):
    parent_stream_name_to_config = [
        ParentStreamConfig(
            stream=MockStream(parent_slices, data_first_parent_slice + data_second_parent_slice, "first_stream"),
            parent_key="id",
            stream_slice_field="first_stream_id",
            options={},
        ),
        ParentStreamConfig(
            stream=MockStream(second_parent_stream_slice, more_records, "second_stream"),
            parent_key="id",
            stream_slice_field="second_stream_id",
            options={},
        ),
    ]

    slicer = SubstreamSlicer(parent_stream_configs=parent_stream_name_to_config, options={})
    slicer.update_cursor(stream_slice, None)
    updated_state = slicer.get_stream_state()
    assert expected_state == updated_state


@pytest.mark.parametrize(
    "test_name, parent_stream_request_options, expected_req_params, expected_headers, expected_body_json, expected_body_data",
    [
        (
            "test_request_option_in_request_param",
            [
                RequestOption(inject_into=RequestOptionType.request_parameter, options={}, field_name="first_stream"),
                RequestOption(inject_into=RequestOptionType.request_parameter, options={}, field_name="second_stream"),
            ],
            {"first_stream_id": "1234", "second_stream_id": "4567"},
            {},
            {},
            {},
        ),
        (
            "test_request_option_in_header",
            [
                RequestOption(inject_into=RequestOptionType.header, options={}, field_name="first_stream"),
                RequestOption(inject_into=RequestOptionType.header, options={}, field_name="second_stream"),
            ],
            {},
            {"first_stream_id": "1234", "second_stream_id": "4567"},
            {},
            {},
        ),
        (
            "test_request_option_in_param_and_header",
            [
                RequestOption(inject_into=RequestOptionType.request_parameter, options={}, field_name="first_stream"),
                RequestOption(inject_into=RequestOptionType.header, options={}, field_name="second_stream"),
            ],
            {"first_stream_id": "1234"},
            {"second_stream_id": "4567"},
            {},
            {},
        ),
        (
            "test_request_option_in_body_json",
            [
                RequestOption(inject_into=RequestOptionType.body_json, options={}, field_name="first_stream"),
                RequestOption(inject_into=RequestOptionType.body_json, options={}, field_name="second_stream"),
            ],
            {},
            {},
            {"first_stream_id": "1234", "second_stream_id": "4567"},
            {},
        ),
        (
            "test_request_option_in_body_data",
            [
                RequestOption(inject_into=RequestOptionType.body_data, options={}, field_name="first_stream"),
                RequestOption(inject_into=RequestOptionType.body_data, options={}, field_name="second_stream"),
            ],
            {},
            {},
            {},
            {"first_stream_id": "1234", "second_stream_id": "4567"},
        ),
    ],
)
def test_request_option(
    test_name,
    parent_stream_request_options,
    expected_req_params,
    expected_headers,
    expected_body_json,
    expected_body_data,
):
    slicer = SubstreamSlicer(
        parent_stream_configs=[
            ParentStreamConfig(
                stream=MockStream(parent_slices, data_first_parent_slice + data_second_parent_slice, "first_stream"),
                parent_key="id",
                stream_slice_field="first_stream_id",
                options={},
                request_option=parent_stream_request_options[0],
            ),
            ParentStreamConfig(
                stream=MockStream(second_parent_stream_slice, more_records, "second_stream"),
                parent_key="id",
                stream_slice_field="second_stream_id",
                options={},
                request_option=parent_stream_request_options[1],
            ),
        ],
        options={},
    )
    stream_slice = {"first_stream_id": "1234", "second_stream_id": "4567"}

    assert expected_req_params == slicer.get_request_params(stream_slice=stream_slice)
    assert expected_headers == slicer.get_request_headers(stream_slice=stream_slice)
    assert expected_body_json == slicer.get_request_body_json(stream_slice=stream_slice)
    assert expected_body_data == slicer.get_request_body_data(stream_slice=stream_slice)
