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
        ( {"id": 123}, {'id': 123} ),
    ],
)
def test_record_resolve_id(record, expected) -> None:
    bulk_query = ShopifyBulkQuery(shop_id=0)
    assert ShopifyBulkRecord(bulk_query).record_resolve_id(record) == expected


@pytest.mark.parametrize(
    "record, types, expected",
    [
        ({"__typename": "Order", "id": "gid://shopify/Order/19435458986123"}, ["Test", "Order"], True),
        ({"__typename": "Test", "id": "gid://shopify/Order/19435458986123"}, "Other", False),
        ({}, "Other", False),
    ],
)
def test_check_record_type(record, types, expected) -> None:
    query = ShopifyBulkQuery(shop_id=0)
    assert ShopifyBulkRecord(query).check_type(record, types) == expected


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
def test_record_resolver(record, expected) -> None:
    bulk_query = ShopifyBulkQuery(shop_id=0)
    record_instance = ShopifyBulkRecord(bulk_query)
    assert record_instance.record_resolve_id(record) == expected