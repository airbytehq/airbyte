#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import pytest
from graphql_query import Argument, Field, InlineFragment, Operation, Query
from source_shopify.shopify_graphql.bulk.query import (
    InventoryLevel,
    MetafieldCustomer,
    MetafieldProductImage,
    ShopifyBulkQuery,
    ShopifyBulkTemplates,
)
from source_shopify.streams.streams import Customers, Products


def test_query_status() -> None:
    expected = """query {
                    node(id: "gid://shopify/BulkOperation/4047052112061") {
                        ... on BulkOperation {
                            id
                            status
                            errorCode
                            createdAt
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
    
    
def test_bulk_query_prepare() -> None:
    expected = '''mutation {
                bulkOperationRunQuery(
                    query: """
                    {some_query}
                    """
                ) {
                    bulkOperation {
                        id
                        status
                        createdAt
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
    
    
def test_bulk_query_cancel() -> None:
    expected = '''mutation {
                bulkOperationCancel(id: "gid://shopify/BulkOperation/4047052112061") {
                    bulkOperation {
                        id
                        status
                        createdAt
                    }
                    userErrors {
                        field
                        message
                    }
                }
            }'''
    
    input_job_id = "gid://shopify/BulkOperation/4047052112061"
    template = ShopifyBulkTemplates.cancel(input_job_id)
    assert repr(template) == repr(expected)
    

@pytest.mark.parametrize(
    "query_name, fields, filter_field, start, end, expected",
    [
        (
            "test_root", 
            ["test_field1", "test_field2"], 
            "updated_at",
            "2023-01-01",
            "2023-01-02", 
            Query(
                name='test_root', 
                arguments=[
                    Argument(name="query", value=f"\"updated_at:>'2023-01-01' AND updated_at:<='2023-01-02'\""), 
                ], 
                fields=[Field(name='edges', fields=[Field(name='node', fields=["test_field1", "test_field2"])])]
            )
        )
    ],
    ids=["simple query with filter and sort"]
)
def test_base_build_query(basic_config, query_name, fields, filter_field, start, end, expected) -> None:
    """
    Expected result rendered:
    '''
    {
        test_root(query: "updated_at:>'2023-01-01' AND updated_at:<='2023-01-02'") {
            edges {
                node {
                id
                test_field1
                test_field2
            }
        }
    }
    '''
    """
    
    builder = ShopifyBulkQuery(basic_config)
    filter_query = f"{filter_field}:>'{start}' AND {filter_field}:<='{end}'"
    built_query = builder.build(query_name, fields, filter_query)
    assert expected.render() == built_query.render()


@pytest.mark.parametrize(
    "query_class, filter_field, start, end, parent_stream_class, expected",
    [
        (
            MetafieldCustomer,
            "updated_at",
            "2023-01-01",
            "2023-01-02",
            Customers,
            Operation(
                type="",
                queries=[
                    Query(
                        name='customers', 
                        arguments=[
                            Argument(name="query", value=f"\"updated_at:>='2023-01-01' AND updated_at:<='2023-01-02'\""),
                            Argument(name="sortKey", value="UPDATED_AT"),    
                        ], 
                        fields=[Field(name='edges', fields=[Field(name='node', fields=['__typename', 'id', Field(name="updatedAt", alias="customers_updated_at"), Field(name="metafields", fields=[Field(name="edges", fields=[Field(name="node", fields=["__typename", "id", "namespace", "value", "key", "description", "createdAt", "updatedAt", "type"])])])])])]
                    )
                ]
            ),
        ),
        (
            MetafieldProductImage,
            "updated_at",
            "2023-01-01",
            "2023-01-02",
            Products,
            Operation(
                type="",
                queries=[
                    Query(
                        name="products",
                        arguments=[
                            Argument(name="query", value=f"\"updated_at:>='2023-01-01' AND updated_at:<='2023-01-02'\""),
                            Argument(name="sortKey", value="UPDATED_AT"),
                        ],
                        fields=[
                            Field(
                                name="edges",
                                fields=[
                                    Field(
                                        name="node",
                                        fields=[
                                            "__typename",
                                            "id",
                                            Field(
                                                name="updatedAt",
                                                alias="products_updated_at",
                                            ),
                                            Field(
                                                name="media",
                                                fields=[
                                                    Field(
                                                        name="edges",
                                                        fields=[
                                                            Field(
                                                                name="node",
                                                                fields=[
                                                                    "__typename",
                                                                    "id",
                                                                    InlineFragment(
                                                                        type="MediaImage",
                                                                        fields=[
                                                                            Field(
                                                                                name="metafields",
                                                                                fields=[
                                                                                    Field(
                                                                                        name="edges",
                                                                                        fields=[
                                                                                            Field(
                                                                                                name="node",
                                                                                                fields=[
                                                                                                    "__typename",
                                                                                                    "id",
                                                                                                    "namespace",
                                                                                                    "value",
                                                                                                    "key",
                                                                                                    "description",
                                                                                                    "createdAt",
                                                                                                    "updatedAt",
                                                                                                    "type",
                                                                                                ]
                                                                                            )
                                                                                        ]
                                                                                    )
                                                                                ]
                                                                            )
                                                                        ]
                                                                    )
                                                                ]
                                                            )
                                                        ]
                                                    )
                                                ]
                                            )
                                        ]
                                    )
                                ]
                            )
                        ]
                    )
                ]
            )
        ),
        (
            InventoryLevel,
            "updated_at",
            "2023-01-01",
            "2023-01-02",
            None,
            Operation(
                type="",
                queries=[
                    Query(
                        name='locations',
                        arguments=[
                            Argument(name="includeLegacy", value="true"),
                            Argument(name="includeInactive", value="true"),
                        ], 
                        fields=[
                            Field(
                                name='edges', 
                                fields=[
                                    Field(
                                        name='node', 
                                        fields=[
                                            '__typename',
                                            'id',
                                            Field(
                                                name="inventoryLevels", 
                                                arguments=[
                                                    Argument(name="query", value=f"\"updated_at:>='2023-01-01' AND updated_at:<='2023-01-02'\""),
                                                ], 
                                                fields=[
                                                    Field(
                                                        name="edges", 
                                                        fields=[
                                                            Field(
                                                                name="node", 
                                                                fields=[
                                                                  "__typename",
                                                                  "id",
                                                                  "canDeactivate",
                                                                  "createdAt",
                                                                  "deactivationAlert",
                                                                  "updatedAt",
                                                                  Field(name="item", fields=[Field(name="inventoryHistoryUrl", alias="inventory_history_url"), Field(name="id", alias="inventory_item_id"), Field(name="locationsCount", alias="locations_count", fields=["count"])]),
                                                                  Field(
                                                                        name="quantities", 
                                                                        arguments=[
                                                                            Argument(name="names", value=['"available"', '"incoming"', '"committed"', '"damaged"', '"on_hand"', '"quality_control"', '"reserved"', '"safety_stock"'])
                                                                        ], 
                                                                        fields=[
                                                                            "id",
                                                                            "name",
                                                                            "quantity",
                                                                            "updatedAt",
                                                                        ],
                                                                    )
                                                                ]
                                                            )
                                                        ]
                                                    )
                                                ]
                                            )
                                        ]
                                    )
                                ]
                            )
                        ]
                    )
                ]
            ),
        ),
    ],
    ids=[
        "MetafieldCustomers query with 1 query_path(str)",
        "MetafieldProductImages query with composite quey_path(List[2])",
        "InventoryLevel query",
    ]
)
def test_bulk_query(auth_config, query_class, filter_field, start, end, parent_stream_class, expected) -> None:
    if parent_stream_class:
        parent_stream = parent_stream_class(auth_config)
        parent_stream_cursor_alias = f"{parent_stream.name}_{parent_stream.cursor_field}"
        stream_query = query_class(auth_config, parent_stream_cursor_alias)
    else:
        stream_query = query_class(auth_config)

    assert stream_query.get(filter_field, start, end) == expected.render()