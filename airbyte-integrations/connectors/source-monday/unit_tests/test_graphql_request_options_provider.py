#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pytest
from source_monday import GraphQLRequestOptionsProvider

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
    ("input_schema", "stream_name", "config", "graphql_query"),
    [
        pytest.param(
            nested_object_schema,
            "test_stream",
            {},
            {"query": "query{test_stream(limit:100,page:2){root{nested{nested_of_nested}},sibling}}"},
            id="test_get_request_params_produces_graphql_query_for_object_items"
        ),
        pytest.param(
            nested_array_schema,
            "test_stream",
            {},
            {"query": "query{test_stream(limit:100,page:2){root{nested{nested_of_nested}},sibling}}"},
            id="test_get_request_params_produces_graphql_query_for_array_items"
        ),
        pytest.param(
            nested_array_schema,
            "items",
            {},
            {"query": "query{boards(limit:100,page:2){items(limit:100){root{nested{nested_of_nested}},sibling}}}"},
            id="test_get_request_params_produces_graphql_query_for_items_stream"
        ),
        pytest.param(
            nested_array_schema,
            "teams",
            {"teams_limit": 100},
            {'query': 'query{teams(limit:100,page:2){id,name,picture_url,users(limit:100){id}}}'},
            id="test_get_request_params_produces_graphql_query_for_teams_optimized_stream"
        ),
        pytest.param(
            nested_array_schema,
            "teams",
            {},
            {'query': 'query{teams(limit:100,page:2){root{nested{nested_of_nested}},sibling}}'},
            id="test_get_request_params_produces_graphql_query_for_teams_stream"
        )
    ]
)
def test_get_request_params(mocker, input_schema, graphql_query, stream_name, config):
    mocker.patch.object(GraphQLRequestOptionsProvider, "_get_schema_root_properties", return_value=input_schema)
    provider = GraphQLRequestOptionsProvider(
        limit="{{ options['items_per_page'] }}",
        options={"name": stream_name, "items_per_page": 100},
        config=config
    )
    assert provider.get_request_params(
        stream_state={},
        stream_slice={},
        next_page_token={"next_page_token": 2}
    ) == graphql_query
