# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
from __future__ import annotations

from typing import Optional, Mapping, Any

import pytest
import requests_mock
from freezegun import freeze_time

from airbyte_cdk.test.utils.assertions import assert_good_read
from airbyte_cdk.test.utils.data import get_json_contents
from airbyte_cdk.test.utils.reading import read_records
from airbyte_protocol.models import SyncMode

from .common import common_params, config, endpoint_url, source


def modified_after() -> str:
    return "2017-01-01T00:00:00"


def modified_before() -> str:
    return "2017-01-30T23:59:59"


def date_range() -> str:
    # Create and encode date range
    return f"modified_after={modified_after()}&modified_before={modified_before()}".replace(":", "%3A")


def build_url(stream_name: str, date_filterable: bool = True, custom_resource_path: Optional[str] = None) -> str:
    if date_filterable:
        return f"{endpoint_url(stream_name, custom_resource_path)}?{common_params()}&{date_range()}"
    return f"{endpoint_url(stream_name, custom_resource_path)}?{common_params()}"


def simple_endpoint_test_configuration() -> list[tuple[str, Optional[str], int, bool, Optional[str]]]:
    return


@freeze_time(modified_before())
@requests_mock.Mocker(kw="mock")
@pytest.mark.parametrize(
    "stream_name, num_records, date_filterable, custom_resource_path, custom_json_response_file",
    [
        ("customers", 2, False, None,  None),
        ("coupons", 2, True, None,  None),
        ("orders", 2, True, None,  None),
        ("payment_gateways", 4, False, None, None),
        ("product_attributes", 2, False, "products/attributes", None),
        ("product_categories", 7, False, "products/categories", None),
        ("product_reviews", 2, False, "products/reviews", None),
        ("products", 2, False, None, None),
        ("product_shipping_classes", 2, False, "products/shipping_classes", None),
        ("product_tags", 2, False, "products/tags", None),
        ("shipping_methods", 3, False, None, None),
        ("shipping_zones", 2, False, "shipping/zones", None),
        ("system_status_tools", 9, False, "system_status/tools", None),
    ]
)
def test_read_simple_endpoints_successfully(stream_name, num_records, date_filterable, custom_resource_path, custom_json_response_file,
                                            **kwargs) -> None:
    """Test basic read for  all streams that don't have parent streams."""

    # Register mock response
    kwargs["mock"].get(
        build_url(stream_name, date_filterable, custom_resource_path),
        text=get_json_contents(custom_json_response_file or f"{stream_name}.json", __file__)
    )

    # Read records
    output = read_records(source(), config(), stream_name, SyncMode.full_refresh)

    # Check read was successful
    assert_good_read(output, num_records)
