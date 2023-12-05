#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import pytest
from graphql_query import Argument, Field, Operation, Query
from source_shopify.shopify_graphql.bulk.query import GraphQlQueryBuilder, Metafields, ShopifyBulkTemplates


def test_query_status():
    expected = """query {
                    node(id: "gid://shopify/BulkOperation/4047052112061") {
                        ... on BulkOperation {
                            id
                            status
                            errorCode
                            objectCount
                            fileSize
                            url
                            partialDataUrl
                        }
                    }
                }"""
    
    input_job_id = "gid://shopify/BulkOperation/4047052112061"
    template = ShopifyBulkTemplates.status(input_job_id)
    assert repr(template) == repr(expected)
    
    
def test_bulk_query_prepare():
    expected = '''mutation {
                bulkOperationRunQuery(
                    query: """
                    {some_query}
                    """
                ) {
                    bulkOperation {
                        id
                        status
                    }
                    userErrors {
                        field
                        message
                    }
                }
            }'''
    
    input_query_from_slice = "{some_query}"
    template = ShopifyBulkTemplates.prepare(input_query_from_slice)
    assert repr(template) == repr(expected)
    

def test_base_get_edge_node():
    """
    Expected result rendered: (var = expected)
    '''
        test_root {
            edges {
                node {
                    id
                    test1
                    test2
                }
            }
        }
    '''
    """
    builder = GraphQlQueryBuilder()
    expected = Field(name='test_root', fields=[Field(name='edges', fields=[Field(name='node', fields=['id', 'test1', 'test2'])])])
    edge_node = builder.get_edge_node(name="test_root", fields=["id", "test1", "test2"])
    assert expected.render() == edge_node.render()
    

@pytest.mark.parametrize(
    "query_path, sub_edge_name, sub_edge_fields, filter_query, sort_key, expected",
    [
        (
            "test_root", 
            "sub_entity", 
            ["test_field1", "test_field2"], 
            "updated_at:>'2023-01-01' AND updated_at:<='2023-01-02'", 
            "UPDATED_AT", 
            Query(
                name='test_root', 
                arguments=[
                    Argument(name="query", value=f"\"updated_at:>'2023-01-01' AND updated_at:<='2023-01-02'\""),
                    Argument(name="sortKey", value="UPDATED_AT"),    
                ], 
                fields=[Field(name='edges', fields=[Field(name='node', fields=['id',Field(name="sub_entity", fields=[Field(name="edges", fields=[Field(name="node", fields=["test_field1", "test_field2"])])])])])]
            )
        )
    ],
    ids=["simple query with filter and sort"]
)
def test_base_build_query(query_path, sub_edge_name, sub_edge_fields, filter_query, sort_key, expected):
    """
    Expected result rendered:
    '''
        test_root(
            query: "updated_at:>'2023-01-01' AND updated_at:<='2023-01-02'"
            sortKey: UPDATED_AT
            ) {
                edges {
                    node {
                    id
                    sub_entity {
                        edges {
                            node {
                                test_field1
                                test_field2
                            }
                        }
                    }
                }
            }
    '''
    """
    builder = GraphQlQueryBuilder()
    sub_edge_fields = builder.get_edge_node(name=sub_edge_name, fields=sub_edge_fields)
    built_query = builder.build_query(query_path, sub_edge_fields, filter_query, sort_key)
    assert expected.render() == built_query.render()


@pytest.mark.parametrize(
    "query_path, filter_field, start, end, sot_key, expected",
    [
        (
            "test_root", 
            "updated_at", 
            "2023-01-01",
            "2023-01-02", 
            "UPDATED_AT",
            Operation(
                type="",
                queries=[
                    Query(
                        name='test_root', 
                        arguments=[
                            Argument(name="query", value=f"\"updated_at:>='2023-01-01' AND updated_at:<='2023-01-02'\""),
                            Argument(name="sortKey", value="UPDATED_AT"),    
                        ], 
                        fields=[Field(name='edges', fields=[Field(name='node', fields=['id',Field(name="metafields", fields=[Field(name="edges", fields=[Field(name="node", fields=["id", "namespace", "value", "key", "description", "createdAt", "updatedAt", "type"])])])])])]
                    )
                ]
            ),
        ),
        (
            ["test_root"], 
            "updated_at", 
            "2023-01-01",
            "2023-01-02", 
            "UPDATED_AT",
            Operation(
                type="",
                queries=[
                    Query(
                        name='test_root', 
                        arguments=[
                            Argument(name="query", value=f"\"updated_at:>='2023-01-01' AND updated_at:<='2023-01-02'\""),
                            Argument(name="sortKey", value="UPDATED_AT"),    
                        ], 
                        fields=[Field(name='edges', fields=[Field(name='node', fields=['id',Field(name="metafields", fields=[Field(name="edges", fields=[Field(name="node", fields=["id", "namespace", "value", "key", "description", "createdAt", "updatedAt", "type"])])])])])]
                    )
                ]
            ),
        ),
        (
            ["test_root", "sub_entity"], 
            "updated_at", 
            "2023-01-01",
            "2023-01-02", 
            "UPDATED_AT",
            Operation(
                type="",
                queries=[
                    Query(
                        name='test_root', 
                        arguments=[
                            Argument(name="query", value=f"\"updated_at:>='2023-01-01' AND updated_at:<='2023-01-02'\""),
                            Argument(name="sortKey", value="UPDATED_AT"),    
                        ], 
                        fields=[Field(name='edges', fields=[Field(name='node', fields=['id',Field(name="sub_entity", fields=[Field(name="edges", fields=[Field(name="node", fields=["id", Field(name="metafields", fields=[Field(name="edges", fields=[Field(name="node", fields=["id", "namespace", "value", "key", "description", "createdAt", "updatedAt", "type"])])])])])])])])]
                    )
                ]
            ),
        ),
        (
            ["test_root", "1st_element", "2nd_element"], 
            "updated_at", 
            "2023-01-01",
            "2023-01-02", 
            "UPDATED_AT",
            Operation(
                type="",
                queries=[
                    Query(
                        name='test_root', 
                        arguments=[
                            Argument(name="query", value=f"\"updated_at:>='2023-01-01' AND updated_at:<='2023-01-02'\""),
                            Argument(name="sortKey", value="UPDATED_AT"),    
                        ], 
                        fields=[Field(name='edges', fields=[Field(name='node', fields=['id',Field(name="1st_element", fields=[Field(name="edges", fields=[Field(name="node", fields=["id", Field(name="2nd_element", fields=[Field(name="edges", fields=[Field(name="node", fields=["id", Field(name="metafields", fields=[Field(name="edges", fields=[Field(name="node", fields=["id", "namespace", "value", "key", "description", "createdAt", "updatedAt", "type"])])])])])])])])])])])]
                    )
                ]
            ),
        ),
    ],
    ids=[
        "query with 1 query_path(str), filter, sort",
        "query with 1 query_path(List[1]), filter, sort",
        "query with composite quey_path(List[2]), filter, sort",
        "query with composite query_path(List[3]), filter, sort",
    ]
)
def test_metafield_bulk_query(query_path, filter_field, start, end, sot_key, expected):
    assert Metafields(query_path, filter_field, start, end, sot_key).query == expected.render()