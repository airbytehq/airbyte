#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from collections import OrderedDict
from typing import Optional, Mapping, Any, Iterable, List
from unittest.mock import Mock, patch

import pytest
from airbyte_cdk.sources.declarative.incremental.cursor import Cursor
from airbyte_cdk.sources.declarative.incremental.per_partition_cursor import (
    PerPartitionCursor,
    PerPartitionKeySerializer,
    PerPartitionStreamSlice, CursorFactory,
)
from airbyte_cdk.sources.declarative.stream_slicers.stream_slicer import StreamSlicer
from airbyte_cdk.sources.declarative.types import Record
from airbyte_cdk.sources.declarative.incremental import DatetimeBasedCursor
from airbyte_cdk.sources.declarative.partition_routers import SubstreamPartitionRouter
from airbyte_cdk.sources.declarative.datetime import MinMaxDatetime
from airbyte_cdk.sources.declarative.requesters import RequestOption
from airbyte_cdk.sources.declarative.declarative_stream import DeclarativeStream
from airbyte_cdk.sources.declarative.requesters import HttpRequester
from airbyte_cdk.sources.declarative.retrievers import SimpleRetriever
from airbyte_cdk.sources.declarative.auth.token import BasicHttpAuthenticator
from airbyte_cdk.sources.declarative.decoders import JsonDecoder
from airbyte_cdk.sources.declarative.extractors import RecordSelector, DpathExtractor
from airbyte_cdk.sources.declarative.interpolation import InterpolatedString, InterpolatedBoolean
from airbyte_cdk.sources.declarative.partition_routers.substream_partition_router import ParentStreamConfig
from airbyte_cdk.sources.declarative.requesters.paginators import DefaultPaginator
from airbyte_cdk.sources.declarative.requesters.request_options import InterpolatedRequestOptionsProvider
from airbyte_cdk.sources.declarative.requesters.request_path import RequestPath
from airbyte_cdk.sources.utils.transform import TypeTransformer, TransformConfig
from airbyte_cdk.sources.declarative.requesters.paginators.strategies import PageIncrement
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOptionType
from airbyte_cdk.sources.declarative.requesters.requester import HttpMethod
from airbyte_cdk.sources.streams.core import StreamData
from airbyte_cdk.models import AirbyteMessage, AirbyteRecordMessage, SyncMode
from airbyte_cdk.models import Type as MessageType

PARTITION = {
    "partition_key string": "partition value",
    "partition_key int": 1,
    "partition_key list str": ["list item 1", "list item 2"],
    "partition_key list dict": [
        {"dict within list key 1-1": "dict within list value 1-1", "dict within list key 1-2": "dict within list value 1-2"},
        {"dict within list key 2": "dict within list value 2"},
    ],
    "partition_key nested dict": {
        "nested_partition_key 1": "a nested value",
        "nested_partition_key 2": "another nested value",
    },
}

CURSOR_SLICE_FIELD = "cursor slice field"
CURSOR_STATE_KEY = "cursor state"
CURSOR_STATE = {CURSOR_STATE_KEY: "a state value"}
NOT_CONSIDERED_BECAUSE_MOCKED_CURSOR_HAS_NO_STATE = "any"
STATE = {
    "states": [
        {
            "partition": {
                "partition_router_field_1": "X1",
                "partition_router_field_2": "Y1",
            },
            "cursor": {"cursor state field": 1},
        },
        {
            "partition": {
                "partition_router_field_1": "X2",
                "partition_router_field_2": "Y2",
            },
            "cursor": {"cursor state field": 2},
        },
    ]
}


def test_partition_serialization():
    serializer = PerPartitionKeySerializer()
    assert serializer.to_partition(serializer.to_partition_key(PARTITION)) == PARTITION


def test_partition_with_different_key_orders():
    ordered_dict = OrderedDict({"1": 1, "2": 2})
    same_dict_with_different_order = OrderedDict({"2": 2, "1": 1})
    serializer = PerPartitionKeySerializer()

    assert serializer.to_partition_key(ordered_dict) == serializer.to_partition_key(same_dict_with_different_order)


def test_given_tuples_in_json_then_deserialization_convert_to_list():
    """
    This is a known issue with the current implementation. However, the assumption is that this wouldn't be a problem as we only use the
    immutability and we expect stream slices to be immutable anyway
    """
    serializer = PerPartitionKeySerializer()
    partition_with_tuple = {"key": (1, 2, 3)}

    assert partition_with_tuple != serializer.to_partition(serializer.to_partition_key(partition_with_tuple))


def test_stream_slice_merge_dictionaries():
    stream_slice = PerPartitionStreamSlice({"partition key": "partition value"}, {"cursor key": "cursor value"})
    assert stream_slice == {"partition key": "partition value", "cursor key": "cursor value"}


def test_overlapping_slice_keys_raise_error():
    with pytest.raises(ValueError):
        PerPartitionStreamSlice({"overlapping key": "partition value"}, {"overlapping key": "cursor value"})


class MockedCursorBuilder:
    def __init__(self):
        self._stream_slices = []
        self._stream_state = {}

    def with_stream_slices(self, stream_slices):
        self._stream_slices = stream_slices
        return self

    def with_stream_state(self, stream_state):
        self._stream_state = stream_state
        return self

    def build(self):
        cursor = Mock(spec=Cursor)
        cursor.get_stream_state.return_value = self._stream_state
        cursor.stream_slices.return_value = self._stream_slices
        return cursor


@pytest.fixture()
def mocked_partition_router():
    return Mock(spec=StreamSlicer)


@pytest.fixture()
def mocked_cursor_factory():
    cursor_factory = Mock()
    cursor_factory.create.return_value = MockedCursorBuilder().build()
    return cursor_factory


def create_cursor() -> StreamSlicer:
    return DatetimeBasedCursor(
        cursor_field="date_submitted",
        start_datetime=MinMaxDatetime(
            # datetime='{{ config[''start_date''] }}',
            datetime='2024-01-01T00:00:00Z',
            datetime_format='%Y-%m-%dT%H:%M:%SZ',
            parameters={},
        ),
        datetime_format='%Y-%m-%d+%H:%M:%S',
        start_time_option=RequestOption(
            field_name="fIX_THIS",
            inject_into="request_parameter",
            parameters={},
        ),
        cursor_datetime_formats=['%Y-%m-%d %H:%M:%S EST'],
        config={},
        parameters={},
    )

def test_partition_router_using_incremental_date_parent_cursor(
        mocked_cursor_factory, mocked_partition_router
):
    partition = {"partition_field_1": "a value", "partition_field_2": "another value"}
    mocked_partition_router.stream_slices.return_value = [partition]
    cursor_slices = [{"start_datetime": 1}]
    mocked_cursor_factory.create.return_value = MockedCursorBuilder().with_stream_slices(cursor_slices).build()

    # cursor = PerPartitionCursor(mocked_cursor_factory, mocked_partition_router)
    datetime_cursor_factory = CursorFactory(
        lambda: create_cursor(),
    )

    parent_stream = create_declarative_stream()
    substream_partition_router = SubstreamPartitionRouter(
        parent_stream_configs=[ParentStreamConfig(
            stream=parent_stream,
            parent_key="id",
            partition_field="parent_id",
            parameters={},
            config={}
        )],
        config={},
        parameters={}
    )
    cursor = PerPartitionCursor(datetime_cursor_factory, substream_partition_router)

    # Define a mock function to replace my_method
    def mock_my_method(
            sync_mode: SyncMode,
            cursor_field: Optional[List[str]] = None,
            stream_slice: Optional[Mapping[str, Any]] = None,
            stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[StreamData]:
        yield AirbyteMessage(type=MessageType.RECORD, record=AirbyteRecordMessage(stream="surveys", data={"id": "7628838"}, emitted_at=1234))

    # Simulate getting slice for the first time without any state
    with patch.object(parent_stream, 'read_records', new=mock_my_method):
        slices = list(cursor.stream_slices())

        the_slice = slices[0]
        most_recent_record = Record(
            data={
                "date_submitted": "2024-01-11 00:00:00 EST",
                "id": "98765",
                "name": "some_survey_question"
            },
            associated_slice=None,
        )

        # After simple retriever reads records, it calls close_slice() to update current slice with the latest record
        cursor.close_slice(the_slice, most_recent_record)

        post_state = cursor.get_stream_state()

    assert len(slices) == 1

    # Simulate getting slices the second time but this time with an already persisted state
    existing_state = {
        "cursor": {
            "date_submitted": "2024-01-10+06:13:29"
        },
        "partition": {
            "parent_id": "7628838",
            "parent_slice": {
                "end_time": "2024-01-10+06:13:29",
                "start_time": "2024-01-01+00:00:00"
            }
        }
    }
    cursor_existing_state = PerPartitionCursor(datetime_cursor_factory, substream_partition_router)

    # In AbstractSource._read_incremental(), we invoke stream_instance.state = stream_state, which will call SimpleRetriever.state
    # setter and this will in turn call cursor.set_initial_state() which is why we use this to simulate calling from outside
    cursor_existing_state.set_initial_state({"states": [existing_state]})

    with patch.object(parent_stream, 'read_records', new=mock_my_method):
        slices = list(cursor_existing_state.stream_slices())

        the_new_slice = slices[0]
        most_recent_record = Record(
            data={
                "date_submitted": "2024-01-11 00:00:00 EST",
                "id": "98765",
                "name": "some_survey_question"
            },
            associated_slice=None,
        )

        # After simple retriever reads records, it calls close_slice() to update current slice with the latest record
        cursor_existing_state.close_slice(the_new_slice, most_recent_record)

        # The last thing done in the AbstractSource is to call get_stream_state() and emit it to the platform
        state_to_emit = cursor_existing_state.get_stream_state()
        import pprint
        pprint.pprint(state_to_emit)


def create_declarative_stream() -> DeclarativeStream:
    return DeclarativeStream(
        retriever=SimpleRetriever(
            requester=HttpRequester(
                name='jobs',
                url_base='https://harvest.greenhouse.io/v1/',
                path='departments',
                config={'api_key': '46ec9ae8ab90183d0923095882959cca-3'},
                authenticator=BasicHttpAuthenticator(
                    username="{{ config['api_key'] }}",
                    config={'api_key': '46ec9ae8ab90183d0923095882959cca-3'},
                    password='',
                    parameters={},
                ),
                http_method=HttpMethod.GET,
                request_options_provider=InterpolatedRequestOptionsProvider(
                    config={'api_key': '46ec9ae8ab90183d0923095882959cca-3'},
                    request_parameters={},
                    request_headers={},
                    request_body_data={},
                    request_body_json={},
                    parameters={},
                ),
                parameters={},
            ),
            record_selector=RecordSelector(
                extractor=DpathExtractor(
                    field_path=[],
                    config={'api_key': '46ec9ae8ab90183d0923095882959cca-3'},
                    decoder=JsonDecoder(parameters={}),
                    parameters={},
                ),
                config={'api_key': '46ec9ae8ab90183d0923095882959cca-3'},
                parameters={},
                schema_normalization=TypeTransformer(TransformConfig.DefaultSchemaNormalization)
            ),
            paginator=DefaultPaginator(
                pagination_strategy=PageIncrement(
                    page_size=100,
                    start_from_page=1,
                    parameters={},
                ),
                config={'api_key': '46ec9ae8ab90183d0923095882959cca-3'},
                url_base=InterpolatedString(
                    string='https://harvest.greenhouse.io/v1/',
                    default='https://harvest.greenhouse.io/v1/',
                    parameters={},
                ),
                decoder=JsonDecoder(parameters={}),
                page_size_option=RequestOption(
                    field_name='per_page',
                    inject_into=RequestOptionType.request_parameter,
                    parameters={},
                ),
                page_token_option=RequestPath(parameters={}),
                parameters={},
            ),
            stream_slicer=DatetimeBasedCursor(
                cursor_field="date_submitted",
                start_datetime=MinMaxDatetime(
                    # datetime='{{ config[''start_date''] }}',
                    datetime='2024-01-01T00:00:00Z',
                    datetime_format='%Y-%m-%dT%H:%M:%SZ',
                    parameters={},
                ),
                datetime_format='%Y-%m-%d+%H:%M:%S',
                start_time_option=RequestOption(
                    field_name="fIX_THIS",
                    inject_into="request_parameter",
                    parameters={},
                ),
                cursor_datetime_formats=['%Y-%m-%d %H:%M:%S EST'],
                config={},
                parameters={},
            ),
            cursor=DatetimeBasedCursor(
                cursor_field="date_submitted",
                start_datetime=MinMaxDatetime(
                    # datetime='{{ config[''start_date''] }}',
                    datetime='2024-01-01T00:00:00Z',
                    datetime_format='%Y-%m-%dT%H:%M:%SZ',
                    parameters={},
                ),
                datetime_format='%Y-%m-%d+%H:%M:%S',
                start_time_option=RequestOption(
                    field_name="fIX_THIS",
                    inject_into="request_parameter",
                    parameters={},
                ),
                cursor_datetime_formats=['%Y-%m-%d %H:%M:%S EST'],
                config={},
                parameters={},
            ),
            config={},
            parameters={}
        ),
        config={'api_key': '46ec9ae8ab90183d0923095882959cca-3'},
        name='jobs',
        primary_key='id',
        stream_cursor_field='',
        parameters={}
    )
