#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import pytest

from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.requesters.requester import HttpMethod
from airbyte_cdk.sources.declarative.schema.inline_schema_loader import InlineSchemaLoader


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
            {"query": "{test_stream(limit:100,page:2){root{nested{nested_of_nested}},sibling}}"},
            {"next_page_token": 2},
            id="test_get_request_params_produces_graphql_query_for_object_items",
        ),
        pytest.param(
            nested_array_schema,
            "test_stream",
            {},
            {"query": "{test_stream(limit:100,page:2){root{nested{nested_of_nested}},sibling}}"},
            {"next_page_token": 2},
            id="test_get_request_params_produces_graphql_query_for_array_items",
        ),
        pytest.param(
            nested_array_schema,
            "items",
            {},
            {"query": '{next_items_page(limit:100,cursor:"cursor_bla"){cursor,items{root{nested{nested_of_nested}},sibling}}}'},
            {"next_page_token": (2, "cursor_bla")},
            id="test_get_request_params_produces_graphql_query_for_items_stream",
        ),
        pytest.param(
            nested_array_schema,
            "teams",
            {"teams_limit": 100},
            {"query": "{teams(limit:100,page:2){id,name,picture_url,users(limit:100){id}}}"},
            {"next_page_token": 2},
            id="test_get_request_params_produces_graphql_query_for_teams_optimized_stream",
        ),
        pytest.param(
            nested_array_schema,
            "teams",
            {},
            {"query": "{teams(limit:100,page:2){root{nested{nested_of_nested}},sibling}}"},
            {"next_page_token": 2},
            id="test_get_request_params_produces_graphql_query_for_teams_stream",
        ),
    ],
)
def test_get_request_params(components_module, input_schema, graphql_query, stream_name, config, next_page_token):
    mock_schema = {
        stream_name: {
            "properties": input_schema,
        }
    }

    requester = components_module.MondayGraphqlRequester(
        name="a name",
        url_base="https://api.monday.com/v2",
        path="a-path",
        http_method=HttpMethod.GET,
        schema_loader=InlineSchemaLoader(schema=mock_schema, parameters={}),
        request_options_provider=MagicMock(),
        authenticator=MagicMock(),
        error_handler=MagicMock(),
        limit="{{ parameters['items_per_page'] }}",
        nested_limit="{{ parameters.get('nested_items_per_page', 1) }}",
        parameters={"name": stream_name, "items_per_page": 100, "nested_items_per_page": 100},
        config=config,
    )
    assert requester.get_request_body_json(stream_state={}, stream_slice={}, next_page_token=next_page_token) == graphql_query


@pytest.fixture
def monday_requester(components_module):
    mock_schema = {
        "activity_logs": {
            "properties": {
                "updated_at_int": {"type": "integer"},
                "created_at_int": {"type": "integer"},
                "pulse_id": {"type": "integer"},
                "board_id": {"type": "integer"},
                "other_field": {"type": "string"},
                "yet_another_field": {"type": "boolean"},
            }
        }
    }
    mock_schema_loader = InlineSchemaLoader(schema=mock_schema, parameters={"name": "activity_logs"})
    return components_module.MondayGraphqlRequester(
        name="a name",
        url_base="https://api.monday.com/v2",
        path="a-path",
        config={},
        parameters={"name": "activity_logs"},
        schema_loader=mock_schema_loader,
        limit=InterpolatedString.create("100", parameters={"name": "activity_logs"}),
        nested_limit=InterpolatedString.create("100", parameters={"name": "activity_logs"}),
    )


def test_get_schema_root_properties(monday_requester):
    requester = monday_requester
    result_schema = requester._get_schema_root_properties()

    assert result_schema == {"other_field": {"type": "string"}, "yet_another_field": {"type": "boolean"}}


def test_build_activity_query(components_module, mocker, monday_requester):
    object_arguments = {"stream_slice": {"start_time": 1636738688}}
    mocker.patch.object(
        components_module.MondayGraphqlRequester, "_get_object_arguments", return_value="stream_state:{{ stream_state['updated_at_int'] }}"
    )
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
        "... on BoardRelationValue{display_value,linked_item_ids},... on DependencyValue{display_value,linked_item_ids}}}"
    )


def test_get_request_headers(monday_requester):
    headers = monday_requester.get_request_headers()

    assert headers == {"API-Version": "2026-01"}


@pytest.mark.parametrize(
    ("stream_slice", "expected_arguments"),
    [
        pytest.param(
            {"start_time": "2024-01-11T08:30:00Z", "end_time": "2024-01-15T12:00:59Z"},
            'limit:100,page:2,from_date:"2024-01-11T08:30",to_date:"2024-01-15T12:00"',
            id="dated_slice_sends_paired_minute_filters",
        ),
        pytest.param(
            {"start_time": "1970-01-01T00:00:00Z", "end_time": "2024-01-15T12:00:00Z"},
            "limit:100,page:2",
            id="epoch_slice_sends_no_filter",
        ),
        pytest.param({}, "limit:100,page:2", id="empty_slice_sends_no_filter"),
    ],
)
def test_updates_request_body_maps_slice_to_from_and_to_date(components_module, stream_slice, expected_arguments):
    requester = components_module.MondayGraphqlRequester(
        name="updates",
        url_base="https://api.monday.com/v2",
        path="",
        http_method=HttpMethod.POST,
        schema_loader=InlineSchemaLoader(schema={"updates": {"properties": {"id": {"type": ["null", "string"]}}}}, parameters={}),
        limit=InterpolatedString.create("100", parameters={}),
        nested_limit=InterpolatedString.create("100", parameters={}),
        parameters={"name": "updates"},
        config={},
    )

    request_body = requester.get_request_body_json(stream_state={}, stream_slice=stream_slice, next_page_token={"next_page_token": 2})

    assert request_body == {"query": f"{{updates({expected_arguments}){{id}}}}"}
