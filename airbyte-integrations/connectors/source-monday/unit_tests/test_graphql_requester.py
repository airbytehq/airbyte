#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import pytest
from airbyte_cdk.sources.declarative.requesters.requester import HttpMethod
from source_monday import MondayGraphqlRequester

nested_object_schema = {
    "root": {
        "type": ["null", "array"],
        "properties": {
            "nested": {
                "type": ["null", "object"],
                "properties": {
                    "nested_of_nested": {"type": ["null", "string"]}
                }
            }
        }
    },
    "sibling": {"type": ["null", "string"]}
}

nested_array_schema = {
    "root": {
        "type": ["null", "array"],
        "items": {
            "type": ["null", "array"],
            "properties": {
                "nested": {
                    "type": ["null", "object"],
                    "properties": {
                        "nested_of_nested": {"type": ["null", "string"]}
                    }
                }
            }
        }
    },
    "sibling": {"type": ["null", "string"]}
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
            id="test_get_request_params_produces_graphql_query_for_object_items"
        ),
        pytest.param(
            nested_array_schema,
            "test_stream",
            {},
            {"query": "query{test_stream(limit:100,page:2){root{nested{nested_of_nested}},sibling}}"},
            {"next_page_token": 2},
            id="test_get_request_params_produces_graphql_query_for_array_items"
        ),
        pytest.param(
            nested_array_schema,
            "items",
            {},
            {"query": "query{boards(limit:100,page:2){items(limit:100,page:1){root{nested{nested_of_nested}},sibling}}}"},
            {"next_page_token": (2, 1)},
            id="test_get_request_params_produces_graphql_query_for_items_stream"
        ),
        pytest.param(
            nested_array_schema,
            "teams",
            {"teams_limit": 100},
            {'query': 'query{teams(limit:100,page:2){id,name,picture_url,users(limit:100){id}}}'},
            {"next_page_token": 2},
            id="test_get_request_params_produces_graphql_query_for_teams_optimized_stream"
        ),
        pytest.param(
            nested_array_schema,
            "teams",
            {},
            {'query': 'query{teams(limit:100,page:2){root{nested{nested_of_nested}},sibling}}'},
            {"next_page_token": 2},
            id="test_get_request_params_produces_graphql_query_for_teams_stream"
        )
    ]
)
def test_get_request_params(mocker, input_schema, graphql_query, stream_name, config, next_page_token):
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
        config=config
    )
    assert requester.get_request_params(
        stream_state={},
        stream_slice={},
        next_page_token=next_page_token
    ) == graphql_query
