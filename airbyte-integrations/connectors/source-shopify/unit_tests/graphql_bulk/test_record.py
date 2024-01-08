# Copyright (c) 2023 Airbyte, Inc., all rights reserved.


import pytest
from source_shopify.shopify_graphql.bulk.query import ShopifyBulkQuery
from source_shopify.shopify_graphql.bulk.record import ShopifyBulkRecord


@pytest.mark.parametrize(
    "record, expected",
    [
        (
            {"id": "gid://shopify/Order/19435458986123"},
            {'id': 19435458986123, 'admin_graphql_api_id': 'gid://shopify/Order/19435458986123'},
        ),
    ],
)
def test_record_resolve_id(record, expected):
    bulk_query = ShopifyBulkQuery()
    assert ShopifyBulkRecord(bulk_query).record_resolve_id(record) == expected


@pytest.mark.parametrize(
    "record, expected",
    [
        (
            {
                "id": "gid://shopify/Metafield/123", 
                "__parentId": 'gid://shopify/Order/102030',
            },
            {
                "id": 123, 
                'admin_graphql_api_id': 'gid://shopify/Metafield/123', 
                "__parentId": 'gid://shopify/Order/102030',
            },
        )
    ],
) 
def test_record_resolver(record, expected):
    bulk_query = ShopifyBulkQuery()
    record_instance = ShopifyBulkRecord(bulk_query)
    assert record_instance.record_resolve_id(record) == expected