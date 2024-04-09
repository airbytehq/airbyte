# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import pytest
from source_shopify.shopify_graphql.graphql import get_query_products


@pytest.mark.parametrize(
    "page_size, filter_value, next_page_token, expected_query",
    [
        (100, None, None, 'query {\n  products(first: 100, query: null, after: null) {\n    nodes {\n      id\n      title\n      updatedAt\n      createdAt\n      publishedAt\n      status\n      vendor\n      productType\n      tags\n      options {\n        id\n        name\n        position\n        values\n      }\n      handle\n      description\n      tracksInventory\n      totalInventory\n      totalVariants\n      onlineStoreUrl\n      onlineStorePreviewUrl\n      descriptionHtml\n      isGiftCard\n      legacyResourceId\n      mediaCount\n    }\n    pageInfo {\n      hasNextPage\n      endCursor\n    }\n  }\n}'),
        (200, "2027-07-11T13:07:45-07:00", None, 'query {\n  products(first: 200, query: "updated_at:>\'2027-07-11T13:07:45-07:00\'", after: null) {\n    nodes {\n      id\n      title\n      updatedAt\n      createdAt\n      publishedAt\n      status\n      vendor\n      productType\n      tags\n      options {\n        id\n        name\n        position\n        values\n      }\n      handle\n      description\n      tracksInventory\n      totalInventory\n      totalVariants\n      onlineStoreUrl\n      onlineStorePreviewUrl\n      descriptionHtml\n      isGiftCard\n      legacyResourceId\n      mediaCount\n    }\n    pageInfo {\n      hasNextPage\n      endCursor\n    }\n  }\n}'),
        (250, "2027-07-11T13:07:45-07:00", "end_cursor_value", 'query {\n  products(first: 250, query: "updated_at:>\'2027-07-11T13:07:45-07:00\'", after: "end_cursor_value") {\n    nodes {\n      id\n      title\n      updatedAt\n      createdAt\n      publishedAt\n      status\n      vendor\n      productType\n      tags\n      options {\n        id\n        name\n        position\n        values\n      }\n      handle\n      description\n      tracksInventory\n      totalInventory\n      totalVariants\n      onlineStoreUrl\n      onlineStorePreviewUrl\n      descriptionHtml\n      isGiftCard\n      legacyResourceId\n      mediaCount\n    }\n    pageInfo {\n      hasNextPage\n      endCursor\n    }\n  }\n}'),
    ],
)
def test_get_query_products(page_size, filter_value, next_page_token, expected_query):
    assert get_query_products(page_size, 'updatedAt', filter_value, next_page_token) == expected_query
