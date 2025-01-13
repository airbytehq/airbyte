#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from typing import Any
from unittest.mock import MagicMock, Mock

import pytest
from requests import Response

from airbyte_cdk.models import AirbyteMessage, SyncMode, Type
from airbyte_cdk.sources.declarative.partition_routers.substream_partition_router import ParentStreamConfig
from airbyte_cdk.sources.streams import Stream


def _create_response(content: Any) -> Response:
    response = Response()
    response._content = json.dumps(content).encode("utf-8")
    return response


def test_slicer(components_module):
    IncrementalSingleSlice = components_module.IncrementalSingleSlice
    date_time_dict = {"updated_at": 1662459010}
    slicer = IncrementalSingleSlice(config={}, parameters={}, cursor_field="updated_at")
    slicer.close_slice(date_time_dict, date_time_dict)
    assert slicer.get_stream_state() == date_time_dict
    assert slicer.get_request_headers() == {}
    assert slicer.get_request_body_data() == {}
    assert slicer.get_request_body_json() == {}


@pytest.mark.parametrize(
    "last_record, expected, records",
    [
        (
            {"first_stream_cursor": 1662459010},
            {"parent_stream_name": {"parent_cursor_field": 1662459010}, "first_stream_cursor": 1662459010},
            [{"first_stream_cursor": 1662459010}],
        ),
        (None, {}, []),
    ],
)
def test_sub_slicer(components_module, last_record, expected, records):
    IncrementalSubstreamSlicer = components_module.IncrementalSubstreamSlicer
    parent_stream = Mock(spec=Stream)
    parent_stream.name = "parent_stream_name"
    parent_stream.cursor_field = "parent_cursor_field"
    parent_stream.stream_slices.return_value = [{"a slice": "value"}]
    parent_stream.read_records = MagicMock(return_value=records)

    parent_config = ParentStreamConfig(
        stream=parent_stream,
        parent_key="id",
        partition_field="first_stream_id",
        parameters={},
        config={},
    )

    slicer = IncrementalSubstreamSlicer(
        config={}, parameters={}, cursor_field="first_stream_cursor", parent_stream_configs=[parent_config], nested_items_per_page=10
    )
    stream_slice = next(slicer.stream_slices()) if records else {}
    slicer.close_slice(stream_slice, last_record)
    assert slicer.get_stream_state() == expected


def test_null_records(components_module, caplog):
    MondayIncrementalItemsExtractor = components_module.MondayIncrementalItemsExtractor
    extractor = MondayIncrementalItemsExtractor(
        field_path=["data", "boards", "*"],
        config={},
        parameters={},
    )
    content = {
        "data": {
            "boards": [
                {"board_kind": "private", "id": "1234561", "updated_at": "2023-08-15T10:30:49Z"},
                {"board_kind": "private", "id": "1234562", "updated_at": "2023-08-15T10:30:50Z"},
                {"board_kind": "private", "id": "1234563", "updated_at": "2023-08-15T10:30:51Z"},
                {"board_kind": "private", "id": "1234564", "updated_at": "2023-08-15T10:30:52Z"},
                {"board_kind": "private", "id": "1234565", "updated_at": "2023-08-15T10:30:43Z"},
                {"board_kind": "private", "id": "1234566", "updated_at": "2023-08-15T10:30:54Z"},
                None,
                None,
            ]
        },
        "errors": [{"message": "Cannot return null for non-nullable field Board.creator"}],
        "account_id": 123456,
    }
    response = _create_response(content)
    records = extractor.extract_records(response)
    warning_message = "Record with null value received; errors: [{'message': 'Cannot return null for non-nullable field Board.creator'}]"
    assert warning_message in caplog.messages
    expected_records = [
        {"board_kind": "private", "id": "1234561", "updated_at": "2023-08-15T10:30:49Z", "updated_at_int": 1692095449},
        {"board_kind": "private", "id": "1234562", "updated_at": "2023-08-15T10:30:50Z", "updated_at_int": 1692095450},
        {"board_kind": "private", "id": "1234563", "updated_at": "2023-08-15T10:30:51Z", "updated_at_int": 1692095451},
        {"board_kind": "private", "id": "1234564", "updated_at": "2023-08-15T10:30:52Z", "updated_at_int": 1692095452},
        {"board_kind": "private", "id": "1234565", "updated_at": "2023-08-15T10:30:43Z", "updated_at_int": 1692095443},
        {"board_kind": "private", "id": "1234566", "updated_at": "2023-08-15T10:30:54Z", "updated_at_int": 1692095454},
    ]
    assert records == expected_records


@pytest.fixture
def mock_parent_stream():
    def mock_parent_stream_slices(*args, **kwargs):
        return iter([{"ids": [123]}])

    mock_stream = MagicMock(spec=Stream)
    mock_stream.primary_key = "id"  # Example primary key
    mock_stream.stream_slices = mock_parent_stream_slices
    mock_stream.parent_config = ParentStreamConfig(
        stream=mock_stream,
        parent_key="id",
        partition_field="parent_stream_id",
        parameters={},
        config={},
    )

    return mock_stream


@pytest.mark.parametrize(
    "stream_state, parent_records, expected_slices",
    [
        ({}, [], [{}]),
        (
            {"updated_at": "2022-01-01T00:00:00Z"},
            [
                AirbyteMessage(
                    type=Type.RECORD,
                    record={
                        "data": {"id": 123, "name": "Sample Record", "updated_at": "2023-01-01T00:00:00Z"},
                        "stream": "projects",
                        "emitted_at": 1632095449,
                    },
                )
            ],
            [{"parent_stream_id": [123]}],
        ),
        ({"updated_at": "2022-01-01T00:00:00Z"}, AirbyteMessage(type=Type.LOG), []),
    ],
    ids=["no stream state", "successfully read parent record", "skip non_record AirbyteMessage"],
)
def test_read_parent_stream(components_module, mock_parent_stream, stream_state, parent_records, expected_slices):
    IncrementalSubstreamSlicer = components_module.IncrementalSubstreamSlicer
    slicer = IncrementalSubstreamSlicer(
        config={},
        parameters={},
        cursor_field="updated_at",
        parent_stream_configs=[mock_parent_stream.parent_config],
        nested_items_per_page=10,
    )

    mock_parent_stream.read_records = MagicMock(return_value=parent_records)
    slicer.parent_cursor_field = "updated_at"

    slices = list(slicer.read_parent_stream(sync_mode=SyncMode.full_refresh, cursor_field="updated_at", stream_state=stream_state))

    assert slices == expected_slices


def test_set_initial_state(components_module):
    IncrementalSubstreamSlicer = components_module.IncrementalSubstreamSlicer
    slicer = IncrementalSubstreamSlicer(
        config={},
        parameters={},
        cursor_field="updated_at_int",
        parent_stream_configs=[MagicMock(parent_stream_name="parent_stream")],
        nested_items_per_page=10,
    )

    initial_stream_state = {"updated_at_int": 1662459010, "parent_stream": {"parent_cursor_field": 1662459011}}

    expected_state = {"updated_at_int": 1662459010}
    slicer.set_initial_state(initial_stream_state)
    assert slicer._state == expected_state


from unittest.mock import MagicMock

import pytest

from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.requesters.requester import HttpMethod
from airbyte_cdk.sources.declarative.schema.json_file_schema_loader import JsonFileSchemaLoader


nested_object_schema = {
    "root": {
        "type": ["null", "array"],
        "properties": {"nested": {"type": ["null", "object"], "properties": {"nested_of_nested": {"type": ["null", "string"]}}}},
    },
    "sibling": {"type": ["null", "string"]},
}

nested_array_schema = {
    "root": {
        "type": ["null", "array"],
        "items": {
            "type": ["null", "array"],
            "properties": {"nested": {"type": ["null", "object"], "properties": {"nested_of_nested": {"type": ["null", "string"]}}}},
        },
    },
    "sibling": {"type": ["null", "string"]},
}


@pytest.mark.parametrize(
    ("input_schema", "stream_name", "config", "graphql_query", "next_page_token"),
    [
        pytest.param(
            nested_object_schema,
            "test_stream",
            {},
            {"query": "query{test_stream(limit:100,page:2){root{nested{nested_of_nested}},sibling}}"},
            {"next_page_token": 2},
            id="test_get_request_params_produces_graphql_query_for_object_items",
        ),
        pytest.param(
            nested_array_schema,
            "test_stream",
            {},
            {"query": "query{test_stream(limit:100,page:2){root{nested{nested_of_nested}},sibling}}"},
            {"next_page_token": 2},
            id="test_get_request_params_produces_graphql_query_for_array_items",
        ),
        pytest.param(
            nested_array_schema,
            "items",
            {},
            {"query": 'query{next_items_page(limit:100,cursor:"cursor_bla"){cursor,items{root{nested{nested_of_nested}},sibling}}}'},
            {"next_page_token": (2, "cursor_bla")},
            id="test_get_request_params_produces_graphql_query_for_items_stream",
        ),
        pytest.param(
            nested_array_schema,
            "teams",
            {"teams_limit": 100},
            {"query": "query{teams(limit:100,page:2){id,name,picture_url,users(limit:100){id}}}"},
            {"next_page_token": 2},
            id="test_get_request_params_produces_graphql_query_for_teams_optimized_stream",
        ),
        pytest.param(
            nested_array_schema,
            "teams",
            {},
            {"query": "query{teams(limit:100,page:2){root{nested{nested_of_nested}},sibling}}"},
            {"next_page_token": 2},
            id="test_get_request_params_produces_graphql_query_for_teams_stream",
        ),
    ],
)
def test_get_request_params(components_module, mocker, input_schema, graphql_query, stream_name, config, next_page_token):
    MondayGraphqlRequester = components_module.MondayGraphqlRequester
    mocker.patch.object(MondayGraphqlRequester, "_get_schema_root_properties", return_value=input_schema)
    requester = MondayGraphqlRequester(
        name="a name",
        url_base="https://api.monday.com/v2",
        path="a-path",
        http_method=HttpMethod.GET,
        request_options_provider=MagicMock(),
        authenticator=MagicMock(),
        error_handler=MagicMock(),
        limit="{{ parameters['items_per_page'] }}",
        nested_limit="{{ parameters.get('nested_items_per_page', 1) }}",
        parameters={"name": stream_name, "items_per_page": 100, "nested_items_per_page": 100},
        config=config,
    )
    assert requester.get_request_params(stream_state={}, stream_slice={}, next_page_token=next_page_token) == graphql_query


@pytest.fixture
def monday_requester(components_module):
    MondayGraphqlRequester = components_module.MondayGraphqlRequester
    return MondayGraphqlRequester(
        name="a name",
        url_base="https://api.monday.com/v2",
        path="a-path",
        config={},
        parameters={"name": "activity_logs"},
        limit=InterpolatedString.create("100", parameters={"name": "activity_logs"}),
        nested_limit=InterpolatedString.create("100", parameters={"name": "activity_logs"}),
    )


def test_get_schema_root_properties(mocker, monday_requester):
    mock_schema = {
        "properties": {
            "updated_at_int": {"type": "integer"},
            "created_at_int": {"type": "integer"},
            "pulse_id": {"type": "integer"},
            "board_id": {"type": "integer"},
            "other_field": {"type": "string"},
            "yet_another_field": {"type": "boolean"},
        }
    }

    mocker.patch.object(JsonFileSchemaLoader, "get_json_schema", return_value=mock_schema)
    requester = monday_requester
    result_schema = requester._get_schema_root_properties()

    assert result_schema == {"other_field": {"type": "string"}, "yet_another_field": {"type": "boolean"}}


def test_build_activity_query(components_module, mocker, monday_requester):
    MondayGraphqlRequester = components_module.MondayGraphqlRequester
    mock_stream_state = {"updated_at_int": 1636738688}
    object_arguments = {"stream_state": mock_stream_state}
    mocker.patch.object(MondayGraphqlRequester, "_get_object_arguments", return_value="stream_state:{{ stream_state['updated_at_int'] }}")
    requester = monday_requester

    result = requester._build_activity_query(object_name="activity_logs", field_schema={}, sub_page=None, **object_arguments)
    assert (
        result
        == "boards(stream_state:{{ stream_state['updated_at_int'] }}){activity_logs(stream_state:{{ stream_state['updated_at_int'] }}){}}"
    )


def test_build_items_incremental_query(monday_requester):
    object_name = "test_items"
    field_schema = {
        "id": {"type": "integer"},
        "name": {"type": "string"},
        "column_values": {
            "properties": {
                "id": {"type": ["null", "string"]},
                "text": {"type": ["null", "string"]},
                "type": {"type": ["null", "string"]},
                "value": {"type": ["null", "string"]},
                "display_value": {"type": ["null", "string"]},
            }
        },
    }
    stream_slice = {"ids": [1, 2, 3]}

    built_query = monday_requester._build_items_incremental_query(object_name, field_schema, stream_slice)

    assert (
        built_query == "items(limit:100,ids:[1, 2, 3]){id,name,column_values{id,text,type,value,... on MirrorValue{display_value},"
        "... on BoardRelationValue{display_value},... on DependencyValue{display_value}}}"
    )


def test_get_request_headers(monday_requester):
    headers = monday_requester.get_request_headers()

    assert headers == {"API-Version": "2024-01"}


from unittest.mock import MagicMock

import pytest


@pytest.mark.parametrize(
    ("response_json", "last_records", "expected"),
    [
        pytest.param(
            {"data": {"boards": [{"items": [{"id": "1"}]}]}},
            [{"id": "1"}],
            (1, 2),
            id="test_next_item_page_for_the_same_board",
        ),
        pytest.param(
            {"data": {"boards": [{"items": []}]}},
            [],
            (2, 1),
            id="test_next_board_page_with_item_page_reset",
        ),
        pytest.param(
            {"data": {"boards": []}},
            [],
            None,
            id="test_end_pagination",
        ),
    ],
)
def test_item_pagination_strategy(components_module, response_json, last_records, expected):
    ItemPaginationStrategy = components_module.ItemPaginationStrategy
    strategy = ItemPaginationStrategy(
        config={},
        page_size=1,
        parameters={"items_per_page": 1},
    )
    response = MagicMock()
    response.json.return_value = response_json

    assert strategy.next_page_token(response, last_records) == expected


@pytest.mark.parametrize(
    ("response_json", "last_records", "expected"),
    [
        pytest.param(
            {"data": {"boards": [{"items_page": {"cursor": "bla", "items": [{"id": "1"}]}}]}},
            [],
            (1, "bla"),
            id="test_cursor_in_first_request",
        ),
        pytest.param(
            {"data": {"next_items_page": {"cursor": "bla2", "items": [{"id": "1"}]}}},
            [],
            (1, "bla2"),
            id="test_cursor_in_next_page",
        ),
        pytest.param(
            {"data": {"next_items_page": {"items": [{"id": "1"}]}}},
            [],
            (2, None),
            id="test_next_board_page",
        ),
        pytest.param(
            {"data": {"boards": []}},
            [],
            None,
            id="test_end_pagination",
        ),
    ],
)
def test_item_cursor_pagination_strategy(components_module, response_json, last_records, expected):
    ItemCursorPaginationStrategy = components_module.ItemCursorPaginationStrategy
    strategy = ItemCursorPaginationStrategy(
        config={},
        page_size=1,
        parameters={"items_per_page": 1},
    )
    response = MagicMock()
    response.json.return_value = response_json

    assert strategy.next_page_token(response, last_records) == expected


from unittest.mock import MagicMock


def test_extract_records(components_module):
    MondayActivityExtractor = components_module.MondayActivityExtractor
    # Mock the response
    response = MagicMock()
    response_body = {
        "data": {"boards": [{"activity_logs": [{"data": '{"pulse_id": 123}', "entity": "pulse", "created_at": "16367386880000000"}]}]}
    }

    response.json.return_value = response_body
    extractor = MondayActivityExtractor(parameters={})
    records = extractor.extract_records(response)

    # Assertions
    assert len(records) == 1
    assert records[0]["pulse_id"] == 123
    assert records[0]["created_at_int"] == 1636738688


def test_empty_activity_logs_extract_records(components_module):
    MondayActivityExtractor = components_module.MondayActivityExtractor
    response = MagicMock()
    response_body = {"data": {"boards": [{"activity_logs": None}]}}

    response.json.return_value = response_body
    extractor = MondayActivityExtractor(parameters={})
    records = extractor.extract_records(response)

    assert len(records) == 0


def test_extract_records_incremental(components_module):
    MondayIncrementalItemsExtractor = components_module.MondayIncrementalItemsExtractor
    # Mock the response
    response = MagicMock()
    response_body = {"data": {"boards": [{"id": 1, "column_values": [{"id": 11, "text": None, "display_value": "Hola amigo!"}]}]}}

    response.json.return_value = response_body
    extractor = MondayIncrementalItemsExtractor(
        parameters={},
        field_path=["data", "ccccc"],
        config=MagicMock(),
        field_path_pagination=["data", "bbbb"],
        field_path_incremental=["data", "boards", "*"],
    )
    records = extractor.extract_records(response)

    # Assertions
    assert records == [{"id": 1, "column_values": [{"id": 11, "text": "Hola amigo!", "display_value": "Hola amigo!"}]}]
