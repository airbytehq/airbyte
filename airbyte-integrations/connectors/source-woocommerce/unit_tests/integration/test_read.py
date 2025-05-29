# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
from __future__ import annotations

import pytest
import requests_mock
from airbyte_cdk.test.utils.http_mocking import register_mock_responses
from airbyte_cdk.test.utils.reading import read_records
from airbyte_protocol.models import SyncMode
from freezegun import freeze_time

from .common import config, source
from .conftest import (
    coupons_http_calls,
    customers_http_calls,
    order_notes_http_calls,
    orders_empty_last_page,
    orders_http_calls,
    payment_gateways_http_calls,
    product_attribute_terms_http_calls,
    product_attributes_http_calls,
    product_categories_http_calls,
    product_reviews_http_calls,
    product_shipping_classes_http_calls,
    product_tags_http_calls,
    product_variations_http_calls,
    products_http_calls,
    refunds_http_calls,
    shipping_methods_http_calls,
    shipping_zone_locations_http_calls,
    shipping_zone_methods_http_calls,
    shipping_zones_http_calls,
    system_status_tools_http_calls,
    tax_classes_http_calls,
    tax_rates_http_calls,
)


def modified_before() -> str:
    return "2017-01-29T00:00:00"


@freeze_time(modified_before())
@pytest.mark.parametrize(
    "stream_name, num_records, http_calls",
    [
        # Streams without parent streams
        ("customers", 2, customers_http_calls()),
        ("coupons", 2, coupons_http_calls()),
        ("orders", 2, orders_http_calls()),
        ("payment_gateways", 4, payment_gateways_http_calls()),
        ("product_attributes", 2, product_attributes_http_calls()),
        ("product_categories", 7, product_categories_http_calls()),
        ("product_reviews", 2, product_reviews_http_calls()),
        ("products", 2, products_http_calls()),
        ("product_shipping_classes", 2, product_shipping_classes_http_calls()),
        ("product_tags", 2, product_tags_http_calls()),
        ("shipping_methods", 3, shipping_methods_http_calls()),
        ("shipping_zones", 2, shipping_zones_http_calls()),
        ("system_status_tools", 9, system_status_tools_http_calls()),
        ("tax_classes", 3, tax_classes_http_calls()),
        ("tax_rates", 10, tax_rates_http_calls()),
        # Streams with parent streams
        ("order_notes", 6, order_notes_http_calls()),
        ("product_attribute_terms", 14, product_attribute_terms_http_calls()),
        ("product_variations", 4, product_variations_http_calls()),
        ("refunds", 4, refunds_http_calls()),
        ("shipping_zone_locations", 2, shipping_zone_locations_http_calls()),
        ("shipping_zone_methods", 4, shipping_zone_methods_http_calls()),
    ]
)
def test_read_simple_endpoints_successfully(stream_name, num_records, http_calls) -> None:
    """Test basic read for  all streams that don't have parent streams."""

    with requests_mock.Mocker() as m:
        register_mock_responses(m, http_calls)

        output = read_records(source(), config(), stream_name, SyncMode.full_refresh)

        assert len(output.records) == num_records
        assert len(output.errors) == 0
        assert output.is_not_in_logs("error|exception|fail|traceback")


@freeze_time("2017-02-10T00:00:00")
@pytest.mark.parametrize(
    "stream_name, num_records, http_calls",
    [("orders", 2, orders_empty_last_page())]
)
def test_read_with_multiple_pages_with_empty_last_page_successfully(stream_name, num_records, http_calls) -> None:
    """Test read with multiple pages and an empty page in last call."""

    with requests_mock.Mocker() as m:
        register_mock_responses(m, http_calls)

        output = read_records(source(), config(), stream_name, SyncMode.full_refresh)

        assert len(m.request_history) == len(http_calls)
        assert len(output.records) == num_records
        assert len(output.errors) == 0
        assert output.is_not_in_logs("StopIteration")
