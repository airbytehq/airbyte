# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from source_shopify.streams.streams import Customers, Products


def test_api_version_is_threaded_into_rest_and_bulk_urls(auth_config):
    rest_stream = Customers(auth_config)
    bulk_stream = Products(auth_config)

    assert rest_stream.url_base == "https://test-shop.myshopify.com/admin/api/2026-07/"
    assert bulk_stream.job_manager.base_url == "https://test-shop.myshopify.com/admin/api/2026-07/graphql.json"
