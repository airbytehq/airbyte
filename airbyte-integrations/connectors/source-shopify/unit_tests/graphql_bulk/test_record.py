# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from typing import Any, Iterable, Mapping

import pytest
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
    assert ShopifyBulkRecord.record_resolve_id(record) == expected

 
@pytest.mark.parametrize(
    "record, identifier, expected",
    [
        (
            {
                "id": 123, 
                "__parentId": "gid://shopify/Order/102030",
                "admin_graphql_api_id": "gid://shopify/Metafield/123",
            }, 
            "Metafield", 
            {
                'id': 123,
                '__parentId': 'gid://shopify/Order/102030',
                'admin_graphql_api_id': 'gid://shopify/Metafield/123',
            }
        ),
        (
            {
                "id": 123, "__parentId": "gid://shopify/Order/102030",
            }, 
            "Metafield", 
            None,
        ),
        (
            {
                "id": 123, "__parentId": "gid://shopify/Order/102030",
            }, 
            None, 
            {
                "id": 123, "__parentId": "gid://shopify/Order/102030",
            },
        )
    ],
    ids=[
        "when identifier is set, record contains substream",
        "when identifier is set, but record doesn't suit",
        "when no identifier is set, emit substream record as is",
    ]
)  
def test_resolve_substream(record, identifier, expected):
    assert ShopifyBulkRecord.resolve_substream(record, identifier) == expected
    

@pytest.mark.parametrize(
    "record, substream, identifier, use_custom_tranform, expected",
    [
        (
            {
                "id": "gid://shopify/Metafield/123", 
                "__parentId": 'gid://shopify/Order/102030',
            },
            True,
            "Metafield",
            True,
            {
                "id": 123, 
                'admin_graphql_api_id': 'gid://shopify/Metafield/123', 
                "__parentId": 'gid://shopify/Order/102030',
                'new_field': 'new_value',
            },
        ),
        (
            {
                "id": "gid://shopify/Metafield/123", 
                "__parentId": 'gid://shopify/Order/102030',
            },
            True,
            "Metafield",
            None,
            {
                "id": 123, 
                'admin_graphql_api_id': 'gid://shopify/Metafield/123', 
                "__parentId": 'gid://shopify/Order/102030',
            },
        ),
        (
            {
                "id": "gid://shopify/Record/123", 
                "__parentId": 'gid://shopify/Record/102030',
            },
            None,
            None,
            True,
            {
                'id': 123, 
                '__parentId': 'gid://shopify/Record/102030', 
                'admin_graphql_api_id': 'gid://shopify/Record/123', 
                'new_field': 'new_value',
            },
        ),
        (
            {
                "id": "gid://shopify/Record/123", 
                "__parentId": 'gid://shopify/Record/102030',
            },
            None,
            None,
            None,
            {
                'id': 123, 
                '__parentId': 'gid://shopify/Record/102030', 
                'admin_graphql_api_id': 'gid://shopify/Record/123',
            },
        ),
    ],
    ids=[
        "substream record with custom_transsform",
        "substream record with no custom_trransform",
        "record with custom_transform",
        "record with no custom_transform",
    ]
) 
def test_record_resolver(record, substream, identifier, use_custom_tranform, expected):
    
    record_instance = ShopifyBulkRecord()
    
    def custom_transform(record) -> Iterable[Mapping[str, Any]]:
        record["new_field"] = "new_value"
        yield record
    
    if use_custom_tranform:
        assert list(record_instance.record_resolver(record, substream, identifier, custom_transform)) == [expected]
    else:
        assert list(record_instance.record_resolver(record, substream, identifier)) == [expected]