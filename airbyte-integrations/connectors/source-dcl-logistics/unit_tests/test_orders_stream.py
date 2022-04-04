#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest
from source_dcl_logistics.models.order import Order
from source_dcl_logistics.source import Orders


@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(Orders, "path", "v0/example_endpoint")
    mocker.patch.object(Orders, "primary_key", "test_primary_key")
    mocker.patch.object(Orders, "__abstractmethods__", set())


def test_request_params(patch_base_class):
    stream = Orders()
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": {"page": 1}}
    expected_params = {"extended_date": True, "page": 1, "page_size": 100}
    assert stream.request_params(**inputs) == expected_params


def test_parse_response(patch_base_class):
    fake_date_pdt_str = "2014-11-25T09:01:28-08:00"
    fake_date = datetime.strptime(fake_date_pdt_str, "%Y-%m-%dT%H:%M:%S%z")

    stream = Orders()

    fake_order = Order(
        account_number="FAKE",
        order_number="FAKE",
        item_number="FAKE",
        serial_number="FAKE",
        updated_at=fake_date.astimezone(timezone.utc),
    )

    fake_order_json = {
        "account_number": fake_order.account_number,
        "order_number": fake_order.order_number,
        "shipments": [
            {
                "shipping_address": {},
                "packages": [
                    {
                        "shipped_items": [
                            {
                                "item_number": fake_order.item_number,
                                "quantity": fake_order.quantity,
                                "serial_numbers": [fake_order.serial_number],
                            }
                        ]
                    }
                ],
            }
        ],
        "modified_at": fake_date_pdt_str,
    }
    fake_json_response = {"orders": [fake_order_json]}
    inputs = {"response": MagicMock(json=MagicMock(return_value=fake_json_response))}
    assert next(stream.parse_response(**inputs)) == fake_order.__dict__


def test_has_more_pages(patch_base_class):
    stream = Orders()
    fake_json_response = {"orders": None}
    inputs = {"response": MagicMock(json=MagicMock(return_value=fake_json_response))}
    list(stream.parse_response(**inputs))
    assert not stream.has_more_pages
