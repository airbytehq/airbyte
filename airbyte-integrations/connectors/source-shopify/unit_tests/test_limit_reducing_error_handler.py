# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import pytest
import requests
from source_shopify.streams.streams import OrderRefunds, Orders
from source_shopify.utils import LimitReducingErrorHandler, ShopifyNonRetryableErrors
from airbyte_cdk.sources.streams.http.error_handlers import HttpStatusErrorHandler
from airbyte_cdk.sources.streams.http.error_handlers.default_error_mapping import DEFAULT_ERROR_MAPPING

# Mock data for Orders stream with pagination via Link headers
ORDERS_PAGE_1 = {"orders": [{"id": i, "name": f"Order {i}"} for i in range(1, 126)]}  # 125 orders
ORDERS_PAGE_2 = {"orders": [{"id": i, "name": f"Order {i}"} for i in range(126, 251)]}  # 125 orders
ORDERS_PAGE_3 = {"orders": [{"id": i, "name": f"Order {i}"} for i in range(251, 376)]}  # 125 orders

# Mock data for Orders with nested refunds and pagination via Link headers
ORDERS_WITH_REFUNDS_PAGE_1 = {
    "orders": [
        {"id": i, "name": f"Order {i}", "refunds": [{"id": i * 10, "created_at": "2023-01-01T00:00:00Z"}]}
        for i in range(1, 126)  # 125 orders, each with 1 refund
    ]
}
ORDERS_WITH_REFUNDS_PAGE_2 = {
    "orders": [
        {"id": i, "name": f"Order {i}", "refunds": [{"id": i * 10, "created_at": "2023-01-02T00:00:00Z"}]}
        for i in range(126, 251)  # 125 orders, each with 1 refund
    ]
}

class TestOrdersLimitReducingErrorHandler:
    def test_orders_stream_500_error_handling(self, requests_mock):
        # Mock the events endpoint to prevent NoMockAddress error
        requests_mock.get(
            "https://test-shop.myshopify.com/admin/api/2025-01/events.json?filter=Order&verb=destroy",
            [{"status_code": 200, "json": {"events": []}}],
        )
        # Simulate initial URL with 500 errors, then success with pagination
        requests_mock.get(
            "https://test-shop.myshopify.com/admin/api/2025-01/orders.json?limit=250&status=any",
            [
                {"status_code": 500},  # Initial request fails
                {"status_code": 500},  # Retry with 250 fails again
                {
                    "status_code": 200,
                    "json": ORDERS_PAGE_1,
                    "headers": {
                        "Link": '<https://test-shop.myshopify.com/admin/api/2025-01/orders.json?limit=250&page_info=page1>; rel="next"'
                    },
                },
            ],
        )
        # Response for reduced limit
        requests_mock.get(
            "https://test-shop.myshopify.com/admin/api/2025-01/orders.json?limit=125&status=any",
            [
                {
                    "status_code": 200,
                    "json": ORDERS_PAGE_1,
                    "headers": {
                        "Link": '<https://test-shop.myshopify.com/admin/api/2025-01/orders.json?limit=125&page_info=page1>; rel="next"'
                    },
                }
            ],
        )
        # Paginated responses
        requests_mock.get(
            "https://test-shop.myshopify.com/admin/api/2025-01/orders.json?limit=250&page_info=page1",
            [
                {
                    "status_code": 200,
                    "json": ORDERS_PAGE_2,
                    "headers": {
                        "Link": '<https://test-shop.myshopify.com/admin/api/2025-01/orders.json?limit=250&page_info=page2>; rel="next"'
                    },
                }
            ],
        )
        requests_mock.get(
            "https://test-shop.myshopify.com/admin/api/2025-01/orders.json?limit=250&page_info=page2",
            [{"status_code": 200, "json": ORDERS_PAGE_3, "headers": {}}],  # No next page
        )

        # Configure the stream
        config = {"shop": "test-shop", "authenticator": None}
        stream = Orders(config)

        # Mock the error handler with correct parameters
        stream.get_error_handler = lambda: LimitReducingErrorHandler(
            logger=stream.logger,
            max_retries=5,
            error_mapping=DEFAULT_ERROR_MAPPING | ShopifyNonRetryableErrors(stream.name),
            initial_limit=stream.limit
        )

        # Read records
        records = list(stream.read_records(sync_mode="full_refresh"))
        assert len(records) == 375
        assert records[0]["id"] == 1
        assert records[-1]["id"] == 375

class TestOrderRefundsLimitReducingErrorHandler:
    def test_order_refunds_stream_500_error_handling(self, requests_mock):
        # Mock the events endpoint to prevent NoMockAddress error
        requests_mock.get(
            "https://test-shop.myshopify.com/admin/api/2025-01/events.json?filter=Order&verb=destroy",
            [{"status_code": 200, "json": {"events": []}}],
        )
        # Simulate initial URL with 500 error, then success with pagination
        requests_mock.get(
            "https://test-shop.myshopify.com/admin/api/2025-01/orders.json?limit=250&status=any",
            [
                {"status_code": 500},  # Initial request fails
                {
                    "status_code": 200,
                    "json": ORDERS_WITH_REFUNDS_PAGE_1,
                    "headers": {
                        "Link": '<https://test-shop.myshopify.com/admin/api/2025-01/orders.json?limit=250&page_info=page1>; rel="next"'
                    },
                },
            ],
        )
        # Response for reduced limit
        requests_mock.get(
            "https://test-shop.myshopify.com/admin/api/2025-01/orders.json?limit=125&status=any",
            [
                {
                    "status_code": 200,
                    "json": ORDERS_WITH_REFUNDS_PAGE_1,
                    "headers": {
                        "Link": '<https://test-shop.myshopify.com/admin/api/2025-01/orders.json?limit=125&page_info=page1>; rel="next"'
                    },
                }
            ],
        )
        # Paginated response
        requests_mock.get(
            "https://test-shop.myshopify.com/admin/api/2025-01/orders.json?limit=250&page_info=page1",
            [{"status_code": 200, "json": ORDERS_WITH_REFUNDS_PAGE_2, "headers": {}}],  # No next page
        )

        # Configure the stream
        config = {"shop": "test-shop", "authenticator": None}
        parent_stream = Orders(config)
        stream = OrderRefunds(config)

        # Mock the error handler for the parent stream with correct parameters
        parent_stream.get_error_handler = lambda: LimitReducingErrorHandler(
            logger=parent_stream.logger,
            max_retries=5,
            error_mapping=DEFAULT_ERROR_MAPPING | ShopifyNonRetryableErrors(parent_stream.name),
            initial_limit=parent_stream.limit
        )

        # Read records
        records = []
        for slice_ in stream.stream_slices(sync_mode="full_refresh"):
            records.extend(list(stream.read_records(sync_mode="full_refresh", stream_slice=slice_)))

        # Assertions
        assert len(records) == 250
        assert records[0]["id"] == 10
        assert records[-1]["id"] == 2500